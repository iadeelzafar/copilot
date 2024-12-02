"""
Test companion for app.py

Author: Adeel Zafar
Date: 2024-12-01
"""
import unittest
from unittest.mock import patch
from app import (
    is_palindrome,
    extract_words,
    calculate_third_vowel_cost,
    calculate_char_cost,
    calculate_word_costs,
    calculate_credits,
    fetch_report,
    process_report,
    process_message,
    process_messages,
    app,
)

class TestApp(unittest.TestCase):
    def test_is_palindrome(self):
        self.assertTrue(is_palindrome("A man a plan a canal Panama"))
        self.assertFalse(is_palindrome("Hello, World!"))

    def test_extract_words(self):
        words = extract_words("Hello, World! Isn't it great?")
        self.assertEqual(words, ["Hello", "World", "Isn't", "it", "great"])

    def test_calculate_third_vowel_cost(self):
        text = "Hello, World!"
        cost = calculate_third_vowel_cost(text)
        self.assertEqual(cost, 0.3)

    def test_calculate_char_cost(self):
        char_cost = calculate_char_cost(25)  # 25 characters
        self.assertEqual(char_cost, 1.25)  # 25 * 0.05

    def test_calculate_word_costs(self):
        words = ["Hi", "there", "amazing", "world"]
        cost = round(calculate_word_costs(words), 2)
        self.assertEqual(cost, 0.7)  # Short: 0.1, Medium: 0.2, Long: 0.3 + 0.3

    def test_calculate_credits(self):
        message_text = "Hello, amazing world!"
        credits = calculate_credits(message_text, 123)
        self.assertEqual(credits, 1)

    @patch("app.requests.get")
    def test_fetch_report(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"name": "Sample Report", "credit_cost": 10}
        report = fetch_report("report_1")
        self.assertEqual(report["name"], "Sample Report")
        self.assertEqual(report["credit_cost"], 10)

    @patch("app.fetch_report")
    def test_process_report(self, mock_fetch_report):
        mock_fetch_report.return_value = {"name": "Sample Report", "credit_cost": 10}
        report_name, credits_used = process_report("report_1", "Hello, world!", 123)
        self.assertEqual(report_name, "Sample Report")
        self.assertEqual(credits_used, 10)

    @patch("app.fetch_report")
    def test_process_report_not_found(self, mock_fetch_report):
        mock_fetch_report.return_value = None
        _, credits_used = process_report("report_1", "Hello, world!", 123)
        self.assertEqual(credits_used, 1)

    @patch("app.fetch_messages")
    @patch("app.process_message")
    def test_process_messages(self, mock_process_message, mock_fetch_messages):
        mock_fetch_messages.return_value = [{"id": 123, "timestamp": "2024-01-01T00:00:00Z", "text": "Hello, world!"}]
        mock_process_message.return_value = {
            "message_id": 123,
            "timestamp": "2024-01-01T00:00:00Z",
            "credits_used": 2.25,
        }
        messages = [{"id": 123, "timestamp": "2024-01-01T00:00:00Z", "text": "Hello, world!"}]
        result = process_messages(messages)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["credits_used"], 2.25)

    @patch("app.fetch_messages")
    def test_usage(self, mock_fetch_messages):
        mock_fetch_messages.return_value = [{"id": 123, "timestamp": "2024-01-01T00:00:00Z", "text": "Hello, world!"}]
        with app.test_client() as client:
            response = client.get("/usage")
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertIn("usage", data)
            self.assertEqual(data["usage"][0]["message_id"], 123)
            self.assertIn("timestamp", data["usage"][0])
            self.assertEqual(data["usage"][0]["credits_used"], 1)


if __name__ == "__main__":
    unittest.main()

