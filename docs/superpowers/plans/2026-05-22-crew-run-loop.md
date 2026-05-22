# Crew Run Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Crew execution loop mode where each completed round's final output becomes the selected placeholder input for the next round.

**Architecture:** Put loop mechanics in a small pure-Python module (`app/crew_run_loop.py`) and keep Streamlit-specific state, UI, result persistence, and thread control in `app/pg_crew_run.py`. The loop runner emits queue messages for round start, round success, loop completion, and loop failure; the page consumes those messages and updates `st.session_state`, console output, and saved results.

**Tech Stack:** Python 3.12, Streamlit, CrewAI, SQLite JSON entity storage through `db_utils`, `unittest`.

---

## File Structure

- Create `app/crew_run_loop.py`
  - Defines `LoopConfig`.
  - Builds per-round inputs.
  - Extracts final output from CrewAI result objects.
  - Runs sequential loop rounds and emits queue messages.
  - Has no Streamlit import.

- Create `tests/test_crew_run_loop.py`
  - Unit tests for input chaining, output extraction, failure handling, and stop behavior.

- Modify `app/pg_crew_run.py`
  - Adds loop session-state defaults.
  - Draws loop controls in the execution panel.
  - Starts either the existing single-run path or the new loop-thread path.
  - Consumes loop queue messages.
  - Saves every successful loop round as an individual `Result`.
  - Shows loop progress and round statuses.
  - Stops whole loop when the stop button is clicked.

- Modify `app/i18n/zh.json`
  - Adds Chinese labels for loop controls, validation, and round statuses.

- Modify `app/i18n/en.json`
  - Adds English labels for the same keys.

- Modify `tests/test_ui_workbench.py`
  - Source-level assertions that execution page exposes loop controls and imports the loop runner.

---

## Task 1: Pure Loop Runner

**Files:**
- Create: `app/crew_run_loop.py`
- Create: `tests/test_crew_run_loop.py`

- [ ] **Step 1: Write failing tests for loop semantics**

Create `tests/test_crew_run_loop.py` with this content:

