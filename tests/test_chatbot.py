import os
import shutil
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_ROOT = os.path.join(REPO_ROOT, "KPN Agentic AI")
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from main import AgenticKPNChatbot  # type: ignore  # noqa: E402


class AgenticChatbotTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.sessions_dir = os.path.join(REPO_ROOT, "sessions")
        if os.path.exists(self.sessions_dir):
            shutil.rmtree(self.sessions_dir)
        self.bot = AgenticKPNChatbot()

    def tearDown(self) -> None:
        if os.path.exists(self.sessions_dir):
            shutil.rmtree(self.sessions_dir)

    def test_recommendation_flow(self) -> None:
        first_reply = self.bot.chat(
            "I need a Samsung phone under 800 euros with good camera",
            thread_id="qa-user",
        )
        self.assertIn("📱 Search Results", first_reply)

        second_reply = self.bot.chat("Compare it with iPhone 15", thread_id="qa-user")
        self.assertIn("📊 Comparison", second_reply)

        saved_state = self.bot.resume("qa-user")
        self.assertIn("messages", saved_state)
        self.assertIn("product_search", saved_state.get("results", {}))
        self.assertGreaterEqual(len(saved_state.get("messages", [])), 3)

    def test_reset_clears_state(self) -> None:
        self.bot.chat("Show me any deals", thread_id="qa-reset")
        self.assertTrue(os.path.exists(self.sessions_dir))
        self.bot.reset("qa-reset")
        saved_state = self.bot.resume("qa-reset")
        self.assertEqual(saved_state, {})


if __name__ == "__main__":
    unittest.main()
