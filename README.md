# File Synchronization Script

This Python script provides a simple way to synchronize files between directories, including support for SMB (Server Message Block) connections.

## Features

- One-way or two-way synchronization
- Option to delete files in the destination that are not in the source
- Support for SMB connections with username and password authentication

## Requirements

- Python 3.x
- rsync
- cifs-utils (for SMB support)

## Usage

1. Run the script:

   ```
   python main.py
   ```

2. Follow the prompts to enter:
   - Source directory path
   - Destination directory path
   - Synchronization direction (one-way or two-way)
   - Whether to delete files in the destination (yes or no)
   - SMB username and password (if using SMB paths)

## SMB Support

To use SMB paths, enter them in the format:

```
//server/share/path
```

The script will prompt for SMB username and password if an SMB path is detected.

## Note

This script requires root privileges to mount SMB shares. Always use caution when running scripts with elevated permissions.

## License

[MIT License](https://opensource.org/licenses/MIT)