```python
from pathlib import Path
import queue
import sys
import threading
import unittest
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))


class FakeCrew:
    def __init__(self, output):
        self.output = output

    def kickoff(self, inputs):
        return SimpleNamespace(raw=self.output(inputs), tasks_output=[])


class FakeCrewFactory:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def __call__(self):
        index = len(self.calls)
        output = self.outputs[index]

        def produce(inputs):
            self.calls.append(dict(inputs))
            return output

        return FakeCrew(produce)


class CrewRunLoopTests(unittest.TestCase):
    def test_extract_final_output_prefers_result_raw(self):
        from crew_run_loop import extract_final_output

        result = SimpleNamespace(raw=" final answer ", tasks_output=[])

        self.assertEqual(extract_final_output(result), "final answer")

    def test_build_round_inputs_replaces_only_selected_placeholder(self):
        from crew_run_loop import build_round_inputs

        inputs = build_round_inputs(
            {"requirement": "first", "style": "short"},
            target_placeholder="requirement",
            previous_output="second",
        )

        self.assertEqual(inputs, {"requirement": "second", "style": "short"})

    def test_run_crew_loop_chains_previous_output_into_next_round(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory(["round one", "round two", "round three"])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial", "style": "short"},
            config=LoopConfig(enabled=True, count=3, target_placeholder="requirement", loop_id="L_test"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        self.assertEqual(
            factory.calls,
            [
                {"requirement": "initial", "style": "short"},
                {"requirement": "round one", "style": "short"},
                {"requirement": "round two", "style": "short"},
            ],
        )
        message_types = [messages.get_nowait()["type"] for _ in range(messages.qsize())]
        self.assertEqual(
            message_types,
            [
                "loop_round_start",
                "loop_round_success",
                "loop_round_start",
                "loop_round_success",
                "loop_round_start",
                "loop_round_success",
                "loop_complete",
            ],
        )

    def test_run_crew_loop_fails_when_round_output_is_empty(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory([""])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=2, target_placeholder="requirement", loop_id="L_empty"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        messages_by_type = []
        while not messages.empty():
            messages_by_type.append(messages.get_nowait())

        self.assertEqual(messages_by_type[-1]["type"], "loop_failed")
        self.assertIn("empty final output", messages_by_type[-1]["result"])

    def test_run_crew_loop_obeys_stop_event_before_next_round(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        stop_event = threading.Event()
        factory = FakeCrewFactory(["round one", "round two"])

        original_put = messages.put

        def stop_after_first_success(message):
            original_put(message)
            if message["type"] == "loop_round_success":
                stop_event.set()

        messages.put = stop_after_first_success

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=2, target_placeholder="requirement", loop_id="L_stop"),
            message_queue=messages,
            stop_event=stop_event,
        )

        self.assertEqual(factory.calls, [{"requirement": "initial"}])
        last_message = None
        while not messages.empty():
            last_message = messages.get_nowait()
        self.assertEqual(last_message["type"], "loop_stopped")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new test and verify it fails**

Run:

```bash
.venv312/bin/python -m unittest tests/test_crew_run_loop.py -v
```

Expected result:

```text
ModuleNotFoundError: No module named 'crew_run_loop'
```

- [ ] **Step 3: Implement the loop runner**

Create `app/crew_run_loop.py` with this content:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import traceback
from typing import Any, Callable


@dataclass(frozen=True)
class LoopConfig:
    enabled: bool = False
    count: int = 1
    target_placeholder: str | None = None
    loop_id: str | None = None


def normalize_loop_count(value: int | None) -> int:
    try:
        count = int(value or 1)
    except (TypeError, ValueError):
        return 1
    return max(1, count)


def build_round_inputs(
    base_inputs: dict[str, str],
    target_placeholder: str | None,
    previous_output: str | None,
) -> dict[str, str]:
    inputs = dict(base_inputs)
    if target_placeholder and previous_output is not None:
        inputs[target_placeholder] = previous_output
    return inputs


def extract_final_output(result: Any) -> str:
    if isinstance(result, dict):
        if "result" in result:
            return extract_final_output(result["result"])
        if "raw" in result:
            return str(result["raw"] or "").strip()
        if "final_output" in result:
            return str(result["final_output"] or "").strip()

    if hasattr(result, "raw"):
        return str(getattr(result, "raw") or "").strip()

    return str(result or "").strip()


def _now() -> str:
    return datetime.now().isoformat()


def _round_message(
    message_type: str,
    loop_id: str,
    index: int,
    total: int,
    status: str,
    inputs: dict[str, str],
    output: str = "",
    error: str = "",
    result: Any = None,
    target_placeholder: str | None = None,
    previous_output: str | None = None,
) -> dict[str, Any]:
    loop_metadata = {
        "enabled": True,
        "loop_id": loop_id,
        "index": index,
        "total": total,
        "target_placeholder": target_placeholder,
        "previous_output": previous_output,
    }
    round_status = {
        "loop_id": loop_id,
        "index": index,
        "total": total,
        "status": status,
        "input": dict(inputs),
        "output": output,
        "error": error,
        "started_at": _now(),
        "finished_at": _now() if status in {"success", "failed", "stopped"} else "",
    }
    message = {
        "type": message_type,
        "loop": loop_metadata,
        "round": round_status,
    }
    if result is not None:
        message["result"] = result
    if error:
        message["result"] = error
    return message


def run_crew_loop(
    crew_factory: Callable[[], Any],
    base_inputs: dict[str, str],
    config: LoopConfig,
    message_queue: Any,
    stop_event: Any,
) -> None:
    count = normalize_loop_count(config.count)
    loop_id = config.loop_id or f"L_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    target_placeholder = config.target_placeholder
    previous_output: str | None = None
    latest_result: Any = None
    latest_message: dict[str, Any] | None = None
    current_index = 0

    try:
        if config.enabled and not target_placeholder:
            raise ValueError("loop target placeholder is required")

        for round_index in range(1, count + 1):
            current_index = round_index
            if stop_event and stop_event.is_set():
                stopped_inputs = build_round_inputs(base_inputs, target_placeholder, previous_output)
                message_queue.put(
                    _round_message(
                        "loop_stopped",
                        loop_id,
                        round_index,
                        count,
                        "stopped",
                        stopped_inputs,
                        target_placeholder=target_placeholder,
                        previous_output=previous_output,
                    )
                )
                return

            current_inputs = build_round_inputs(base_inputs, target_placeholder, previous_output)
            message_queue.put(
                _round_message(
                    "loop_round_start",
                    loop_id,
                    round_index,
                    count,
                    "running",
                    current_inputs,
                    target_placeholder=target_placeholder,
                    previous_output=previous_output,
                )
            )

            crew = crew_factory()
            result = crew.kickoff(inputs=current_inputs)
            final_output = extract_final_output(result)
            if not final_output:
                raise ValueError(f"round {round_index} produced empty final output")

            latest_result = result
            latest_message = _round_message(
                "loop_round_success",
                loop_id,
                round_index,
                count,
                "success",
                current_inputs,
                output=final_output,
                result=result,
                target_placeholder=target_placeholder,
                previous_output=previous_output,
            )
            message_queue.put(latest_message)
            previous_output = final_output

        message_queue.put(
            {
                "type": "loop_complete",
                "loop": latest_message["loop"] if latest_message else {
                    "enabled": True,
                    "loop_id": loop_id,
                    "index": count,
                    "total": count,
                    "target_placeholder": target_placeholder,
                    "previous_output": previous_output,
                },
                "round": latest_message["round"] if latest_message else {},
                "result": latest_result,
            }
        )
    except Exception as exc:
        failed_inputs = build_round_inputs(base_inputs, target_placeholder, previous_output)
        message_queue.put(
            {
                "type": "loop_failed",
                "result": f"Error running crew loop: {str(exc)}",
                "stack_trace": traceback.format_exc(),
                "loop": {
                    "enabled": True,
                    "loop_id": loop_id,
                    "index": current_index,
                    "total": count,
                    "target_placeholder": target_placeholder,
                    "previous_output": previous_output,
                },
                "round": {
                    "loop_id": loop_id,
                    "index": 0,
                    "total": count,
                    "status": "failed",
                    "input": failed_inputs,
                    "output": "",
                    "error": str(exc),
                    "started_at": _now(),
                    "finished_at": _now(),
                },
            }
        )
```

