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
        self.assertEqual(fake_state.result["loop"]["round_input"], {"requirement": "initial"})

    def test_loop_complete_stops_running(self):
        import pg_crew_run

        original_state = pg_crew_run.ss
        fake_state = FakeSessionState(loop_rounds=[], running=True, result=None, crew_thread="thread")
        page = pg_crew_run.PageCrewRun.__new__(pg_crew_run.PageCrewRun)
        result = SimpleNamespace(raw="final", tasks_output=[])

        try:
            pg_crew_run.ss = fake_state
            page.apply_loop_queue_message(
                {
                    "type": "loop_complete",
                    "loop": {"enabled": True, "loop_id": "L_1", "index": 2, "total": 2, "target_placeholder": "requirement", "previous_output": "prev"},
                    "round": {"loop_id": "L_1", "index": 2, "total": 2, "status": "success", "input": {"requirement": "prev"}, "output": "final", "error": "", "started_at": "s", "finished_at": "f"},
                    "result": result,
                }
            )
        finally:
            pg_crew_run.ss = original_state

        self.assertFalse(fake_state.running)
        self.assertIsNone(fake_state.crew_thread)
        self.assertEqual(fake_state.result["result"], result)
        self.assertEqual(fake_state.result["loop"]["round_input"], {"requirement": "prev"})
