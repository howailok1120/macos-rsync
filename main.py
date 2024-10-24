import subprocess
import os
import sys
import shlex
import re
import time
import json

def rsync_files(source, destination, direction='one-way', delete=False, smb_user=None, smb_password=None):
    try:
        # Basic rsync command with exclusions
        command = ['rsync', '-avz', '--stats']
        
        # Add exclusions
        exclusions = [
            '--exclude=.*',  # Exclude hidden files and directories
            '--exclude=~$*',  # Exclude temporary Office files
            '--exclude=$RECYCLE.BIN',  # Exclude Recycle Bin
            '--exclude=desktop.ini',  # Exclude desktop.ini
            '--exclude=Thumbs.db'  # Exclude Thumbs.db
        ]
        command.extend(exclusions)

        # Add delete option
        if delete:
            command.append('--delete')

        # Add source and destination based on direction
        if direction == 'one-way':
            command.extend([source + '/', destination])
        elif direction == 'two-way':
            command.extend([source + '/', destination])
            # From destination back to source
            command.extend(['&&', 'rsync', '-avz', '--stats'] + exclusions + [destination + '/', source])

        # Print the command being executed (with sensitive info redacted)
        print(f"Executing command: {' '.join(shlex.quote(arg) for arg in command)}")

        # Call rsync command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Show a simple progress indicator
        print("Synchronizing: ", end='', flush=True)
        while process.poll() is None:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        print()  # New line after progress indicator

        # Capture output
        output, stderr = process.communicate()
        
        result = {
            "success": process.returncode == 0,
            "returnCode": process.returncode,
            "filesCopied": 0,
            "filesDeleted": 0,
            "totalFileSize": "0 bytes",
            "speedup": "0.00",
            "error": stderr if process.returncode != 0 else None
        }

        if result["success"]:
            files_copied = re.search(r'Number of files transferred: (\d+)', output)
            files_deleted = re.search(r'Number of deleted files: (\d+)', output)
            total_size = re.search(r'Total file size: ([\d,]+ bytes)', output)
            speedup = re.search(r'speedup is ([\d.]+)', output)
            
            if files_copied:
                result["filesCopied"] = int(files_copied.group(1))
            if files_deleted:
                result["filesDeleted"] = int(files_deleted.group(1))
            if total_size:
                result["totalFileSize"] = total_size.group(1)
            if speedup:
                result["speedup"] = speedup.group(1)

        print(json.dumps(result, indent=2))
        return result

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        return {"success": False, "error": str(e)}

def handle_smb_path(path, user, password):
    # Convert SMB path to a local mount point
    mount_point = f"/tmp/smb_mount_{os.getpid()}"
    os.makedirs(mount_point, exist_ok=True)

    # Mount the SMB share
    mount_command = f"mount -t cifs -o username={user},password={password} {path} {mount_point}"
    subprocess.run(mount_command, check=True, shell=True)

    print(f"SMB path {path} mounted successfully.")
    return mount_point

def main():
    source_path = input("Enter the source directory path: ").strip()
    destination_path = input("Enter the destination directory path: ").strip()

    smb_user = None
    smb_password = None

    if source_path.startswith('//') or source_path.startswith('\\\\'):
        smb_user = input("Enter SMB username for source: ")
        smb_password = input("Enter SMB password for source: ")
        source_path = handle_smb_path(source_path, smb_user, smb_password)

    if destination_path.startswith('//') or destination_path.startswith('\\\\'):
        if not smb_user:
            smb_user = input("Enter SMB username for destination: ")
            smb_password = input("Enter SMB password for destination: ")
        destination_path = handle_smb_path(destination_path, smb_user, smb_password)

    direction = input("Choose sync direction (one-way or two-way): ").strip().lower()
    delete = input("Delete files in the destination? (yes or no): ").strip().lower() == 'yes'

    rsync_files(source_path, destination_path, direction, delete, smb_user, smb_password)

if __name__ == "__main__":
    main()
