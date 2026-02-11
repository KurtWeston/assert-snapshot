# assert-snapshot

Simple snapshot testing tool that captures command output and diffs against saved snapshots

## Features

- Capture stdout and stderr from any command or executable
- Store snapshots in .snapshots/ directory with human-readable filenames
- Generate colored unified diff output showing additions/deletions
- Interactive update mode to accept or reject snapshot changes
- Support for named snapshots to test multiple outputs per command
- Exit with non-zero code when snapshots don't match (CI-friendly)
- Automatic snapshot directory creation and management
- Strip ANSI color codes option for consistent comparisons
- Timeout support for long-running commands
- Glob pattern support for updating multiple snapshots at once

## How to Use

Use this project when you need to:

- Quickly solve problems related to assert-snapshot
- Integrate python functionality into your workflow
- Learn how python handles common patterns

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/assert-snapshot.git
cd assert-snapshot

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python

## Dependencies

- `click`
- `colorama`
- `difflib`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
