# Crew Run Loop Design

## Goal

Add a loop mode to the Crew run page so a selected Crew can run multiple kickoff rounds automatically. From round 2 onward, the previous round's final output is injected into a user-selected placeholder before the next kickoff starts.

This feature targets iterative refinement workflows, such as generating a draft in round 1, improving it in round 2, and refining it again in later rounds.

## Scope

In scope:

- Add loop controls to the existing Crew execution page.
- Let the user enable or disable loop mode before running.
- Let the user set the loop count.
- Let the user choose which existing placeholder receives the previous round output.
- Run each round sequentially in the existing background execution thread.
- Save every round as an individual result.
- Attach loop metadata to each saved result.
- Show loop progress and per-round status in the execution page.
- Stop the whole loop when the user clicks stop.

Out of scope for the first implementation:

- Parallel loop execution.
- Batch input lists.
- Automatic placeholder guessing without user choice.
- Editing task or crew definitions during loop execution.
- Result comparison UI in the results page.
- Conditional loop termination based on model-evaluated quality.

## Current Context

The current execution path is centered in `app/pg_crew_run.py`.

- `control_buttons()` reads placeholder values from `ss.placeholders`.
- It creates a CrewAI crew with `selected_crew.get_crewai_crew(full_output=True)`.
- It starts a background thread targeting `run_crew()`.
- `run_crew()` calls `crewai_crew.kickoff(inputs=inputs)` once and pushes the result into `ss.message_queue`.
- `display_result()` consumes the message queue, stores `ss.result`, displays output, and saves a `Result` through `save_result()`.

The loop feature should extend this path without changing Crew, Agent, or Task definitions.

## User Flow

1. The user selects a Crew on the execution page.
2. The page extracts placeholders from the Crew as it does today.
3. The user fills the initial placeholder values.
4. The user enables loop mode.
5. The user sets loop count, for example `3`.
6. The user selects the placeholder that should receive previous output, for example `requirement`.
7. The user clicks run.
8. Round 1 runs with the manually entered placeholder inputs.
9. Round 1 final output is extracted.
10. Round 2 runs with the same inputs except `requirement` is replaced by round 1 final output.
11. The process repeats until all rounds finish, a round fails, or the user stops the run.

## Loop Input Semantics

The selected placeholder is the only value automatically changed between rounds.

Example:

```python
initial_inputs = {
    "requirement": "请生成一个项目说明",
    "style": "简洁",
}
```

If the user selects `requirement` as the loop target:

```python
round_1_inputs = {
    "requirement": "请生成一个项目说明",
    "style": "简洁",
}

round_2_inputs = {
    "requirement": "<round 1 final output>",
    "style": "简洁",
}

round_3_inputs = {
    "requirement": "<round 2 final output>",
    "style": "简洁",
}
```

Other placeholders remain stable unless the user changes them before a new run starts.

## Output Extraction

The loop needs a deterministic final-output extraction function.

Recommended behavior:

1. If the kickoff result has `result.raw`, use `result.raw`.
2. Else if the message payload contains a `result` object with `.raw`, use that.
3. Else use `str(result)`.
4. Strip surrounding whitespace.

If the extracted output is empty, treat the round as failed because the next round would not have meaningful input.

## Execution Model

Add a new runner that can execute either one round or loop rounds:

```python
run_crew_loop(crewai_crew_factory, base_inputs, loop_config, message_queue, stop_event)
```

The runner should create a fresh CrewAI crew for each round if practical. This avoids hidden state leaking across rounds from the CrewAI runtime. If construction cost is too high, reusing the crew can be evaluated later, but fresh construction is the safer first implementation.

Each round:

1. Check stop event.
2. Build current inputs.
3. Emit a round-start message.
4. Run kickoff.
5. Extract final output.
6. Emit a round-success message with result and output.
7. Save enough metadata for the UI and result persistence.
8. Use extracted output as next round's loop placeholder value.

Failure behavior for the first implementation:

- Stop the loop on the first failed round.
- Emit a round-failed message with stack trace.
- Preserve successful prior rounds.

## State Model

Add Streamlit session state keys:

- `loop_enabled`: boolean.
- `loop_count`: integer, default `1`, minimum `1`.
- `loop_target_placeholder`: string or `None`.
- `loop_run_id`: generated ID for the current loop run.
- `loop_rounds`: list of round status dictionaries.
- `loop_stop_requested`: boolean or a `threading.Event`.

Round status dictionary:

```python
{
    "loop_id": "L_xxx",
    "index": 1,
    "total": 3,
    "status": "running | success | failed | stopped",
    "input": {...},
    "output": "...",
    "error": "...",
    "started_at": "...",
    "finished_at": "...",
}
```

## Result Persistence

Each successful round should be saved as a normal `Result` so existing results behavior continues to work.

Add metadata into the serialized result payload:

```python
{
    "loop": {
        "enabled": True,
        "loop_id": "L_xxx",
        "index": 1,
        "total": 3,
        "target_placeholder": "requirement",
        "previous_output": "... or None"
    },
    "result": "<existing serialized result>"
}
```

This avoids requiring a database schema migration because the app already stores JSON in the `entities` table.

## UI Design

In `PageCrewRun.control_buttons()` or nearby execution controls:

- Add an expander or compact panel named `Loop`.
- Add checkbox `启用 Loop`.
- Add number input `循环次数`.
- Add selectbox `上一轮结果注入到`.
- The selectbox options come from `get_placeholders_from_crew(selected_crew)`.
- Disable loop controls while running.

Validation:

- If loop is enabled and no placeholders exist, show an error and disable run.
- If loop is enabled and no target placeholder is selected, show an error and disable run.
- If loop count is `1`, behavior is equivalent to a normal single run except metadata may say loop disabled or total 1.

Progress display:

- Show current round as `第 N / M 轮`.
- Show a progress bar based on completed rounds.
- Show a compact list of round statuses.
- Continue using the existing console output panel for detailed runtime logs.

## Stop Behavior

The stop button should stop the whole loop, not only the current round.

Expected behavior:

- Set the loop stop flag.
- Attempt to stop the active thread using the existing force-stop path.
- Do not start any subsequent rounds.
- Mark pending rounds as stopped where possible.
- Stop console capture.
- Leave successful completed rounds saved.

## Error Handling

Validation errors happen before the thread starts:

- Missing placeholder target.
- Invalid loop count.
- Selected Crew is invalid.

Runtime errors happen inside a round:

- Capture stack trace.
- Mark current round failed.
- Stop loop.
- Send failure message through the queue.
- Display the error in the existing result area.

## Testing Plan

Unit-level tests:

- Placeholder extraction is used to populate loop target options.
- Loop config validation disables run when no target placeholder exists.
- Round 2 input replaces only the selected placeholder.
- Other placeholders remain unchanged across rounds.
- Empty extracted output fails the loop.
- Every successful round produces saveable result metadata.
- Stop flag prevents subsequent rounds.

Source-level UI tests:

- Execution page contains loop controls.
- Run path passes loop config into the runner.
- Result serialization preserves loop metadata.

Manual verification:

- Run a Crew with one placeholder for two rounds.
- Confirm round 2 input is round 1 output.
- Confirm two results appear after completion.
- Start a longer loop and stop it during execution.

## Open Decisions

Resolved:

- Loop mode uses previous round output as the next round input.
- The user chooses the target placeholder explicitly.
- First implementation stops on first failure.
- First implementation runs rounds sequentially.

Deferred:

- Batch input mode.
- Result comparison UI.
- Conditional quality-based stopping.
- Continuing after failed rounds.
