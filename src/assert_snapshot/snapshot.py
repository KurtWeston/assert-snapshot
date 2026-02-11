"""Core snapshot capture, storage, and comparison logic."""

import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict


class SnapshotManager:
    def __init__(self, snapshot_dir: str = ".snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)
    
    def _validate_name(self, name: str) -> None:
        """Validate snapshot name to prevent path traversal."""
        if '/' in name or '\\' in name or '..' in name:
            raise ValueError(
                "Invalid snapshot name: cannot contain path separators or '..'"
            )
        if name.startswith('.'):
            raise ValueError("Invalid snapshot name: cannot start with '.'")
    
    def _generate_name(self, command: List[str], name: Optional[str] = None) -> str:
        """Generate snapshot filename from command or use provided name."""
        if name:
            self._validate_name(name)
            return f"{name}.snapshot"
        
        cmd_str = '_'.join(command[:3])
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', cmd_str)
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        return f"{sanitized}.snapshot"
    
    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _run_command(
        self,
        command: List[str],
        timeout: int = 30,
        strip_ansi: bool = False
    ) -> str:
        """Execute command and capture output safely."""
        if not command:
            raise ValueError("Command cannot be empty")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            output = result.stdout + result.stderr
            
            if strip_ansi:
                output = self._strip_ansi(output)
            
            return output
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        except FileNotFoundError:
            raise FileNotFoundError(f"Command not found: {command[0]}")
    
    def capture(
        self,
        command: List[str],
        name: Optional[str] = None,
        strip_ansi: bool = False,
        timeout: int = 30
    ) -> str:
        """Capture command output and save as snapshot."""
        output = self._run_command(command, timeout, strip_ansi)
        snapshot_name = self._generate_name(command, name)
        snapshot_path = self.snapshot_dir / snapshot_name
        
        snapshot_path.write_text(output, encoding='utf-8')
        return snapshot_name
    
    def verify(
        self,
        command: List[str],
        name: Optional[str] = None,
        strip_ansi: bool = False,
        timeout: int = 30
    ) -> Dict[str, any]:
        """Verify command output matches saved snapshot."""
        snapshot_name = self._generate_name(command, name)
        snapshot_path = self.snapshot_dir / snapshot_name
        
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_name}")
        
        expected = snapshot_path.read_text(encoding='utf-8')
        actual = self._run_command(command, timeout, strip_ansi)
        
        return {
            'matches': expected == actual,
            'expected': expected,
            'actual': actual,
            'snapshot_name': snapshot_name
        }
    
    def update(
        self,
        command: List[str],
        name: Optional[str] = None,
        strip_ansi: bool = False,
        timeout: int = 30
    ) -> str:
        """Update existing snapshot with new output."""
        return self.capture(command, name, strip_ansi, timeout)
    
    def list_snapshots(self, pattern: Optional[str] = None) -> List[str]:
        """List all snapshots, optionally filtered by glob pattern."""
        if pattern:
            snapshots = self.snapshot_dir.glob(pattern)
        else:
            snapshots = self.snapshot_dir.glob('*.snapshot')
        
        return sorted([s.name for s in snapshots])
