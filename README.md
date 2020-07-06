# Bobs-file-backup-assistant
This program assists in backup and maintain personal data files such as documents, pictures, and videos.
It provides a suite of functionalities from tools like Rsync, fdupes, and md5deep.

It's written in Python 3 with tkinter GUI.\
A **note** on file comparison function.\
Filecmp.cmp(src,dst,shallow=False) is practically as good as compare checksums\
If shallow option is omitted then it defaults to True which isn't totally reliable\
because it only compares file metadata like file size and modification time.\
So two separate files have same size and modification time, even if file name and content are different,\
the default filecmp.cmp function (shallow=True) still returns True.\
The downside is for large files, it takes a long time to compare file content.

Tested on Windows 8.1.\
May also work on Linux.

A self-contained windows executable is provided.

Please build with terminal attached because terminal is used heavily to display information.

This program is best suited for backup and maintain data files that have no duplication, like personal documents, pictures, and vidoes.
Features include:
- Backup sync
- Finding and removing duplicated files (option to compare checksum)
- Finding reused file names, and prompt user to investigate
- Delete all instances of specified file or folder in target directory
- Checksum comparison between two directories
- Checksum record generation, validation, and update
- Check age of files base on creation and access time and report

**Limitations:**
- In certain situations like if there are lots of renamed files, or files that have same size and modification time but different content,
  the backup sync file comparison process could take a long time if file sizes are large because in this case, the program compares files by its content
- Checksum record validation disallow duplicated files
- Checksum recording doesn't work in Linux
- If a file is moved at source, it's deleted and re-copied to new location at destination
- If a folder is renamed, it's deleted and re-copied at destination

**Advantages:**
- If a file is renamed at source, it's not re-copied during backup sync operation, but simply renamed at destination.
- There is extensive checksum functionality provided throughout.

**Safety measures:**
- It doesn't delete any files without asking for confirmation.
- It doesn't copy and overwrite any files.
- If there is any file name conflict during copying, it just adds a suffix to the original file name and copy to the new name.
- When multiple files use the same name, user to investigate if it's a naming conflict or a modified file.