- [ ] **Step 4: Run the new loop tests**

Run:

```bash
.venv312/bin/python -m unittest tests/test_crew_run_loop.py -v
```

Expected result:

```text
Ran 5 tests

OK
```

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add app/crew_run_loop.py tests/test_crew_run_loop.py
git commit -m "Add crew run loop runner" -m "Introduce a pure-Python loop runner so previous round output can be chained into the selected Crew placeholder without coupling the loop mechanics to Streamlit state." -m "Tested: .venv312/bin/python -m unittest tests/test_crew_run_loop.py -v" -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
```

---

## Task 2: Streamlit State and Loop Controls

**Files:**
- Modify: `app/pg_crew_run.py`
- Modify: `app/i18n/zh.json`
- Modify: `app/i18n/en.json`
- Modify: `tests/test_ui_workbench.py`

- [ ] **Step 1: Write failing source-level UI tests**

Add this test method to `tests/test_ui_workbench.py` inside `WorkbenchUiTests`:

```python
    def test_crew_run_page_exposes_loop_controls(self):
        source = (ROOT / "app" / "pg_crew_run.py").read_text(encoding="utf-8")
        zh = (ROOT / "app" / "i18n" / "zh.json").read_text(encoding="utf-8")
        en = (ROOT / "app" / "i18n" / "en.json").read_text(encoding="utf-8")

        self.assertIn("from crew_run_loop import LoopConfig, run_crew_loop", source)
        self.assertIn("'loop_enabled': False", source)
        self.assertIn("'loop_count': 2", source)
        self.assertIn("'loop_target_placeholder': None", source)
        self.assertIn("def draw_loop_controls(self, selected_crew):", source)
        self.assertIn('st.checkbox(t("crew_run.loop_enabled")', source)
        self.assertIn('st.number_input(t("crew_run.loop_count")', source)
        self.assertIn('st.selectbox(t("crew_run.loop_target_placeholder")', source)
        self.assertIn('"loop_enabled": "启用 Loop"', zh)
        self.assertIn('"loop_target_placeholder": "上一轮结果注入到"', zh)
        self.assertIn('"loop_enabled": "Enable loop"', en)
        self.assertIn('"loop_target_placeholder": "Inject previous result into"', en)
```

- [ ] **Step 2: Run the UI test and verify it fails**

Run:

```bash
.venv312/bin/python -m unittest tests/test_ui_workbench.py -v
```

Expected result:

```text
FAIL: test_crew_run_page_exposes_loop_controls
```

- [ ] **Step 3: Add i18n keys**

In `app/i18n/zh.json`, extend the `crew_run` object with these keys after `console_empty`:

```json
    "console_empty": "团队开始运行后，控制台输出会显示在这里。",
    "loop_panel": "Loop 设置",
    "loop_panel_caption": "将上一轮最终输出自动作为下一轮输入。",
    "loop_enabled": "启用 Loop",
    "loop_count": "循环次数",
    "loop_target_placeholder": "上一轮结果注入到",
    "loop_no_placeholders": "当前团队没有可注入的占位符，无法启用 Loop。",
    "loop_select_placeholder": "请选择上一轮结果要注入的占位符。",
    "loop_progress": "Loop 进度",
    "loop_round_status": "第 {index}/{total} 轮：{status}",
    "loop_status_waiting": "等待中",
    "loop_status_running": "运行中",
    "loop_status_success": "成功",
    "loop_status_failed": "失败",
    "loop_status_stopped": "已停止"
