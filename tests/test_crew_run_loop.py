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


def drain_messages(messages):
    drained = []
    while not messages.empty():
        drained.append(messages.get_nowait())
    return drained


class CrewRunLoopTests(unittest.TestCase):
    def test_loop_config_defaults(self):
        from crew_run_loop import LoopConfig

        config = LoopConfig()

        self.assertFalse(config.enabled)
        self.assertEqual(config.count, 1)
        self.assertIsNone(config.target_placeholder)
        self.assertIsNone(config.loop_id)

    def test_normalize_loop_count(self):
        from crew_run_loop import normalize_loop_count

        self.assertEqual(normalize_loop_count(None), 1)
        self.assertEqual(normalize_loop_count(0), 1)
        self.assertEqual(normalize_loop_count(-3), 1)
        self.assertEqual(normalize_loop_count(4), 4)
        self.assertEqual(normalize_loop_count("5"), 5)
        self.assertEqual(normalize_loop_count("invalid"), 1)

    def test_extract_final_output_prefers_result_raw(self):
        from crew_run_loop import extract_final_output

        result = SimpleNamespace(raw=" final answer ", tasks_output=[])

        self.assertEqual(extract_final_output(result), "final answer")

    def test_extract_final_output_strips_nested_dict_values(self):
        from crew_run_loop import extract_final_output

        self.assertEqual(extract_final_output({"result": {"raw": " nested answer "}}), "nested answer")
        self.assertEqual(extract_final_output({"raw": " raw answer "}), "raw answer")
        self.assertEqual(extract_final_output({"final_output": " final answer "}), "final answer")

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

    def test_run_crew_loop_generates_loop_id_when_config_loop_id_is_none(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory(["round one"])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=1, target_placeholder="requirement"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        drained = drain_messages(messages)
        loop_ids = {message["loop"]["loop_id"] for message in drained}

        self.assertEqual(len(loop_ids), 1)
        loop_id = loop_ids.pop()
        self.assertRegex(loop_id, r"^L_\d{20}$")
        self.assertTrue(all(message["round"]["loop_id"] == loop_id for message in drained))

    def test_run_crew_loop_emits_loop_enabled_true_when_config_disabled(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory(["round one"])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=False, count=1, target_placeholder="requirement", loop_id="L_disabled"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        drained = drain_messages(messages)

        self.assertEqual([message["loop"]["enabled"] for message in drained], [True, True, True])

    def test_loop_round_success_has_contract_payload_and_original_result(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        result = SimpleNamespace(raw=" round one ", tasks_output=[])

        class ResultCrew:
            def kickoff(self, inputs):
                return result

        run_crew_loop(
            crew_factory=ResultCrew,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=1, target_placeholder="requirement", loop_id="L_contract"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        success = [message for message in drain_messages(messages) if message["type"] == "loop_round_success"][0]

        self.assertEqual(set(success), {"type", "loop", "round", "result"})
        self.assertEqual(
            success["loop"],
            {
                "enabled": True,
                "loop_id": "L_contract",
                "index": 1,
                "total": 1,
                "target_placeholder": "requirement",
                "previous_output": None,
            },
        )
        self.assertEqual(
            set(success["round"]),
            {"loop_id", "index", "total", "status", "input", "output", "error", "started_at", "finished_at"},
        )
        self.assertEqual(success["round"]["loop_id"], "L_contract")
        self.assertEqual(success["round"]["index"], 1)
        self.assertEqual(success["round"]["total"], 1)
        self.assertEqual(success["round"]["status"], "success")
        self.assertEqual(success["round"]["input"], {"requirement": "initial"})
        self.assertEqual(success["round"]["output"], "round one")
        self.assertEqual(success["round"]["error"], "")
        self.assertTrue(success["round"]["started_at"])
        self.assertTrue(success["round"]["finished_at"])
        self.assertIs(success["result"], result)

    def test_loop_complete_preserves_original_final_result_object(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        results = [
            SimpleNamespace(raw="round one", tasks_output=[]),
            SimpleNamespace(raw="round two", tasks_output=[]),
        ]
        calls = []

        class ResultCrewFactory:
            def __call__(self):
                result = results[len(calls)]

                class ResultCrew:
                    def kickoff(self, inputs):
                        calls.append(dict(inputs))
                        return result

                return ResultCrew()

        run_crew_loop(
            crew_factory=ResultCrewFactory(),
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=2, target_placeholder="requirement", loop_id="L_complete"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        complete = drain_messages(messages)[-1]

        self.assertEqual(complete["type"], "loop_complete")
        self.assertEqual(set(complete), {"type", "loop", "round", "result"})
        self.assertIs(complete["result"], results[1])
        self.assertEqual(complete["loop"]["index"], 2)
        self.assertEqual(complete["loop"]["previous_output"], "round one")
        self.assertEqual(complete["round"]["index"], 2)
        self.assertEqual(complete["round"]["status"], "success")
        self.assertEqual(complete["round"]["input"], {"requirement": "round one"})
        self.assertEqual(complete["round"]["output"], "round two")

    def test_run_crew_loop_fails_when_enabled_without_target_placeholder(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory(["should not run"])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=1, loop_id="L_missing"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        failed = drain_messages(messages)[-1]

        self.assertEqual(factory.calls, [])
        self.assertEqual(failed["type"], "loop_failed")
        self.assertEqual(failed["result"], "loop target placeholder is required")
        self.assertIn("stack_trace", failed)
        self.assertEqual(failed["loop"]["loop_id"], "L_missing")
        self.assertEqual(failed["loop"]["index"], 1)
        self.assertEqual(failed["round"]["index"], 1)
        self.assertEqual(failed["round"]["status"], "failed")
        self.assertEqual(failed["round"]["input"], {"requirement": "initial"})
        self.assertEqual(failed["round"]["error"], "loop target placeholder is required")

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

    def test_loop_failed_contains_failed_input_and_one_based_failed_index(self):
        from crew_run_loop import LoopConfig, run_crew_loop

        messages = queue.Queue()
        factory = FakeCrewFactory(["round one", ""])

        run_crew_loop(
            crew_factory=factory,
            base_inputs={"requirement": "initial"},
            config=LoopConfig(enabled=True, count=2, target_placeholder="requirement", loop_id="L_failed"),
            message_queue=messages,
            stop_event=threading.Event(),
        )

        failed = drain_messages(messages)[-1]

        self.assertEqual(failed["type"], "loop_failed")
        self.assertEqual(failed["result"], "round 2 produced empty final output")
        self.assertIn("stack_trace", failed)
        self.assertEqual(failed["loop"]["index"], 2)
        self.assertEqual(failed["loop"]["previous_output"], "round one")
        self.assertEqual(failed["round"]["index"], 2)
        self.assertEqual(failed["round"]["status"], "failed")
        self.assertEqual(failed["round"]["input"], {"requirement": "round one"})
        self.assertEqual(failed["round"]["output"], "")
        self.assertEqual(failed["round"]["error"], "round 2 produced empty final output")

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
