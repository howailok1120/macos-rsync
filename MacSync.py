import os
import json
import logging
from datetime import datetime
from urllib.parse import urlparse
import socket
from smb.SMBConnection import SMBConnection
import getpass
import subprocess
import shlex
import sys
import re
import time

def setup_logging():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console.setFormatter(console_formatter)
    logging.getLogger('').addHandler(console)

def connect_to_smb(smb_url, username, password):
    parsed_url = urlparse(smb_url)
    server_name = parsed_url.hostname
    share_name = parsed_url.path.strip('/').split('/')[0]
    
    print(f"Attempting to connect to server: {server_name}")
    
    try:
        ip_address = socket.gethostbyname(server_name)
        print(f"Resolved IP address: {ip_address}")
    except socket.gaierror as e:
        print(f"Unable to resolve hostname: {e}")
        print("Please check if the hostname is correct and your DNS settings are properly configured.")
        return None, None, None, None

    try:
        conn = SMBConnection(username, password, 'local-machine', server_name, use_ntlm_v2=True)
        if conn.connect(ip_address, 139):
            print("Successfully connected to SMB server")
            return conn, share_name, '/'.join(parsed_url.path.strip('/').split('/')[1:]), ip_address
        else:
            print("Failed to connect to SMB server")
            print("Please check if the server is reachable and the SMB service is running.")
            return None, None, None, None
    except Exception as e:
        print(f"Error connecting to SMB server: {e}")
        print("This could be due to firewall settings, incorrect credentials, or server configuration.")
        return None, None, None, None

def is_smb_path(path):
    return path.lower().startswith('smb://')

def rsync_files(source, destination, direction='one-way', delete=False):
    try:
        base_command = ['rsync', '-avz', '--stats']
        exclusions = [
            '--exclude=.*',
            '--exclude=~$*',
            '--exclude=$RECYCLE.BIN',
            '--exclude=desktop.ini',
            '--exclude=Thumbs.db'
        ]
        base_command.extend(exclusions)

        if delete and direction == 'one-way':
            base_command.append('--delete')

        if direction == 'one-way':
            commands = [base_command + [source + '/', destination]]
        elif direction == 'two-way':
            commands = [
                base_command + [source + '/', destination],
                base_command + [destination + '/', source]
            ]

        result = {
            "success": True,
            "returnCode": 0,
            "filesCopied": 0,
            "filesDeleted": 0,
            "totalFileSize": "0 bytes",
            "speedup": "0.00",
            "error": None
        }

        for cmd in commands:
            print(f"Executing command: {' '.join(shlex.quote(arg) for arg in cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            print("Synchronizing: ", end='', flush=True)
            while process.poll() is None:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
            print()

            output, stderr = process.communicate()
            
            if process.returncode != 0:
                result["success"] = False
                result["returnCode"] = process.returncode
                result["error"] = stderr
                break

            files_copied = re.search(r'Number of files transferred: (\d+)', output)
            files_deleted = re.search(r'Number of deleted files: (\d+)', output)
            total_size = re.search(r'Total file size: ([\d,]+ bytes)', output)
            speedup = re.search(r'speedup is ([\d.]+)', output)
            
            if files_copied:
                result["filesCopied"] += int(files_copied.group(1))
            if files_deleted:
                result["filesDeleted"] += int(files_deleted.group(1))
            if total_size:
                result["totalFileSize"] = total_size.group(1)
            if speedup:
                result["speedup"] = speedup.group(1)

        print(json.dumps(result, indent=2))
        return result

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        return {"success": False, "error": str(e)}

def main():
    setup_logging()
    logger = logging.getLogger('')

    while True:
        # Source path
        source_mode = input("Choose source mode (1 for local path, 2 for SMB): ")
        source_conn = None
        if source_mode == "1":
            source_path = input("Enter the source directory path: ")
            if not os.path.exists(source_path):
                print("The specified local path does not exist.")
                return
        elif source_mode == "2":
            source_path = input("Enter the source SMB URL: ")
            username = input("Enter SMB username for source: ")
            password = getpass.getpass("Enter SMB password for source: ")
            source_conn, share_name, directory, ip_address = connect_to_smb(source_path, username, password)
            if not source_conn:
                print("Source connection failed. Exiting program.")
                return
            source_path = f"//{share_name}/{directory}"
        else:
            print("Invalid source mode selection. Exiting program.")
            return

        # Destination path
        dest_mode = input("Choose destination mode (1 for local path, 2 for SMB): ")
        dest_conn = None
        if dest_mode == "1":
            destination_path = input("Enter the destination directory path: ")
        elif dest_mode == "2":
            destination_path = input("Enter the destination SMB URL: ")
            username = input("Enter SMB username for destination: ")
            password = getpass.getpass("Enter SMB password for destination: ")
            dest_conn, share_name, directory, ip_address = connect_to_smb(destination_path, username, password)
            if not dest_conn:
                print("Destination connection failed. Exiting program.")
                return
            destination_path = f"//{share_name}/{directory}"
        else:
            print("Invalid destination mode selection. Exiting program.")
            return

        direction = input("Choose sync direction (one-way or two-way): ").strip().lower()
        
        delete = False
        if direction == 'one-way':
            delete = input("Delete files in the destination? (yes/no): ").strip().lower() == 'yes'
        elif direction != 'two-way':
            print("Invalid direction. Please choose 'one-way' or 'two-way'.")
            return

        result = rsync_files(source_path, destination_path, direction, delete)

        if result["success"]:
            logger.info(f"Sync completed successfully.")
            logger.info(f"Files copied: {result['filesCopied']}")
            logger.info(f"Files deleted: {result['filesDeleted']}")
            logger.info(f"Total file size: {result['totalFileSize']}")
            logger.info(f"Speedup: {result['speedup']}")
        else:
            logger.error(f"Sync failed: {result['error']}")

        if source_conn:
            source_conn.close()
        if dest_conn:
            dest_conn.close()

        another_sync = input("Do you want to perform another sync? (yes/no): ").lower()
        if another_sync != 'yes':
            break

    print("Program finished. Goodbye!")

if __name__ == "__main__":
    main()
