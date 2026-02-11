"""Tests for diff formatting and interactive prompts."""

import pytest
from unittest.mock import patch
from assert_snapshot.formatter import format_diff, prompt_update


class TestFormatter:
    def test_format_diff_additions(self):
        """Test diff formatting shows additions in green."""
        expected = 'line1\nline2'
        actual = 'line1\nline2\nline3'
        diff = format_diff(expected, actual)
        assert '+line3' in diff
        assert '\x1b[32m' in diff  # Green color code

    def test_format_diff_deletions(self):
        """Test diff formatting shows deletions in red."""
        expected = 'line1\nline2\nline3'
        actual = 'line1\nline3'
        diff = format_diff(expected, actual)
        assert '-line2' in diff
        assert '\x1b[31m' in diff  # Red color code

    def test_format_diff_no_changes(self):
        """Test diff formatting with identical content."""
        text = 'same\ncontent'
        diff = format_diff(text, text)
        assert diff == ''  # No diff output

    def test_format_diff_context_lines(self):
        """Test diff includes context lines."""
        expected = 'a\nb\nc'
        actual = 'a\nX\nc'
        diff = format_diff(expected, actual)
        assert '@@' in diff  # Hunk header
        assert '\x1b[36m' in diff  # Cyan color for hunk

    @patch('builtins.input', return_value='y')
    def test_prompt_update_yes(self, mock_input):
        """Test prompt accepts 'y' response."""
        result = prompt_update()
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_prompt_update_no(self, mock_input):
        """Test prompt rejects 'n' response."""
        result = prompt_update()
        assert result is False

    @patch('builtins.input', return_value='')
    def test_prompt_update_default_no(self, mock_input):
        """Test prompt defaults to no on empty input."""
        result = prompt_update()
        assert result is False

    @patch('builtins.input', side_effects=['invalid', 'y'])
    def test_prompt_update_retry(self, mock_input):
        """Test prompt retries on invalid input."""
        result = prompt_update()
        assert result is True
