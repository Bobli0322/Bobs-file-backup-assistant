import datetime
#from datetime import datetime
import time
import os, shutil, filecmp

#- Use filecmp for file content comparison
#- Make this a module with compareLocal and compareGlobal functions
#       localCompare compare only files within a folder
#       globalCompare compares across folders
#- Implement backupCopy and compareNcopy functions
#- Delete duplicates in globalCompare based on file creation and access time
#- For fileBackup function Remove files and folders in dstDir but not in srcDir
#- Optimise compareNcopy by iterate through files only once to get
#       what is same and different between 2 lists of files
#-
#       Generate a dummy directory to do a pre-op test to verify program
#        function
#
#       Separating analysing data from processing data(filing())
#       Using global variables to communicate results
#
#       Using shutil.copytree function to copy entire dir tree
#       for src dir that not in dst 
#       instead of previously using compareNcopy to copy each file
#
#       When comparison operation determines two files have same content
#       but different filename
#       change the dst filename to match src filename
#
#       When comparison operation determines two files have same content
#       If the DST file's Creation Date is older than 2 years,
#       Delete the DST file and copy the SRC file over again
#       for data retention purpose.
#       When files are copied, the DST file must update its creation date
#       Copy and replace function in Windows does not update file creation date
#       thus the file must be deleted first then copied.
#
#       Before sync operation begin, generate a report
#       of what is to be renamed, copied and removed
#       then ask user for confirmation
#
#       Option to only copy src files that are not in dst
#       (No deletion of dst files) (Additive sync)(disregards aged files)
#
#       Duplicated file removal compares all files regardless of filename or extension
#
#       Checking for aged file use both creation date and access date
#       because when files move from one drive to another, only access date change
#
#       When removing duplicated files, remove the older one
#       use both file creation time and file access time
#       list out all four values, find the biggest value (latest datetime value)
#       file of which the biggest value belongs to is kept
#       newest file has either its creation or access time being the latest time
#
#       filecmp.clear_cache() after function finishes
#
#       do checksum to verify data integrity
#       checksum assume that src and dst are synced already
#
#       Have rename only sync mode (for use Rsync)
#
#       Create file compare function to allow choose compare method
#       filecmp.cmp or hashlib
#
#       Create hasher function to switch between hashing methods
#
#       add directories to exclude.
#
#       Have a feature to detect reused file names
#
#       Function to select a dir to generate a file that contains data checksum + filename + mod time table
#           - include feature to merge with an existing file
#       Function to validate this checksum table against checksum computed from selected dir
#           - Computed value found in table + same file name = same file
#           - Computed value found in table + different file name = renamed file (Update table)
#           - Computed value not found in table + different file name = new file (Update table)
#           - Computed value not found in table + same name + different mod time = modifed file (Update table)
#           - Computed value not found in table + same name + same mod time = corrupted file
#              (This feature only update the CSV record file, does not copy or remove actual file)
#           - include feature to detect duplicates in an existing record file
#
#       filecmp.cmp needs to include 'shallow=False' option for file content comparison
#       otherwise filecmp.cmp only compare file metadata (os.stat)
#
#       allowing program to detect duplicated file and sync
#
#       Detect which OS program is running on and adapt
#
#       check file age base on creation and access time and report
#       - copied file update creation time
#       - moved file update access time
#
#       improve backup sync speed by using mixture of comparison methods
#           - compare file metadata (size, modification date)
#           - compare file name
#           - compare file content (byte by byte)
#
#        Checksum recording now can handle duplicated files
#           but it takes multiple iterations of analysis and update to complete
#           impact is low because all it's doing is updating csv files

#Limitations
#1. Checksum record validation disallow duplicated files

#It's better to put immutable here
print('Executing')
cwd = os.getcwd()
delim = ''
if cwd[0] == '/':
        delim = '/'
elif cwd[1] == ':' and cwd[2] == '\\':
        delim = '\\'

now = datetime.datetime.now()
nowYr = now.year #assign current year(int)

gb_conv = 9.31e-10
mb_conv = 9.537e-7

cmp_Mode = 0
hash_Mode = 'sha256'
thumbs = 'Thumbs.db'
pycache = '__pycache__'

#Global variable for sync function
totalSrcFile = 0
totalDstFile = 0
totalSrcCopy = 0
totalDstRemove = 0
totalDstRename = 0
agedFile = 0
dstRM_size = 0
srcCP_size = 0
net_sync_size = 0

#mkdirList= []
rmtreeList = []
copytreeList = []
renameList = []
removeList = []
checkNcopyList = []
agedFileList = []

#Global variable for duplicated file removal
dupFileList = []
dupFileRM = 0

#Global variable for folder file removal
delDFList = []
delCount = 0

#Global variable for checksum validation
genTable = []
recordTable = []
recordDir = ''
csvName0 = ''

#code profiling
profile1 = []
profile2 = []
profile3 = []
profile1Num = 0
profile2Num = 0
profile3Num = 0

if __name__ == '__main__':#{0
    print('Module has no standalone function')
    #a = ['c:', 'user','home']
    #b = buildPath('aa', 'bb')
    #print(b)
#}0