```

In `app/i18n/en.json`, extend the `crew_run` object with these keys after `console_empty`:

```json
    "console_empty": "Console output will appear here after the crew starts.",
    "loop_panel": "Loop settings",
    "loop_panel_caption": "Use each round's final output as the next round's input.",
    "loop_enabled": "Enable loop",
    "loop_count": "Loop count",
    "loop_target_placeholder": "Inject previous result into",
    "loop_no_placeholders": "This crew has no injectable placeholders, so loop mode cannot be enabled.",
    "loop_select_placeholder": "Select the placeholder that receives the previous round result.",
    "loop_progress": "Loop progress",
    "loop_round_status": "Round {index}/{total}: {status}",
    "loop_status_waiting": "Waiting",
    "loop_status_running": "Running",
    "loop_status_success": "Success",
    "loop_status_failed": "Failed",
    "loop_status_stopped": "Stopped"
```

Keep valid JSON commas when editing the existing `console_empty` line.

- [ ] **Step 4: Add loop state defaults and controls**

Modify `app/pg_crew_run.py` imports:

```python
import threading
from crew_run_loop import LoopConfig, run_crew_loop
```

Keep the existing `import threading` line and add the loop import near the other local imports.

Extend `maintain_session_state()` defaults:

```python
            'loop_enabled': False,
            'loop_count': 2,
            'loop_target_placeholder': None,
            'loop_run_id': None,
            'loop_rounds': [],
            'loop_stop_event': None,
```

Add this method to `PageCrewRun` after `draw_placeholders()`:

```python
    def draw_loop_controls(self, selected_crew):
        placeholders = sorted(self.get_placeholders_from_crew(selected_crew))
        st.markdown(f"#### {t('crew_run.loop_panel')}")
        st.caption(t("crew_run.loop_panel_caption"))

        ss.loop_enabled = st.checkbox(
            t("crew_run.loop_enabled"),
            value=bool(ss.loop_enabled),
            disabled=ss.running,
            key="crew_run_loop_enabled_control",
        )

        if not ss.loop_enabled:
            return True

        if not placeholders:
            st.error(t("crew_run.loop_no_placeholders"))
            return False

        ss.loop_count = st.number_input(
            t("crew_run.loop_count"),
            min_value=2,
            max_value=20,
            value=max(2, int(ss.loop_count or 2)),
            step=1,
            disabled=ss.running,
            key="crew_run_loop_count_control",
        )

        current_target = ss.loop_target_placeholder
        index = placeholders.index(current_target) if current_target in placeholders else 0
        ss.loop_target_placeholder = st.selectbox(
            t("crew_run.loop_target_placeholder"),
            options=placeholders,
            index=index,
            disabled=ss.running,
            key="crew_run_loop_target_placeholder_control",
        )
        return bool(ss.loop_target_placeholder)
```

In `draw_crews()`, inside the right column after the validity check and before `self.control_buttons(selected_crew)`, add:

```python
                loop_config_valid = self.draw_loop_controls(selected_crew)
                self.control_buttons(selected_crew, loop_config_valid=loop_config_valid)
```

Replace the old call:

```python
                self.control_buttons(selected_crew)
```

Update the method signature:

```python
    def control_buttons(self, selected_crew, loop_config_valid=True):
```

Update the run button disabled expression:

```python
            run_clicked = st.button(
                t('crew_run.run_button'),
                disabled=not selected_crew.is_valid() or ss.running or not loop_config_valid,
                type="primary",
                use_container_width=True,
            )
```

- [ ] **Step 5: Run UI tests**

Run:

```bash
.venv312/bin/python -m unittest tests/test_ui_workbench.py -v
```

Expected result:

```text
OK
```

- [ ] **Step 6: Commit Task 2**

Run:

```bash
git add app/pg_crew_run.py app/i18n/zh.json app/i18n/en.json tests/test_ui_workbench.py
git commit -m "Add crew run loop controls" -m "Expose loop configuration in the Crew run page while keeping the controls disabled during active execution and validating placeholder availability before a loop can start." -m "Tested: .venv312/bin/python -m unittest tests/test_ui_workbench.py -v" -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
```

---

## Task 3: Thread Integration, Queue Handling, and Result Persistence

**Files:**
- Modify: `app/pg_crew_run.py`
- Create or modify: `tests/test_crew_run_page_loop.py`

- [ ] **Step 1: Write failing tests for page-level loop helpers**

Create `tests/test_crew_run_page_loop.py` with this content:

```python
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))


class FakeSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class CrewRunPageLoopTests(unittest.TestCase):
    def test_build_loop_config_uses_session_state(self):
        import pg_crew_run

        original_state = pg_crew_run.ss
        fake_state = FakeSessionState(
            loop_enabled=True,
            loop_count=4,
            loop_target_placeholder="requirement",
        )
        page = pg_crew_run.PageCrewRun.__new__(pg_crew_run.PageCrewRun)

        try:
            pg_crew_run.ss = fake_state
            config = page.build_loop_config()
        finally:
            pg_crew_run.ss = original_state

        self.assertTrue(config.enabled)
        self.assertEqual(config.count, 4)
        self.assertEqual(config.target_placeholder, "requirement")
        self.assertTrue(config.loop_id.startswith("L_"))

    def test_loop_round_success_updates_rounds_and_latest_result(self):
        import pg_crew_run

        original_state = pg_crew_run.ss
        fake_state = FakeSessionState(loop_rounds=[], result=None)
        page = pg_crew_run.PageCrewRun.__new__(pg_crew_run.PageCrewRun)
        result = SimpleNamespace(raw="round output", tasks_output=[])
        message = {
            "type": "loop_round_success",
            "loop": {"enabled": True, "loop_id": "L_1", "index": 1, "total": 2, "target_placeholder": "requirement", "previous_output": None},
            "round": {"loop_id": "L_1", "index": 1, "total": 2, "status": "success", "input": {"requirement": "initial"}, "output": "round output", "error": "", "started_at": "s", "finished_at": "f"},
            "result": result,
        }

        try:
            pg_crew_run.ss = fake_state
            page.apply_loop_queue_message(message)
        finally:
            pg_crew_run.ss = original_state

        self.assertEqual(fake_state.loop_rounds[0]["status"], "success")
        self.assertEqual(fake_state.result["result"], result)
        self.assertEqual(fake_state.result["loop"]["loop_id"], "L_1")

    def test_loop_complete_stops_running(self):
        import pg_crew_run

        original_state = pg_crew_run.ss
        fake_state = FakeSessionState(loop_rounds=[], running=True, result=None)
        page = pg_crew_run.PageCrewRun.__new__(pg_crew_run.PageCrewRun)
        result = SimpleNamespace(raw="final", tasks_output=[])

        try:
            pg_crew_run.ss = fake_state
            page.apply_loop_queue_message(
                {
                    "type": "loop_complete",
                    "loop": {"enabled": True, "loop_id": "L_1", "index": 2, "total": 2, "target_placeholder": "requirement", "previous_output": "prev"},
                    "round": {"loop_id": "L_1", "index": 2, "total": 2, "status": "success", "input": {}, "output": "final", "error": "", "started_at": "s", "finished_at": "f"},
                    "result": result,
                }
            )
        finally:
            pg_crew_run.ss = original_state

        self.assertFalse(fake_state.running)
        self.assertEqual(fake_state.result["result"], result)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the page loop tests and verify they fail**

Run:

```bash
.venv312/bin/python -m unittest tests/test_crew_run_page_loop.py -v
```

Expected result:

```text
AttributeError: 'PageCrewRun' object has no attribute 'build_loop_config'
```

- [ ] **Step 3: Add loop config and queue helper methods**

In `app/pg_crew_run.py`, add this import near local imports:

```python
from crew_run_loop import LoopConfig, run_crew_loop
```

Add these methods to `PageCrewRun` after `draw_loop_controls()`:

```python
    def build_loop_config(self):
        return LoopConfig(
            enabled=bool(ss.loop_enabled),
            count=int(ss.loop_count or 1),
            target_placeholder=ss.loop_target_placeholder if ss.loop_enabled else None,
            loop_id=f"L_{rnd_id()}",
        )

    def current_inputs(self):
        return {key.split('_', 1)[1]: value for key, value in ss.placeholders.items() if key.startswith("placeholder_")}

    def update_loop_round(self, round_status):
        if not round_status:
            return
        rounds = [round_info for round_info in ss.loop_rounds if round_info.get("index") != round_status.get("index")]
        rounds.append(round_status)
        ss.loop_rounds = sorted(rounds, key=lambda item: item.get("index", 0))

    def apply_loop_queue_message(self, message):
        message_type = message.get("type")
        if message_type in {"loop_round_start", "loop_round_success", "loop_stopped"}:
            self.update_loop_round(message.get("round"))

        if message_type == "loop_round_success":
            loop_metadata = dict(message.get("loop") or {})
            loop_metadata["round_input"] = dict((message.get("round") or {}).get("input") or {})
            ss.result = {"result": message.get("result"), "loop": loop_metadata}
            return

        if message_type == "loop_complete":
            loop_metadata = dict(message.get("loop") or {})
            loop_metadata["round_input"] = dict((message.get("round") or {}).get("input") or {})
            ss.result = {"result": message.get("result"), "loop": loop_metadata}
            ss.running = False
            ss.crew_thread = None
            return

        if message_type == "loop_failed":
            self.update_loop_round(message.get("round"))
            ss.result = message.get("result")
            ss.running = False
            ss.crew_thread = None
            return

        if message_type == "loop_stopped":
            ss.running = False
            ss.crew_thread = None
```

