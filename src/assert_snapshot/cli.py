"""CLI entry point for assert-snapshot."""

import sys
import click
from pathlib import Path
from .snapshot import SnapshotManager
from .formatter import format_diff, prompt_update


@click.group()
def cli():
    """Snapshot testing tool for command output."""
    pass


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--name', help='Named snapshot identifier')
@click.option('--strip-ansi', is_flag=True, help='Strip ANSI color codes')
@click.option('--timeout', type=int, default=30, help='Command timeout in seconds')
def capture(command, name, strip_ansi, timeout):
    """Capture command output as a snapshot."""
    manager = SnapshotManager()
    try:
        snapshot_name = manager.capture(
            list(command),
            name=name,
            strip_ansi=strip_ansi,
            timeout=timeout
        )
        click.echo(f"Snapshot saved: {snapshot_name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--name', help='Named snapshot identifier')
@click.option('--strip-ansi', is_flag=True, help='Strip ANSI color codes')
@click.option('--timeout', type=int, default=30, help='Command timeout in seconds')
def verify(command, name, strip_ansi, timeout):
    """Verify command output matches saved snapshot."""
    manager = SnapshotManager()
    try:
        result = manager.verify(
            list(command),
            name=name,
            strip_ansi=strip_ansi,
            timeout=timeout
        )
        if result['matches']:
            click.echo("✓ Snapshot matches")
            sys.exit(0)
        else:
            click.echo("✗ Snapshot mismatch\n")
            click.echo(format_diff(result['expected'], result['actual']))
            sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Run 'capture' first to create a snapshot.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--name', help='Named snapshot identifier')
@click.option('--strip-ansi', is_flag=True, help='Strip ANSI color codes')
@click.option('--timeout', type=int, default=30, help='Command timeout in seconds')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
def update(command, name, strip_ansi, timeout, yes):
    """Update existing snapshot with new output."""
    manager = SnapshotManager()
    try:
        result = manager.verify(
            list(command),
            name=name,
            strip_ansi=strip_ansi,
            timeout=timeout
        )
        
        if result['matches']:
            click.echo("Snapshot already matches, no update needed.")
            sys.exit(0)
        
        click.echo(format_diff(result['expected'], result['actual']))
        
        if yes or prompt_update():
            snapshot_name = manager.update(
                list(command),
                name=name,
                strip_ansi=strip_ansi,
                timeout=timeout
            )
            click.echo(f"\nSnapshot updated: {snapshot_name}")
        else:
            click.echo("Update cancelled.")
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='list')
@click.option('--pattern', help='Glob pattern to filter snapshots')
def list_snapshots(pattern):
    """List all saved snapshots."""
    manager = SnapshotManager()
    snapshots = manager.list_snapshots(pattern)
    
    if not snapshots:
        click.echo("No snapshots found.")
        return
    
    click.echo(f"Found {len(snapshots)} snapshot(s):\n")
    for snap in snapshots:
        click.echo(f"  {snap}")


def main():
    cli()


if __name__ == '__main__':
    main()
