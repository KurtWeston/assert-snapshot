"""Tests for snapshot manager core functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil
from assert_snapshot.snapshot import SnapshotManager


@pytest.fixture
def temp_snapshot_dir():
    """Create temporary snapshot directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def manager(temp_snapshot_dir):
    """Create SnapshotManager with temp directory."""
    return SnapshotManager(snapshot_dir=temp_snapshot_dir)


class TestSnapshotManager:
    def test_capture_simple_command(self, manager):
        """Test capturing output from simple command."""
        snapshot_name = manager.capture(['echo', 'hello'])
        assert snapshot_name.endswith('.snapshot')
        snapshot_path = manager.snapshot_dir / snapshot_name
        assert snapshot_path.exists()
        assert 'hello' in snapshot_path.read_text()

    def test_capture_with_custom_name(self, manager):
        """Test capturing with custom snapshot name."""
        snapshot_name = manager.capture(['echo', 'test'], name='custom')
        assert snapshot_name == 'custom.snapshot'
        assert (manager.snapshot_dir / 'custom.snapshot').exists()

    def test_verify_matching_snapshot(self, manager):
        """Test verification succeeds when output matches."""
        manager.capture(['echo', 'hello'], name='test')
        result = manager.verify(['echo', 'hello'], name='test')
        assert result['matches'] is True

    def test_verify_mismatched_snapshot(self, manager):
        """Test verification fails when output differs."""
        manager.capture(['echo', 'hello'], name='test')
        result = manager.verify(['echo', 'goodbye'], name='test')
        assert result['matches'] is False
        assert 'hello' in result['expected']
        assert 'goodbye' in result['actual']

    def test_verify_missing_snapshot(self, manager):
        """Test verification raises error for missing snapshot."""
        with pytest.raises(FileNotFoundError):
            manager.verify(['echo', 'test'], name='nonexistent')

    def test_strip_ansi_codes(self, manager):
        """Test ANSI code stripping."""
        text = '\x1b[31mred\x1b[0m'
        stripped = manager._strip_ansi(text)
        assert stripped == 'red'
        assert '\x1b' not in stripped

    def test_invalid_snapshot_name_path_traversal(self, manager):
        """Test validation rejects path traversal attempts."""
        with pytest.raises(ValueError, match='path separators'):
            manager.capture(['echo', 'test'], name='../evil')

    def test_invalid_snapshot_name_dot_prefix(self, manager):
        """Test validation rejects names starting with dot."""
        with pytest.raises(ValueError, match='cannot start'):
            manager.capture(['echo', 'test'], name='.hidden')

    def test_command_timeout(self, manager):
        """Test timeout handling for long-running commands."""
        with pytest.raises(TimeoutError, match='timed out'):
            manager.capture(['sleep', '10'], timeout=1)

    def test_command_not_found(self, manager):
        """Test error handling for nonexistent commands."""
        with pytest.raises(FileNotFoundError, match='Command not found'):
            manager.capture(['nonexistent_command_xyz'])

    def test_empty_command(self, manager):
        """Test error handling for empty command."""
        with pytest.raises(ValueError, match='cannot be empty'):
            manager.capture([])

    def test_generate_name_sanitization(self, manager):
        """Test command name sanitization."""
        name = manager._generate_name(['echo', 'hello@world!'])
        assert '@' not in name
        assert '!' not in name
        assert name.endswith('.snapshot')

    def test_update_snapshot(self, manager):
        """Test updating existing snapshot."""
        manager.capture(['echo', 'old'], name='test')
        manager.update(['echo', 'new'], name='test')
        result = manager.verify(['echo', 'new'], name='test')
        assert result['matches'] is True

    def test_list_snapshots(self, manager):
        """Test listing all snapshots."""
        manager.capture(['echo', 'a'], name='snap1')
        manager.capture(['echo', 'b'], name='snap2')
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 2
        assert any('snap1' in s for s in snapshots)

    def test_delete_snapshot(self, manager):
        """Test deleting snapshot."""
        manager.capture(['echo', 'test'], name='todelete')
        manager.delete_snapshot('todelete')
        with pytest.raises(FileNotFoundError):
            manager.verify(['echo', 'test'], name='todelete')
