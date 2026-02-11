"""Tests for CLI commands and argument parsing."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil
from assert_snapshot.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create temporary directory for CLI tests."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


class TestCLI:
    def test_capture_command(self, runner, temp_dir):
        """Test capture command creates snapshot."""
        with runner.isolated_filesystem(temp=temp_dir):
            result = runner.invoke(cli, ['capture', 'echo', 'hello'])
            assert result.exit_code == 0
            assert 'Snapshot saved' in result.output
            assert Path('.snapshots').exists()

    def test_capture_with_name(self, runner, temp_dir):
        """Test capture with custom name."""
        with runner.isolated_filesystem(temp=temp_dir):
            result = runner.invoke(cli, ['capture', '--name', 'test', 'echo', 'hi'])
            assert result.exit_code == 0
            assert Path('.snapshots/test.snapshot').exists()

    def test_verify_matching(self, runner, temp_dir):
        """Test verify succeeds with matching output."""
        with runner.isolated_filesystem(temp=temp_dir):
            runner.invoke(cli, ['capture', '--name', 'test', 'echo', 'hello'])
            result = runner.invoke(cli, ['verify', '--name', 'test', 'echo', 'hello'])
            assert result.exit_code == 0
            assert '✓' in result.output

    def test_verify_mismatch(self, runner, temp_dir):
        """Test verify fails with different output."""
        with runner.isolated_filesystem(temp=temp_dir):
            runner.invoke(cli, ['capture', '--name', 'test', 'echo', 'hello'])
            result = runner.invoke(cli, ['verify', '--name', 'test', 'echo', 'bye'])
            assert result.exit_code == 1
            assert '✗' in result.output

    def test_verify_missing_snapshot(self, runner, temp_dir):
        """Test verify fails when snapshot doesn't exist."""
        with runner.isolated_filesystem(temp=temp_dir):
            result = runner.invoke(cli, ['verify', '--name', 'missing', 'echo', 'hi'])
            assert result.exit_code == 1
            assert 'Error' in result.output

    def test_update_with_yes_flag(self, runner, temp_dir):
        """Test update command with --yes flag."""
        with runner.isolated_filesystem(temp=temp_dir):
            runner.invoke(cli, ['capture', '--name', 'test', 'echo', 'old'])
            result = runner.invoke(cli, ['update', '--yes', '--name', 'test', 'echo', 'new'])
            assert result.exit_code == 0

    def test_strip_ansi_flag(self, runner, temp_dir):
        """Test --strip-ansi flag works."""
        with runner.isolated_filesystem(temp=temp_dir):
            result = runner.invoke(cli, ['capture', '--strip-ansi', 'echo', 'test'])
            assert result.exit_code == 0

    def test_timeout_option(self, runner, temp_dir):
        """Test --timeout option is accepted."""
        with runner.isolated_filesystem(temp=temp_dir):
            result = runner.invoke(cli, ['capture', '--timeout', '5', 'echo', 'test'])
            assert result.exit_code == 0

    def test_no_command_error(self, runner):
        """Test error when no command provided."""
        result = runner.invoke(cli, ['capture'])
        assert result.exit_code != 0
