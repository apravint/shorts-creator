"""Tests for the FastMCP tool dispatch and specification."""

import unittest
from unittest.mock import patch
from shorts_creator.mcp_server import TOOLS_SPEC, handle_tool_call


class TestMCPServer(unittest.TestCase):
    def test_tools_spec_validity(self):
        self.assertGreaterEqual(len(TOOLS_SPEC), 4)
        for tool in TOOLS_SPEC:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)

    def test_tool_call_list_voices(self):
        res = handle_tool_call("list_voices", {"lang": "en"})
        self.assertEqual(res["status"], "success")
        self.assertIn("voices", res)
        self.assertIn("female", res["voices"])

    @patch("shorts_creator.mcp_server.prepare_script")
    def test_tool_call_generate_script(self, mock_prepare):
        mock_prepare.return_value = {
            "title": "AI Revolution",
            "script": "The world is changing.",
            "sentences": ["The world is changing."],
            "tags": ["#ai"]
        }
        res = handle_tool_call("generate_script", {"topic": "AI Revolution", "lang": "en"})
        self.assertEqual(res["status"], "success")
        self.assertIn("script", res)
        self.assertEqual(res["script"]["title"], "AI Revolution")

    def test_tool_call_unknown(self):
        res = handle_tool_call("nonexistent_tool_xyz", {})
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
