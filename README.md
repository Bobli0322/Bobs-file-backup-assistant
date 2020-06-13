# Bobs-file-backup-assistant
This program assists in backup and maintain personal data files such as documents, pictures, and videos.
It provides a suite of functionalities from tools like Rsync, fdupes, and md5deep.
It's specifically effective when the user wants to root out duplicated files.
If file duplication is a feature of the data, then existing tools like Rsync is much better.

It's written in Python 3 with tkinter GUI.

Most of testing was done in Windows 8.1 over a period of two years.
It has also been tested successfully a couple of times on Linux.

A self-contained windows executable is provided.

Please build with terminal attached because terminal is used heavily to display information.

This program is best suited for backup and maintain data files that have no duplication, like personal documents, pictures, and vidoes.
Features include:
- Backup sync
- Detects files that haven't been copied or moved for more than 2 years, and delete them and re-copy
- Finding and removing duplicated files (option to compare checksum)
- Finding reused file names, and prompt user to investigate
- Delete all instances of specified file or folder in target directory
- Checksum comparison between two directories
- Checksum record generation and validation

Issue:
- Backup sync and checksum record validation don't deal with duplicated files very well.
- If a file is moved at source, it's deleted and re-copied to new location at destination
- If a folder is renamed, it's deleted and re-copied at destination
- Checksum record validation sees files with same name, different checksum, different mod-time as potentially modified file,
    even if the two files are actually different files, but takes no action and require user investigation

Advantages:
- If a file is renamed at source, it's not re-copied during backup sync operation, but simply renamed at destination.
- There is extensive checksum functionality provided throughout, which is the most reliable way to compare two files.

Safety measures:
- It doesn't delete any files without asking for confirmation.
- It doesn't copy and overwrite any files.
- If there is any file name conflict during copying, it just adds a suffix to the original file name and copy to the new name.
- When two files have same name different content, user to investigate if it's a naming conflict or a modified file.