- [ ] **Step 4: Add loop thread target**

Add this method after the existing `run_crew()` method:

```python
    def run_crew_loop_thread(self, selected_crew, inputs, loop_config, message_queue, stop_event):
        if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
            import agentops
            agentops.start_session()
        try:
            run_crew_loop(
                crew_factory=lambda: selected_crew.get_crewai_crew(full_output=True),
                base_inputs=inputs,
                config=loop_config,
                message_queue=message_queue,
                stop_event=stop_event,
            )
        except Exception as e:
            if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
                agentops.end_session()
            stack_trace = traceback.format_exc()
            print(f"Error running crew loop: {str(e)}\n{stack_trace}")
            message_queue.put({"type": "loop_failed", "result": f"Error running crew loop: {str(e)}", "stack_trace": stack_trace})
        finally:
            if hasattr(ss, 'console_capture'):
                ss.console_capture.stop()
```

- [ ] **Step 5: Start loop thread from run button**

Inside `control_buttons()`, replace:

```python
            inputs = {key.split('_')[1]: value for key, value in ss.placeholders.items()}
```

with:

```python
            inputs = self.current_inputs()
```

Before creating the thread, add:

```python
            ss.loop_rounds = []
            ss.loop_stop_event = threading.Event()
            loop_config = self.build_loop_config()
```

Replace the single unconditional thread creation with:

```python
            if loop_config.enabled:
                ss.crew_thread = threading.Thread(
                    target=self.run_crew_loop_thread,
                    kwargs={
                        "selected_crew": selected_crew,
                        "inputs": inputs,
                        "loop_config": loop_config,
                        "message_queue": ss.message_queue,
                        "stop_event": ss.loop_stop_event,
                    },
                )
            else:
                ss.crew_thread = threading.Thread(
                    target=self.run_crew,
                    kwargs={
                        "crewai_crew": crew,
                        "inputs": inputs,
                        "message_queue": ss.message_queue,
                    },
                )
```

Keep the existing `ss.crew_thread.start()`, `ss.result = None`, `ss.running = True`, and `st.rerun()` after this block.

- [ ] **Step 6: Stop whole loop**

In the `if stop_clicked:` block, before `self.force_stop_thread(ss.crew_thread)`, add:

```python
            if ss.loop_stop_event is not None:
                ss.loop_stop_event.set()
```

After clearing `ss.crew_thread`, add:

```python
            ss.loop_stop_event = None
```

- [ ] **Step 7: Poll queue before displaying saved results**

Add this method to `PageCrewRun` before `display_result()`:

```python
    def poll_run_queue(self):
        if not (ss.running and ss.crew_thread is not None):
            return
        try:
            message = ss.message_queue.get_nowait()
        except queue.Empty:
            return

        if isinstance(message, dict) and str(message.get("type", "")).startswith("loop_"):
            self.apply_loop_queue_message(message)
            return

        ss.result = message
        ss.running = False
        ss.crew_thread = None
        if hasattr(ss, 'console_capture'):
            ss.console_capture.stop()
```

In `display_result()`, after the console panel block and before `if ss.result is not None:`, add:

```python
        self.poll_run_queue()
```

Then replace this existing polling block:

```python
                    message = ss.message_queue.get_nowait()
                    if str(message.get("type", "")).startswith("loop_"):
                        self.apply_loop_queue_message(message)
                    else:
                        ss.result = message
                        ss.running = False
                        if hasattr(ss, 'console_capture'):
                            ss.console_capture.stop()
                    st.rerun()
```

with:

```python
                    self.poll_run_queue()
                    st.rerun()
```

This ordering matters: loop round success stores `ss.result` for display and persistence, but the page must keep polling later loop messages while `ss.running` is still true.

- [ ] **Step 8: Persist loop metadata with round results**

