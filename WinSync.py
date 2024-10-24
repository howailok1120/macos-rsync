import os
import subprocess
import shlex

def rsync_files(source, destination, direction='one-way', delete=False):
    try:
        # Convert paths to use forward slashes for rsync compatibility
        source = source.replace('\\', '/')
        destination = destination.replace('\\', '/')

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
            command.extend([source, destination])
        elif direction == 'two-way':
            command.extend([source, destination])
            command.extend([destination, source])

        # Print the command being executed
        print(f"Executing command: {' '.join(shlex.quote(arg) for arg in command)}")

        # Call rsync command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, stderr = process.communicate()

        if process.returncode == 0:
            print("File synchronization successful!")
        else:
            print(f"File synchronization failed with return code {process.returncode}")
            print("Error output:")
            print(stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    source_path = input("Enter the source directory path: ").strip()
    destination_path = input("Enter the destination directory path: ").strip()

    direction = input("Choose sync direction (one-way or two-way): ").strip().lower()
    delete = input("Delete files in the destination? (yes or no): ").strip().lower() == 'yes'

    rsync_files(source_path, destination_path, direction, delete)

if __name__ == "__main__":
    main()