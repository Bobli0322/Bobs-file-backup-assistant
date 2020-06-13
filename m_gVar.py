import datetime
import time
import os

print('EXECUTING')
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

if __name__ == '__main__':#{0
    print('Module has no standalone function')
    #a = ['c:', 'user','home']
    #b = buildPath('aa', 'bb')
    #print(b)
#}0