In `display_result()`, before the `Result(` construction, add:

```python
                    stored_inputs = {key.split('_', 1)[1]: value for key, value in relevant_placeholders.items()}
                    if isinstance(ss.result, dict) and "loop" in ss.result:
                        stored_inputs = ss.result["loop"].get("round_input", stored_inputs)
```

Then replace the `Result(` construction with:

```python
                    result = Result(
                        id=f"R_{rnd_id()}",
                        crew_id=ss.selected_crew_name,
                        crew_name=ss.selected_crew_name,
                        inputs=stored_inputs,
                        result=self.serialize_result(ss.result, curr_crew),
                    )
```

This keeps non-loop result persistence unchanged and makes loop results store the actual round input instead of the original form input.

- [ ] **Step 9: Run page loop tests**

Run:

```bash
.venv312/bin/python -m unittest tests/test_crew_run_page_loop.py -v
```

Expected result:

```text
Ran 3 tests

OK
```

- [ ] **Step 10: Run all tests**

Run:

```bash
.venv312/bin/python -m unittest discover -s tests -v
```

Expected result:

```text
OK
```

- [ ] **Step 11: Commit Task 3**

Run:

```bash
git add app/pg_crew_run.py tests/test_crew_run_page_loop.py
git commit -m "Wire crew run loop execution" -m "Connect loop configuration to the Crew run thread, consume per-round queue messages, persist round results, and stop the whole loop through the existing stop control." -m "Tested: .venv312/bin/python -m unittest discover -s tests -v" -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
```

---

## Task 4: Progress Display and Styling

**Files:**
- Modify: `app/pg_crew_run.py`
- Modify: `app/ui_styles.py`
- Modify: `tests/test_ui_workbench.py`

- [ ] **Step 1: Write failing source-level style tests**

Add these assertions to `test_execution_page_has_cockpit_sections` in `tests/test_ui_workbench.py`:

```python
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn("def draw_loop_progress", source)
        self.assertIn("crew-run-loop-panel", source)
        self.assertIn("crew-run-loop-round", source)
        self.assertIn(".crew-run-loop-panel", style_source)
        self.assertIn(".crew-run-loop-round", style_source)
```

- [ ] **Step 2: Run UI tests and verify failure**

Run:

```bash
.venv312/bin/python -m unittest tests/test_ui_workbench.py -v
```

Expected result:

```text
FAIL: test_execution_page_has_cockpit_sections
```

- [ ] **Step 3: Add loop progress renderer**

Add this method to `PageCrewRun` after `draw_loop_controls()`:

```python
    def draw_loop_progress(self):
        if not ss.loop_rounds:
            return

        total = max([round_info.get("total", 1) for round_info in ss.loop_rounds] or [1])
        completed = len([round_info for round_info in ss.loop_rounds if round_info.get("status") in {"success", "failed", "stopped"}])
        progress = min(1.0, completed / max(1, total))

        st.markdown(f"#### {t('crew_run.loop_progress')}")
        st.progress(progress)
        rows = []
        status_labels = {
            "waiting": t("crew_run.loop_status_waiting"),
            "running": t("crew_run.loop_status_running"),
            "success": t("crew_run.loop_status_success"),
            "failed": t("crew_run.loop_status_failed"),
            "stopped": t("crew_run.loop_status_stopped"),
        }
        for round_info in ss.loop_rounds:
            status = round_info.get("status", "waiting")
            label = status_labels.get(status, status)
            rows.append(
                f'<div class="crew-run-loop-round is-{status}">'
                f'{t("crew_run.loop_round_status", index=round_info.get("index"), total=round_info.get("total"), status=label)}'
                f'</div>'
            )
        st.markdown(
            f'<div class="crew-run-loop-panel">{"".join(rows)}</div>',
            unsafe_allow_html=True,
        )
```

In `draw_crews()`, after `self.control_buttons(selected_crew, loop_config_valid=loop_config_valid)`, add:

```python
                self.draw_loop_progress()
```

- [ ] **Step 4: Add CSS**

In `app/ui_styles.py`, near the existing `.crew-run-log-panel` styles, add:

