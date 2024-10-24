# File Synchronization Script

This Python script provides a simple way to synchronize files between directories, including support for SMB (Server Message Block) connections on macOS and Linux. It also includes a version for Windows.

## Features

- One-way or two-way synchronization
- Option to delete files in the destination that are not in the source (one-way only)
- Support for SMB connections with username and password authentication (macOS/Linux)
- Excludes hidden and system files by default

## Requirements

- Python 3.x
- rsync
  - **macOS/Linux**: rsync is typically pre-installed.
  - **Windows**: Install rsync via WSL, Cygwin, or another method.

## Usage

### macOS/Linux

1. Run the script:

   ```
   python MacSync.py
   ```

2. Follow the prompts to enter:
   - Source directory path
   - Destination directory path
   - Synchronization direction (one-way or two-way)
   - Whether to delete files in the destination (yes or no, one-way only)
   - SMB username and password (if using SMB paths)

### Windows

1. Ensure rsync is installed and accessible on your system.

2. Run the script:

   ```
   python WinSync.py
   ```

3. Follow the prompts to enter:
   - Source directory path
   - Destination directory path
   - Synchronization direction (one-way or two-way)
   - Whether to delete files in the destination (yes or no, one-way only)

## SMB Support (macOS/Linux only)

To use SMB paths, enter them in the format:

```
//server/share/path
```

The script will prompt for SMB username and password if an SMB path is detected.

## Note

- This script requires root privileges to mount SMB shares on macOS/Linux. Always use caution when running scripts with elevated permissions.
- The delete option is not supported for two-way synchronization to prevent data loss.

## License

[MIT License](https://opensource.org/licenses/MIT)
