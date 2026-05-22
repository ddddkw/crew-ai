from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import traceback
from typing import Any, Mapping


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
    previous_output: str | None = None
    latest_result: str | None = None
    current_index = 0

    try:
        for current_index in range(total_rounds):
            if stop_event.is_set():
                message_queue.put(
                    _round_message(
                        "loop_stopped",
                        config,
                        current_index,
                        total_rounds,
                        result=latest_result,
                    )
                )
                return latest_result

            current_inputs = build_round_inputs(
                base_inputs,
                config.target_placeholder,
                previous_output,
            )
            message_queue.put(
                _round_message(
                    "loop_round_start",
                    config,
                    current_index,
                    total_rounds,
                    inputs=current_inputs,
                )
            )

            result = crew_factory().kickoff(inputs=current_inputs)
            final_output = extract_final_output(result)
            if not final_output:
                raise ValueError(f"round {current_index + 1} produced empty final output")

            latest_result = final_output
            message_queue.put(
                _round_message(
                    "loop_round_success",
                    config,
                    current_index,
                    total_rounds,
                    result=final_output,
                )
            )
            previous_output = final_output

        complete_index = max(0, total_rounds - 1)
        message_queue.put(
            _round_message(
                "loop_complete",
                config,
                complete_index,
                total_rounds,
                result=latest_result,
            )
        )
        return latest_result
    except Exception as exc:
        message_queue.put(
            _round_message(
                "loop_failed",
                config,
                current_index,
                total_rounds,
                result=str(exc),
                stack_trace=traceback.format_exc(),
            )
        )
        return None


def _round_message(
    message_type: str,
    config: LoopConfig,
    current_index: int,
    total_rounds: int,
    *,
    result: str | None = None,
    stack_trace: str | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "type": message_type,
        "timestamp": _timestamp(),
        "loop": {
            "id": config.loop_id,
            "enabled": config.enabled,
            "count": total_rounds,
            "target_placeholder": config.target_placeholder,
            "current_index": current_index,
        },
        "round": {
            "index": current_index,
            "number": current_index + 1,
            "total": total_rounds,
        },
    }
    if result is not None:
        message["result"] = result
    if stack_trace is not None:
        message["stack_trace"] = stack_trace
    if inputs is not None:
        message["inputs"] = dict(inputs)
    return message


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
