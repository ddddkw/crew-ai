from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import traceback
from typing import Any, Mapping


_MISSING = object()


@dataclass
class LoopConfig:
    enabled: bool = False
    count: int = 1
    target_placeholder: str | None = None
    loop_id: str | None = None


def normalize_loop_count(value: Any) -> int:
    try:
        return max(1, int(value or 1))
    except (TypeError, ValueError):
        return 1


def build_round_inputs(
    base_inputs: Mapping[str, Any],
    target_placeholder: str | None,
    previous_output: str | None,
) -> dict[str, Any]:
    inputs = dict(base_inputs)
    if target_placeholder and previous_output is not None:
        inputs[target_placeholder] = previous_output
    return inputs


def extract_final_output(result: Any) -> str:
    if isinstance(result, dict):
        for key in ("result", "raw", "final_output"):
            if key in result:
                return extract_final_output(result[key])
    if hasattr(result, "raw"):
        return str(getattr(result, "raw") or "").strip()
    return str(result or "").strip()


def run_crew_loop(
    crew_factory: Any,
    base_inputs: Mapping[str, Any],
    config: LoopConfig,
    message_queue: Any,
    stop_event: Any,
) -> str | None:
    total_rounds = normalize_loop_count(config.count)
    loop_id = config.loop_id or f"L_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    target_placeholder = config.target_placeholder
    previous_output: str | None = None
    latest_output: str | None = None
    latest_result: Any = None
    current_index = 1
    current_inputs = dict(base_inputs)
    current_output = ""
    current_started_at = _now()
    round_previous_output: str | None = None
    last_inputs = current_inputs
    last_started_at = current_started_at
    last_previous_output: str | None = None

    try:
        if config.enabled and not target_placeholder:
            raise ValueError("loop target placeholder is required")

        for current_index in range(1, total_rounds + 1):
            round_previous_output = previous_output
            current_inputs = build_round_inputs(
                base_inputs,
                target_placeholder,
                round_previous_output,
            )
            current_output = ""

            if stop_event.is_set():
                message_queue.put(
                    _round_message(
                        "loop_stopped",
                        loop_id,
                        target_placeholder,
                        current_index,
                        total_rounds,
                        round_previous_output,
                        "stopped",
                        current_inputs,
                        output=latest_output or "",
                        result=latest_result,
                    )
                )
                return latest_output

            current_started_at = _now()
            message_queue.put(
                _round_message(
                    "loop_round_start",
                    loop_id,
                    target_placeholder,
                    current_index,
                    total_rounds,
                    round_previous_output,
                    "started",
                    current_inputs,
                    started_at=current_started_at,
                )
            )

            result = crew_factory().kickoff(inputs=current_inputs)
            final_output = extract_final_output(result)
            current_output = final_output
            if not final_output:
                raise ValueError(f"round {current_index} produced empty final output")

            latest_output = final_output
            latest_result = result
            last_inputs = current_inputs
            last_started_at = current_started_at
            last_previous_output = round_previous_output
            message_queue.put(
                _round_message(
                    "loop_round_success",
                    loop_id,
                    target_placeholder,
                    current_index,
                    total_rounds,
                    round_previous_output,
                    "success",
                    current_inputs,
                    output=final_output,
                    result=result,
                    started_at=current_started_at,
                )
            )
            previous_output = final_output

        message_queue.put(
            _round_message(
                "loop_complete",
                loop_id,
                target_placeholder,
                total_rounds,
                total_rounds,
                last_previous_output,
                "success",
                last_inputs,
                output=latest_output or "",
                result=latest_result,
                started_at=last_started_at,
            )
        )
        return latest_output
    except Exception as exc:
        error = str(exc)
        message_queue.put(
            _round_message(
                "loop_failed",
                loop_id,
                target_placeholder,
                current_index,
                total_rounds,
                round_previous_output,
                "failed",
                current_inputs,
                output=current_output,
                error=error,
                result=error,
                stack_trace=traceback.format_exc(),
                started_at=current_started_at,
            )
        )
        return None


def _round_message(
    message_type: str,
    loop_id: str,
    target_placeholder: str | None,
    index: int,
    total_rounds: int,
    previous_output: str | None,
    status: str,
    inputs: Mapping[str, Any],
    *,
    output: str = "",
    error: str = "",
    result: Any = _MISSING,
    stack_trace: str | None = None,
    started_at: str | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "type": message_type,
        "loop": {
            "enabled": True,
            "loop_id": loop_id,
            "index": index,
            "total": total_rounds,
            "target_placeholder": target_placeholder,
            "previous_output": previous_output,
        },
        "round": {
            "loop_id": loop_id,
            "index": index,
            "total": total_rounds,
            "status": status,
            "input": dict(inputs),
            "output": output,
            "error": error,
            "started_at": started_at or _now(),
            "finished_at": _now() if status in {"success", "failed", "stopped"} else "",
        },
    }
    if result is not _MISSING:
        message["result"] = result
    if stack_trace is not None:
        message["stack_trace"] = stack_trace
    return message


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
