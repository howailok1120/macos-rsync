import subprocess
import os

def rsync_files(source, destination, direction='one-way', delete=False, smb_user=None, smb_password=None):
    try:
        # Check if source or destination is an SMB path
        is_smb_source = source.startswith('//') or source.startswith('\\\\')
        is_smb_dest = destination.startswith('//') or destination.startswith('\\\\')

        if is_smb_source or is_smb_dest:
            # Handle SMB connection
            if not smb_user or not smb_password:
                raise ValueError("SMB connection requires username and password")

            if is_smb_source:
                source = handle_smb_path(source, smb_user, smb_password)
            if is_smb_dest:
                destination = handle_smb_path(destination, smb_user, smb_password)

        # Basic rsync command
        command = ['rsync', '-avz']

        # Add delete option
        if delete:
            command.append('--delete')

        # Add source and destination based on direction
        if direction == 'one-way':
            command.extend([source, destination])
        elif direction == 'two-way':
            command.extend([source, destination])
            # From destination back to source
            command.extend(['&&', 'rsync', '-avz'] + [destination, source])

        # Call rsync command
        subprocess.run(command, check=True, shell=True)
        print("File synchronization successful!")
    except subprocess.CalledProcessError as e:
        print(f"File synchronization failed: {e}")
    except ValueError as e:
        print(f"Error: {e}")

def handle_smb_path(path, user, password):
    # Convert SMB path to a local mount point
    mount_point = f"/tmp/smb_mount_{os.getpid()}"
    os.makedirs(mount_point, exist_ok=True)

    # Mount the SMB share
    mount_command = f"mount -t cifs -o username={user},password={password} {path} {mount_point}"
    subprocess.run(mount_command, check=True, shell=True)

    return mount_point

def main():
    source_path = input("Enter the source directory path: ")
    destination_path = input("Enter the destination directory path: ")

    direction = input("Choose sync direction (one-way or two-way): ").strip().lower()
    delete = input("Delete files in the destination? (yes or no): ").strip().lower() == 'yes'

    smb_user = None
    smb_password = None
    if source_path.startswith('//') or destination_path.startswith('//'):
        smb_user = input("Enter SMB username: ")
        smb_password = input("Enter SMB password: ")

    rsync_files(source_path, destination_path, direction, delete, smb_user, smb_password)

if __name__ == "__main__":
    main()
