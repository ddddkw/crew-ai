import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class ToolNameResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db_utils
        import my_tools

        cls.db_utils = db_utils
        cls.my_tools = my_tools

    def test_resolves_chinese_tool_display_name_from_existing_database(self):
        tool_class = self.my_tools.resolve_tool_class("DuckDuckGo 搜索")

        self.assertIs(tool_class, self.my_tools.TOOL_CLASSES["DuckDuckGoSearchTool"])

    def test_resolves_missing_translation_key_display_names(self):
        tool_class = self.my_tools.resolve_tool_class("tool.selenium_scraping")

        self.assertIs(tool_class, self.my_tools.TOOL_CLASSES["SeleniumScrapingTool"])

    def test_load_tools_accepts_legacy_localized_name(self):
        original_load_entities = self.db_utils.load_entities
        try:
            self.db_utils.load_entities = lambda entity_type: [
                ("tool_1", {"name": "DuckDuckGo 搜索", "parameters": {}})
            ] if entity_type == "tool" else []

            tools = self.db_utils.load_tools()
        finally:
            self.db_utils.load_entities = original_load_entities

        self.assertEqual(len(tools), 1)
        self.assertIsInstance(tools[0], self.my_tools.TOOL_CLASSES["DuckDuckGoSearchTool"])

    def test_save_tool_persists_canonical_name_and_display_name(self):
        captured = {}
        original_save_entity = self.db_utils.save_entity
        try:
            self.db_utils.save_entity = lambda entity_type, entity_id, data: captured.update(
                {"entity_type": entity_type, "entity_id": entity_id, "data": data}
            )

            self.db_utils.save_tool(self.my_tools.MyDuckDuckGoSearchTool(tool_id="tool_1"))
        finally:
            self.db_utils.save_entity = original_save_entity

        self.assertEqual(captured["entity_type"], "tool")
        self.assertEqual(captured["data"]["name"], "DuckDuckGoSearchTool")
        self.assertIn("display_name", captured["data"])

    def test_import_export_page_uses_tool_resolver(self):
        source = (ROOT / "app" / "pg_export_crew.py").read_text(encoding="utf-8")

        self.assertIn("resolve_tool_class", source)
        self.assertIn("get_tool_class_key", source)
        self.assertNotIn("TOOL_CLASSES[tool_data['name']]", source)


if __name__ == "__main__":
    unittest.main()
