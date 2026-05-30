import unittest

from auction.monitor import _message_sort_key, _poll_wait_seconds, _removed_message_id


class MonitorOrderingTest(unittest.TestCase):
    def test_messages_are_sortable_by_published_at(self):
        items = [
            {"snippet": {"publishedAt": "2026-05-27T03:16:05Z", "displayMessage": "김아로미 20"}},
            {"snippet": {"publishedAt": "2026-05-27T03:16:04Z", "displayMessage": "--------낙찰선--------"}},
        ]

        sorted_messages = [item["snippet"]["displayMessage"] for item in sorted(items, key=_message_sort_key)]

        self.assertEqual(sorted_messages, ["--------낙찰선--------", "김아로미 20"])

    def test_deleted_live_chat_event_points_to_removed_message(self):
        snippet = {
            "type": "messageDeletedEvent",
            "messageDeletedDetails": {"deletedMessageId": "bid-message-1"},
        }

        self.assertEqual(_removed_message_id(snippet), "bid-message-1")

    def test_retracted_live_chat_event_points_to_removed_message(self):
        snippet = {
            "type": "messageRetractedEvent",
            "messageRetractedDetails": {"retractedMessageId": "bid-message-2"},
        }

        self.assertEqual(_removed_message_id(snippet), "bid-message-2")

    def test_idle_monitor_respects_slow_quota_saving_polling(self):
        self.assertEqual(_poll_wait_seconds(5000, 15, False), 15)

    def test_active_auction_uses_youtube_recommended_polling(self):
        self.assertEqual(_poll_wait_seconds(5000, 15, True), 5)


if __name__ == "__main__":
    unittest.main()
