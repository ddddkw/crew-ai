from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CrewRunNavigationTests(unittest.TestCase):
    def test_crew_run_does_not_force_english_kickoff_page_key(self):
        source = (ROOT / "app" / "pg_crew_run.py").read_text(encoding="utf-8")

        self.assertNotIn('ss.page = "Kickoff!"', source)
        self.assertNotIn("ss.page != \"Kickoff!\"", source)


if __name__ == "__main__":
    unittest.main()