```css
        .crew-run-loop-panel {
          display: flex;
          flex-direction: column;
          gap: 0.42rem;
          margin-top: 0.6rem;
          padding: 0.72rem;
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 8px;
          background: rgba(15, 23, 42, 0.34);
        }

        .crew-run-loop-round {
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 7px;
          padding: 0.5rem 0.62rem;
          color: var(--studio-muted);
          background: rgba(15, 23, 42, 0.42);
          font-size: 0.84rem;
          font-weight: 650;
        }

        .crew-run-loop-round.is-running {
          color: #dbeafe;
          border-color: rgba(96, 165, 250, 0.28);
          background: rgba(37, 99, 235, 0.14);
        }

        .crew-run-loop-round.is-success {
          color: #bbf7d0;
          border-color: rgba(34, 197, 94, 0.24);
          background: rgba(22, 101, 52, 0.16);
        }

        .crew-run-loop-round.is-failed,
        .crew-run-loop-round.is-stopped {
          color: #fecaca;
          border-color: rgba(248, 113, 113, 0.24);
          background: rgba(127, 29, 29, 0.16);
        }
```

- [ ] **Step 5: Run UI tests**

Run:

```bash
.venv312/bin/python -m unittest tests/test_ui_workbench.py -v
```

Expected result:

```text
OK
```

- [ ] **Step 6: Commit Task 4**

Run:

```bash
git add app/pg_crew_run.py app/ui_styles.py tests/test_ui_workbench.py
git commit -m "Show crew run loop progress" -m "Add visible progress and per-round status rows for loop execution so users can inspect which round is running, completed, failed, or stopped." -m "Tested: .venv312/bin/python -m unittest tests/test_ui_workbench.py -v" -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
```

---

## Task 5: End-to-End Verification

**Files:**
- Modify only if verification exposes defects.

- [ ] **Step 1: Run full test suite**

Run:

```bash
.venv312/bin/python -m unittest discover -s tests -v
```

Expected result:

```text
OK
```

- [ ] **Step 2: Restart Streamlit**

Find the existing process:

```bash
lsof -nP -iTCP:8501 -sTCP:LISTEN
```

If a process is listed, stop it:

```bash
kill $(lsof -tiTCP:8501 -sTCP:LISTEN)
```

Start the app:

```bash
env CREWAI_STORAGE_DIR=/Users/doukaiwei/Documents/codeProjects/crew-ai/.crewai_storage .venv312/bin/streamlit run app/app.py --server.headless true --server.address 127.0.0.1 --server.port 8501
```

Verify it responds:

```bash
curl -I http://127.0.0.1:8501/
```

Expected result:

```text
HTTP/1.1 200 OK
```

- [ ] **Step 3: Manual UI verification**

In the browser at `http://127.0.0.1:8501/`:

1. Open the execution page.
2. Select a valid Crew that has at least one placeholder.
3. Fill the placeholder input.
4. Enable Loop.
5. Set loop count to `2`.
6. Select the placeholder that receives previous output.
7. Run the Crew.
8. Confirm the loop progress panel shows round 1 and round 2.
9. Confirm two successful rounds appear if both kickoffs succeed.
10. Open the results page.
11. Confirm each round has a saved result.

- [ ] **Step 4: Stop behavior verification**

In the browser:

1. Start a loop with count `5`.
2. Click stop while a round is running.
3. Confirm no later round starts after the stop.
4. Confirm already successful rounds remain in results.
5. Confirm the app remains responsive after stop.

- [ ] **Step 5: Commit verification fixes if needed**

If Step 3 or Step 4 exposes a defect, fix only that defect and commit:

```bash
git add app/pg_crew_run.py app/ui_styles.py tests
git commit -m "Fix crew run loop verification issue" -m "Address the defect found during manual loop verification while preserving the approved loop behavior and test coverage." -m "Tested: .venv312/bin/python -m unittest discover -s tests -v" -m "Co-authored-by: OmX <omx@oh-my-codex.dev>"
```

If no defect is found, do not create an empty commit.

---

## Self-Review

Spec coverage:

- Loop controls are covered in Task 2.
- Previous-output injection into a selected placeholder is covered in Task 1 and Task 3.
- Sequential execution and stop-on-failure behavior are covered in Task 1.
- Per-round result persistence is covered in Task 3.
- Progress display is covered in Task 4.
- Stop behavior is covered in Task 3 and verified in Task 5.
- Full test and manual verification are covered in Task 5.

Placeholder scan:

- The plan contains no forbidden placeholder token, no unresolved decision, and no open implementation placeholder.

Type consistency:

- `LoopConfig`, `run_crew_loop`, `build_round_inputs`, and `extract_final_output` are introduced in Task 1 and reused by later tasks with the same names.
- Queue message types are consistently named `loop_round_start`, `loop_round_success`, `loop_complete`, `loop_failed`, and `loop_stopped`.
- Session-state keys are consistently named `loop_enabled`, `loop_count`, `loop_target_placeholder`, `loop_run_id`, `loop_rounds`, and `loop_stop_event`.
