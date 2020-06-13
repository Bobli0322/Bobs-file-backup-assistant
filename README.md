# Bobs-file-backup-assistant
This program assists in backup and maintain personal data files such as documents, pictures, and videos.

It's written in Python 3 with tkinter GUI.

A self-contained windows executable is also provided.

Please build with terminal attached because terminal is used heavily to display information.

This program is best suited for backup and maintain data files that have no duplication, like personal documents, pictures, and vidoes.
Features include:
- Backup sync
- Detects files that haven't been copied or moved for more than 2 years, and delete them and re-copy
- Finding and removing duplicated files
- Finding reused file names
- Delete all instances of specified file or folder in target directory
- Checksum comparison between two directories
- Checksum record generation and validation

Issue:
It doesn't deal with duplicated files very well.

Safety measures:
It doesn't delete any files without asking for confirmation
It doesn't copy and overwrite any files
If there is any file name conflict during copying, it just adds a suffix to the original file name and copy to the new name
When two files have same name different content, user to investigate if it's a naming conflict or a modified file
