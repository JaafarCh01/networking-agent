import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.sender import send_linkedin_message # Assuming sender.py is in src

class TestSender(unittest.TestCase):

    @patch('src.sender.sync_playwright')
    def test_send_linkedin_message_success(self, mock_sync_playwright):
        """
        Test that send_linkedin_message returns True on success.
        """
        # Mock Playwright's context manager and objects
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Simulate successful execution (no exceptions)
        result = send_linkedin_message(mock_playwright, "http://linkedin.com/in/testprofile", "Test message")

        self.assertTrue(result)
        mock_page.goto.assert_called()
        mock_page.fill.assert_called()
        mock_page.click.assert_called()

    @patch('src.sender.sync_playwright')
    def test_send_linkedin_message_failure(self, mock_sync_playwright):
        """
        Test that send_linkedin_message returns False on failure.
        """
        # Mock Playwright to raise an exception
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Simulate a failure during the process
        mock_page.click.side_effect = Exception("Test exception")

        result = send_linkedin_message(mock_playwright, "http://linkedin.com/in/testprofile", "Test message")

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
