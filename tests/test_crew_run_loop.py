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
