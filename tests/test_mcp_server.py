import json
import unittest

from inboxshield.mcp_server import handle


class MCPServerTests(unittest.TestCase):
    def test_lists_tools(self):
        response = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertEqual(
            names, {"policy_lookup", "security_scan", "ticket_classify"}
        )

    def test_calls_policy_tool(self):
        response = handle(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "policy_lookup",
                    "arguments": {"category": "account_access"},
                },
            }
        )
        payload = json.loads(response["result"]["content"][0]["text"])
        self.assertIn("Never request passwords", payload["policy"])


if __name__ == "__main__":
    unittest.main()

