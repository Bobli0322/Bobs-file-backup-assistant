import stat
import shutil
import sys
import filecmp
from m_gVar import * #contains global variables
import m_FileOps1_1 as fOps
import m_class_entity as entityc
import m_functions as func

#Ver 1.0
#Ver 1.1 Use filecmp for file content comparison
#Ver 1.2 Make this a module with compareLocal and compareGlobal functions
#       localCompare compare only files within a folder
#       globalCompare compares across folders
#Ver 1.3 Implement backupCopy and compareNcopy functions
#Ver 1.4 Delete duplicates in globalCompare based on file access time
#Ver 1.5 For fileBackup function Remove files and folders in dstDir but not in srcDir
#Ver 1.6 Optimise compareNcopy by iterate through files only once to get
#       what is same and different between 2 lists of files
#Ver 1.7
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

#Known limitations
#1. Validation of checksum record disallow duplicated files

def fCompare(f1, f2, method):#{0
    if method == 0:#{1
        #filecmp shallow=True - compare file metadata(os.stat)
        #filecmp shallow=False - compare file content (Recommanded)
        return filecmp.cmp(f1, f2, shallow=False)
    #}1
    elif method == 1:#{1
        fileHash1 = func.hasher(f1, False, hash_Mode)
        fileHash2 = func.hasher(f2, False, hash_Mode)
        if fileHash1 == fileHash2:#{2
            return True
        #}2
        else:#{2
            return False
        #}2
    #}1
#}0
#Generate checksum for each and compare them one at a time
#instead of whole list compare
def validate(srcDir, dstDir, exlSrcDir, exlDstDir):#{0
    srcList = []
    dstList = []
    print('Checksum...')
    if type(srcDir) is list:#{1
        for i in srcDir:#{2
            p1 = func.buildPath(i[0], i[2], delim)
            p2 = func.buildPath(i[1], i[3], delim)
            fileHash1 = func.hasher(p1, False, hash_Mode)
            fileHash2 = func.hasher(p2, False, hash_Mode)
            if fileHash1 != fileHash2:#{3
                print('Checksum: File checksum failed')
                return 0
            #}3
        #}2
        print('Checksum: File checksum passed')
        return 1
    #}1
    else:#{1
        entity0 = entityc.entity(srcDir, dstDir, delim)
        srcDir = entity0.srcDir
        dstDir = entity0.dstDir
        esList = listExl(exlSrcDir)
        edList = listExl(exlDstDir)
        print('Source directories to exclude:')
        print(esList)
        print('Destination directories to exclude:')
        print(edList)
        isExlSrc = False
        isExlDst = False
        
        for pf, sf, fn in os.walk(srcDir):#{2
            for esDir in esList:#{3
                if esDir in pf:#{4
                    isExlSrc = True
                #}4
            #}3
            if isExlSrc == True:#{3
                isExlSrc = False
                continue
            #}3
            else:#{3
                for f in fn:#{4
                    tempStr = func.buildPath(pf, f, delim)
                    srcList.append(tempStr)
                #}4
            #}3
        #}2
        for pf, sf, fn in os.walk(dstDir):#{2
            for edDir in edList:#{3
                if edDir in pf:#{4
                    isExlDst = True
                #}4
            #}3
            if isExlDst == True:#{3
                isExlDst = False
                continue
            #}3
            else:#{3
                for f in fn:#{4
                    tempStr = func.buildPath(pf, f, delim)
                    dstList.append(tempStr)
                #}4
            #}3
        #}2    
        if len(srcList) != len(dstList):#{2
            print('Checksum: directory checksum failed')
            return 0
        #}2
        else:#{2
            for i in range(len(srcList)):#{3
                p1 = srcList[i]
                p2 = dstList[i]
                
                tStr1 = p1.replace(srcDir,'')
                strHash1 = func.hasher(tStr1, True, hash_Mode)
                fileHash1 = func.hasher(p1, False, hash_Mode)
                
                tStr2 = p2.replace(dstDir,'')
                strHash2 = func.hasher(tStr2, True, hash_Mode)
                fileHash2 = func.hasher(p2, False, hash_Mode)
                
                if strHash1 != strHash2 or fileHash1 != fileHash2:#{4
                    print('Checksum: directory checksum failed')
                    return 0
                #}4
            #}3
        #}2
        print('Checksum: directory checksum passed')
        return 1
    #}1
#}0
#remove targeted dir and file
def delete(isFolder):#{0
    global delCount
    delCount = 0
    print('Removing target..')
    if isFolder == True:#{1
        for tarDir in delDFList:#{2
            shutil.rmtree(tarDir, onerror=remove_readonly)
            delCount = delCount + 1
        #}2
    #}1
    else:#{1
        for tarFile in delDFList:#{2
            try:#{3
                os.remove(tarFile)
                delCount = delCount + 1
            #}3
            except OSError:#{3
                continue
            #}3
        #}2
    #}1
    delDFList.clear()
    print('Completed, ' + str(delCount) + ' instances removed.\n')
#}0
#remove duplicated files
def dup():#{0
    global dupFileRM
    dupFileRM = 0
    print('Removing duplicated files...')
    for dp in dupFileList:#{1
        try:#{2
            os.remove(dp)
            dupFileRM = dupFileRM + 1
        #}2
        except OSError:#{2
            continue
        #}2
    #}1
    dupFileList.clear()
    print('Completed, ' + str(dupFileRM) + ' files removed.\n')
#}0

#Carry out filing operations
def filing(iMode, iCS):#{0
    global totalSrcFile
    global totalDstFile
    global totalSrcCopy
    global totalDstRemove
    global totalDstRename
    #totalSrcFile = 0
    #totalDstFile = 0
    totalSrcCopy = 0
    totalDstRemove = 0
    totalDstRename = 0
    
    if iMode == 3:#{1
        print('Mirror Syncing...')
    #}1
    elif iMode == 1:#{1
        print('Additive Syncing...')
    #}1
    elif iMode == 2:#{1
        print('File name Syncing...')
    #}1        
    if iMode == 3:#{1
        for tf in rmtreeList:#{2
            #print('Folder remove ' + tf)
            temp = sum([len(cc) for aa, bb, cc in os.walk(tf)])
            totalDstRemove = totalDstRemove + temp
            shutil.rmtree(tf, onerror=remove_readonly)
        #}2
        for rmf in removeList:#{2
            try:#{3
                os.remove(rmf)
                totalDstRemove = totalDstRemove + 1
                #print('Remove: ' + rmf)
            #}3
            except OSError:#{3
                continue
            #}3
        #}2
    #}1
    if iMode == 3 or iMode == 2:#{1
        for rnf in renameList:#{2
            try:#{3
                os.rename(rnf[0], rnf[1])
                totalDstRename = totalDstRename + 1
                #print('Rename: ' + rnf[0] + ' -> ' + rnf[1])
            #}3
            except OSError:#{3
                continue
            #}3
        #}2
    #}1
    if iMode == 3 or iMode == 1:#{1
        #copytree function create dst directory path automatically
        for cpt in copytreeList:#{2
            shutil.copytree(cpt[0], cpt[1])
            temp = sum([len(cc) for aa, bb, cc in os.walk(cpt[1])])
            totalSrcCopy = totalSrcCopy + temp
        #}2
        for cpf in checkNcopyList:#{2
            tempDst = func.buildPath(cpf[1], cpf[3], delim)
            #print('Folder copy ' + cpf[0] + ' to ' + cpf[1])
            if fOps.checkNcopy(cpf[0], cpf[1], cpf[2], cpf[3], delim) == True:#{3
                totalSrcCopy = totalSrcCopy + 1
            #}3
        #}2
    #}1
    #Checksum for transfered files
    if (iMode == 1 or iMode == 3) and iCS == 1:#{1
        if len(checkNcopyList) != 0:#{2
            v1 = validate(checkNcopyList, '', '', '')
        #}2
        else:#{2
            v1 = 3
        #}2
        if len(copytreeList) != 0:#{2
            for i in copytreeList:#{3
                v2 = validate(i[0], i[1], '', '')
                if v2 == 0:#{4
                    break
                #}4
            #}3
        #}2
        else:#{2
            v2 = 3
        #}2
        v3 = v1 + v2
        if v3 == 2 or v3 == 4:#{2
            print('Checksum: Transfered file checksum passed')
        #}2
        elif v3 == 6:#{2
            print('Checksum: Nothing to validate')
        #}2
        else:#{2
            print('Checksum: Transfered file checksum failed')
        #}2
    #}1   
    rmtreeList.clear()
    copytreeList.clear()
    renameList.clear()
    removeList.clear()
    checkNcopyList.clear()
    print('Total source file count: ' + str(totalSrcFile))
    print('Total destination file count: ' + str(totalDstFile))
    print('Total source file copied: ' + str(totalSrcCopy))
    print('Total destination file removed: ' + str(totalDstRemove))
    print('Total destination file renamed: ' + str(totalDstRename))
    if iMode == 3 and totalSrcFile == totalDstFile - totalDstRemove + totalSrcCopy:#{1
        print("No issue encountered with mirroring")
    #}1
    '''
    else:#{1
        print("Issue encountered, please investigate")
    #}1
    '''
    print('Sync finished\n')
#}0

def sync_size_est(dst_drive):#{0
    global dstRM_size
    global srcCP_size
    global net_sync_size
    dstRM_size = 0
    srcCP_size = 0
    net_sync_size = 0
    
    dst_stat = shutil.disk_usage(dst_drive)
    dst_total = dst_stat.total #int in bytes
    dst_free = dst_stat.free #int in bytes
    dst_total_gb = dst_total*gb_conv #int in GB
    dst_free_gb = dst_free*gb_conv #int in GB
    print('Destination drive capacity:')
    print('Total: ' + str(dst_total_gb) +'GB' + ' Free: ' + str(dst_free_gb) + 'GB')
    
    if len(removeList) != 0:#{1
        #print(removeList)
        for f in removeList:#{2
            rmFsize = os.path.getsize(f)
            dstRM_size = dstRM_size + rmFsize
        #}2
    #}1
    if len(rmtreeList) != 0:#{1
        for f in rmtreeList:#{2
            for d, sd, fs in os.walk(f):#{3
                for fn in fs:#{4
                    fp = func.buildPath(d, fn, delim)
                    fp_size = os.path.getsize(fp)
                    dstRM_size = dstRM_size + fp_size
                #}4
            #}3
        #}2
    #}1
    if len(checkNcopyList) != 0:#{1
        #print(checkNcopyList)
        for f in checkNcopyList:#{2
            fp = func.buildPath(f[0], f[2], delim)
            cpFsize = os.path.getsize(fp)
            srcCP_size = srcCP_size + cpFsize
        #}2
    #}1
    if len(copytreeList) != 0:#{1
        for f in copytreeList:#{2
            fp = f[0]
            for d, sd, fs in os.walk(fp):#{3
                for fn in fs:#{4
                    fp = func.buildPath(d, fn, delim)
                    fp_size = os.path.getsize(fp)
                    srcCP_size = srcCP_size + fp_size
                #}4
            #}3
        #}2
    #}1
    net_sync_size = srcCP_size - dstRM_size
    srcCP_size_gb = srcCP_size*gb_conv
    dstRM_size_gb = dstRM_size*gb_conv
    net_sync_size_gb = net_sync_size*gb_conv
    if srcCP_size_gb < 1:#{1
        srcCP_size_mb = srcCP_size*mb_conv
        print('Files to copy: ' + str(srcCP_size_mb) + 'MB')
    #}1
    else:#{1
        print('Files to copy: ' + str(srcCP_size_gb) + 'GB')
    #}1
    if dstRM_size_gb < 1:#{1
        dstRM_size_mb = dstRM_size*mb_conv
        print('Files to remove: ' + str(dstRM_size_mb) + 'MB')
    #}1
    else:#{1
        print('Files to remove: ' + str(dstRM_size_gb) + 'GB')
    #}1
    if net_sync_size_gb < 1:#{1
        net_sync_size_mb = net_sync_size*mb_conv
        print('Net increase to destination: ' + str(net_sync_size_mb) + 'MB')
    #}1
    else:#{1
        print('Net increase to destination: ' + str(net_sync_size_gb) + 'GB')
    #}1
#}0
def remove_readonly(func, path, _):#{0
    #Clear the readonly bit and reattempt the removal
    os.chmod(path, stat.S_IWRITE)
    func(path)
#}0
def testDel(tarDir, isFolder):#{0
    tarDir = tarDir + delim
    testTarDir = []
    testContent = "testFile"
    testTarDir.append(func.buildPath(tarDir, "testDir", delim))
    tStr = "testDir" + delim + "subDir"
    testTarDir.append(func.buildPath(tarDir, tStr, delim))
    tStr = "testDir" + delim + "testFile.txt"
    testTarFile = func.buildPath(tarDir, tStr, delim)
    
    for tDir in testTarDir:#{1
        if not os.path.isdir(tDir):#{2
            os.mkdir(tDir)
        #}2
    #}1
    tFile = open(testTarFile, 'a', encoding='utf8')
    tFile.write(testContent)
    tFile.close()
    
    if isFolder:#{1
        delDirFile(tarDir, "subDir", isFolder, '')
        delete(isFolder)
        if os.path.isfile(testTarFile):#{2
            print("Test successful")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return False
        #}2
    #}1
    else:#{1
        delDirFile(tarDir, "testFile.txt", isFolder, '')
        delete(isFolder)
        if os.path.isdir(testTarDir[1]):#{2
            print("Test successful")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return False
        #}2
    #}1
#}0
def testDup(tarDir, mode, cmpMode):#{0
    tarDir = tarDir + delim
    testTarDir = []
    testTarFile = []
    testContent = "testFile"
    testTarDir.append(func.buildPath(tarDir, "testDir", delim))
    tStr = "testDir" + delim + "subDir1"
    testTarDir.append(func.buildPath(tarDir, tStr, delim))
    tStr = "testDir" + delim + "subDir2"
    testTarDir.append(func.buildPath(tarDir, tStr, delim))
    tStr = "testDir" + delim + "subDir1" + delim + "testFile1.txt"
    testTarFile.append(func.buildPath(tarDir, tStr, delim))
    tStr = "testDir" + delim + "subDir2" + delim + "testFile2.txt"
    testTarFile.append(func.buildPath(tarDir, tStr, delim))
    tStr = "testDir" + delim + "subDir2" + delim + "testFile3.txt"
    testTarFile.append(func.buildPath(tarDir, tStr, delim))
    
    for tDir in testTarDir:#{1
        if not os.path.isdir(tDir):#{2
            os.mkdir(tDir)
        #}2
    #}1
    for i in range(len(testTarFile)):#{1
        if not os.path.isfile(testTarFile[i]):#{2
            tFile = open(testTarFile[i], 'a', encoding='utf8')
            tFile.write(testContent)
            tFile.close()
        #}2
    #}1
    if mode == 1:#{1
        globalCompare(testTarDir[0], cmpMode, '')
        dup()
        result1 = os.listdir(testTarDir[1])
        result2 = os.listdir(testTarDir[2])
        if (len(result1) == 0 and len(result2) == 1) or \
        (len(result1) == 1 and len(result2) == 0):#{2
            print("Test successful")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return False
        #}2
    #}1
    elif mode == 2:#{1
        localCompare(testTarDir[0], cmpMode, '')
        dup()
        result1 = os.listdir(testTarDir[1])
        result2 = os.listdir(testTarDir[2])
        if len(result1) == 1 and len(result2) == 1:#{2
            print("Test successful")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=remove_readonly)
            return False
        #}2
    #}1
#}0
#Test the function of backupCopy 
def testSync(srcDir, dstDir):#{0
    srcDir = srcDir + delim
    dstDir = dstDir + delim
    testSrcDir = []
    testDstDir = []
    testSrcFile = []
    testDstFile = []
    testContent = ["testFile0", "testFile1", "testFile2", "testFile3"]
    resFile = []
    testSrcDir.append(func.buildPath(srcDir, "testDir", delim))
    testDstDir.append(func.buildPath(dstDir, "testDir", delim))
    tStr = "testDir" + delim + "subDir1"
    testSrcDir.append(func.buildPath(srcDir, tStr, delim))
    tStr = "testDir" + delim + "subDir2"
    testSrcDir.append(func.buildPath(srcDir, tStr, delim))
    testDstDir.append(func.buildPath(dstDir, tStr, delim))
    tStr = "testDir" + delim + "subDir3"
    testDstDir.append(func.buildPath(dstDir, tStr, delim))
    tStr1 = "testDir" + delim + "testFile0.txt"
    testSrcFile.append(func.buildPath(srcDir, tStr1, delim))
    tStr2 = "testDir" + delim + "subDir1" + delim + "testFile1.txt"
    testSrcFile.append(func.buildPath(srcDir, tStr2, delim))
    tStr3 = "testDir" + delim + "subDir2" + delim + "testFile2.txt"
    testSrcFile.append(func.buildPath(srcDir, tStr3, delim))
    testDstFile.append(func.buildPath(dstDir, tStr3, delim))
    tStr = "testDir" + delim + "subDir3" + delim + "testFile3.txt"
    testDstFile.append(func.buildPath(dstDir, tStr, delim))
    
    resFile.append(func.buildPath(dstDir, tStr1, delim))
    resFile.append(func.buildPath(dstDir, tStr2, delim))
    resFile.append(func.buildPath(dstDir, tStr3, delim))
    
    for sDir in testSrcDir:#{1
        if not os.path.isdir(sDir):#{2
            os.mkdir(sDir)
        #}2
    #}1
    for dDir in testDstDir:#{1
        if not os.path.isdir(dDir):#{2
            os.mkdir(dDir)
        #}2
    #}1
    for i in range(len(testSrcFile)):#{1
        if not os.path.isfile(testSrcFile[i]):#{2
            srcFile = open(testSrcFile[i], 'a', encoding='utf8')
            srcFile.write(testContent[i])
            srcFile.close()
        #}2
    #}1
    for j in range(len(testDstFile)):#{1
        if not os.path.isfile(testDstFile[j]):#{2
            dstFile = open(testDstFile[j], 'a', encoding='utf8')
            dstFile.write(testContent[j+2])
            dstFile.close()
        #}2
    #}1
    print("Testing core function..")
    backupCopy(testSrcDir[0], testDstDir[0], '', '')
    filing(3, 1)
    if os.path.isfile(resFile[0]) and os.path.isfile(resFile[1]) \
    and os.path.isfile(resFile[2]):#{1
        print("Test successful")
        shutil.rmtree(testSrcDir[0], onerror=remove_readonly)
        shutil.rmtree(testDstDir[0], onerror=remove_readonly)
        return True
    #}1
    else:#{1
        print("Test failed")
        #shutil.rmtree(testSrcDir[0], onerror=remove_readonly)
        #shutil.rmtree(testDstDir[0], onerror=remove_readonly)
        return False
    #}1
#}0
def listExl(exlDir):#{0
    eList1 = []
    eList2 = []
    eList = []
    for i in range(len(exlDir)):#{1
        if exlDir[i] == '<':#{2
            eList1.append(i)
        #}2
        elif exlDir[i] == '>':#{2
            eList2.append(i)
        #}2
    #}1
    for i in range(len(eList1)):#{1
        tl = eList2[i] - eList1[i]
        tl = eList1[i] + tl
        tStr = exlDir[eList1[i]+1:tl]
        entity0 = entityc.entity(tStr, tStr, delim)
        tStr = entity0.targetDir
        eList.append(tStr)
    #}1
    return eList
#}0
def loadFileObj(fileList, objList, isDup):#{0
    c = 0
    inc = 1
    strucList = []
    dupList = []
    ndupList = []
    size = 0
    fDir = ''
    while c <= len(fileList)-1:#{1
        nc = c + inc
        if nc > len(fileList)-1:#{2
            if size != 0 and len(dupList) != 0 and fDir != '':#{3
                dupList.append(fDir)
                dupList.append(size)
                dupList.append(inc)
                tList = dupList.copy() 
                strucList.append(tList) 
                size = 0
                fDir = ''
                dupList.clear()
            #}3
            else:#{3
                if isDup == False:#{4
                    fsize0 = fileList[c][2]
                    fstr0 = fileList[c][0] + delim + fileList[c][1]
                    if not fstr0 in ndupList:#{5
                        #ndupList.append(fstr0) #not needed coz function returns from here
                        ts = [fileList[c][1], fileList[c][0], fsize0, 1]
                        strucList.append(ts)
                    #}5
                #}4
            #}3
            break
        #}2
        fsize0 = fileList[c][2]
        fstr0 = fileList[c][0] + delim + fileList[c][1]
        fsize1 = fileList[nc][2]
        fstr1 = fileList[nc][0] + delim + fileList[nc][1]
        if fsize0 == fsize1:#{2
            if fCompare(fstr0, fstr1, cmp_Mode):#{3
                #print(fstr0 + ' == ' + fstr1)
                if size == 0:#{4
                    size = fsize0
                #}4
                if fDir == '':#{4
                    fDir = fileList[c][0]
                #}4
                if not fileList[c][1] in dupList:#{4
                    dupList.append(fileList[c][1])
                #}4
                if not fileList[nc][1] in dupList:#{4
                    dupList.append(fileList[nc][1])
                #}4
                inc = inc + 1
            #}3
        #}2
        else:#{2
            if size != 0 and len(dupList) != 0 and fDir != '':#{3
                dupList.append(fDir)
                dupList.append(size)
                dupList.append(inc)
                tList = dupList.copy()
                strucList.append(tList) 
                size = 0
                fDir = ''
                dupList.clear()
            #}3
            else:#{3
                if isDup == False:#{4
                    if inc > 1:#{5
                        if not fstr1 in ndupList:#{6 
                            ndupList.append(fstr1)
                            ts = [fileList[nc][1], fileList[nc][0], fsize1, 1]
                            strucList.append(ts)
                        #}6
                    #}5
                    else:#{5
                        if not fstr0 in ndupList:#{6
                            ndupList.append(fstr0)
                            ts = [fileList[c][1], fileList[c][0], fsize0, 1]
                            strucList.append(ts)
                        #}6
                    #}5
                #}4
            #}3
            c = c + inc
            inc = 1
        #}2
    #}1
    #strucList.sort(key=len) #comment out to keep sorted in file size
    for i in strucList:#{1
        num = i[-1]
        fsize = i[-2]
        #fDir = i[0].replace(dirStr, '')
        #fDir = fDir.split(delim)
        #del fDir[-1]
        #fDir = delim.join(fDir)
        fNames = i[0:num]
        fDir = i[num]
        item0 = entityc.iFile(num, fNames, fDir, fsize)
        objList.append(item0)
    #}1
#}0
#"Copy" files in srcDir into dstDir ignoring all subfolders
#Only files that does not exist in dstDir
def compareNcopy(srcDir, dstDir):#{0
    entity0 = entityc.entity(srcDir, dstDir, delim)
    srcDir = entity0.srcDir
    dstDir = entity0.dstDir
    if not os.path.isdir(srcDir) or not os.path.isdir(dstDir) or srcDir == dstDir:#{1
        return 0
    #}1
    else:#{1
        sameFileSrc = []
        srcFileList = []
        srcSizeList = []
        srcToCopy = []
        dstFileList = []
        dstSizeList = []
        srcObjList = [] 
        dstObjList = []
        
        global totalSrcFile #int
        global totalDstFile #int
        global totalSrcCopy #int
        global totalDstRemove #int
        global totalDstRename #int
        
        for folderName, subFolders, fileNames in os.walk(srcDir):#{2
            if folderName == srcDir:#{3
                for fileName in fileNames:#{4
                    if fileName.lower() != thumbs.lower():#{5
                        fsize = os.path.getsize(func.buildPath(folderName, fileName, delim))
                        srcSizeList.append(fsize)
                        srcFileList.append([folderName, fileName, fsize])
                    #}5
                #}4
            #}3
        #}2
        for folderName, subFolders, fileNames in os.walk(dstDir):#{2
            if folderName == dstDir:#{3
                for fileName in fileNames:#{4
                    if fileName.lower() != thumbs.lower():#{5
                        fsize = os.path.getsize(func.buildPath(folderName, fileName, delim))
                        dstSizeList.append(fsize)
                        dstFileList.append([folderName, fileName, fsize])
                    #}5
                #}4
            #}3
        #}2
        #Assign value to global variables
        totalSrcFile = totalSrcFile + len(srcFileList)
        totalDstFile = totalDstFile + len(dstFileList)
        
        #At this point path and file size are both ready for comparison
        srcFileList.sort(key=lambda x: x[2]) #sort fileList against fSize (file size)
        dstFileList.sort(key=lambda x: x[2]) #sort fileList against fSize (file size)
        
        loadFileObj(srcFileList, srcObjList, False)
        loadFileObj(dstFileList, dstObjList, False)
        '''
        print(srcDir + ' vs ' + dstDir)
        for i in srcObjList:
            ts = i.fileNames
            print(ts)
        for i in dstObjList:
            ts = i.fileNames
            print(ts)
        '''
        #srcObjList.sort(key=lambda x: x.fileSize)
        #dstObjList.sort(key=lambda x: x.fileSize)
        
        #To remove dstDir files that does not exist in srcDir
        #To also update dstFileDict and dstFileList
        #If true then maybe there are some files to remove
        if len(dstObjList) != 0:#{2
            #If there is nothing in the srcFolder
            #then remove all files in corresponding dstfolder, no need to fileCompare
            if len(srcObjList) == 0:#{3
                for c in range(len(dstObjList)):#{4
                    #This bit of code is the same as
                    #remove command when srcFile is compared against dstFile
                    if dstObjList[c].num == 1:#{5
                        tempRM0 = func.buildPath(dstDir, dstObjList[c].fileNames[0], delim) #dstDir is always as dstFileList[c][0]
                        removeList.append(tempRM0)
                        totalDstRemove = totalDstRemove + 1 #Global variable
                    #}5
                    else:#{5
                        nList = dstObjList[c].fileNames
                        totalDstRemove = totalDstRemove + dstObjList[c].num
                        for i in nList:#{6
                            tempRM = func.buildPath(dstDir, i, delim)
                            removeList.append(tempRM)
                        #}6
                    #}5
                #}4
            #}3
            else:#{3
                for c in range(len(dstObjList)):#{4
                    toRemove = True
                    dstDirFile = func.buildPath(dstDir, dstObjList[c].fileNames[0], delim) #complete path
                    dstFile = dstObjList[c].fileNames[0] #file name only
                    dstFsize = dstObjList[c].fileSize
                    dstFnum = dstObjList[c].num
                    #Assume if file size different then content different
                    if dstFsize in srcSizeList:#{5 
                        for d in range(len(srcObjList)):#{6
                            srcFile = srcObjList[d].fileNames[0] #file name only
                            srcFsize = srcObjList[d].fileSize
                            srcDirFile = func.buildPath(srcDir, srcObjList[d].fileNames[0], delim) #complete path
                            srcFnum = srcObjList[d].num
                            #return actual size which is same on different file system, not size on disk
                            #Investigate further about filecmp.cmp
                            if dstFsize == srcFsize:#{7
                                #filecmp compare primarily compare file size and modification time
                                #3rd arg 0-filecmp, 1-hashlib
                                if fCompare(dstDirFile, srcDirFile, cmp_Mode):#{8
                                    #And its corresponding srcFile is added to srcToCopy list
                                    #By not adding it to the sameFileSrc list
                                    #before the file is re-copied
                                    #dstFile to be kept, but renamed to be same as corresponding srcFile
                                    if dstFnum == 1 and srcFnum == 1:#{9
                                        if dstFile != srcFile:#{10
                                                tempRN1 = func.buildPath(dstDir, srcFile, delim)
                                                renameList.append([dstDirFile, tempRN1])
                                                totalDstRename = totalDstRename + 1 #Global variable
                                        #}10
                                        toRemove = False
                                        sameFileSrc.append(srcObjList[d]) #file that is the same
                                        break
                                    #}9
                                    else:#{9
                                        srcNlist = srcObjList[d].fileNames.copy() 
                                        dstNlist = dstObjList[c].fileNames.copy()
                                        toRM = []
                                        for i in srcNlist:#{10
                                            if i in dstNlist:#{11
                                                dstNlist.remove(i)
                                                toRM.append(i) #not to remove elements while looping
                                            #}11
                                        #}10
                                        for i in toRM:#{10
                                            srcNlist.remove(i)
                                        #}10
                                        srcLen = len(srcNlist)
                                        dstLen = len(dstNlist)
                                        numSum = srcLen + dstLen
                                        if numSum != 0:#{10
                                            numDiff = srcLen - dstLen
                                            if numDiff > 0:#{11
                                                    for i in range(dstLen, srcLen, 1):#{12
                                                            checkNcopyList.append([srcDir, dstDir, srcNlist[i], srcNlist[i]])
                                                            totalSrcCopy = totalSrcCopy + 1 #Global variable
                                                    #}12
                                                    for i in range(0, dstLen, 1):#{12
                                                            if srcNlist[i] != dstNlist[i]:#{13
                                                                    tempRN1 = func.buildPath(dstDir, srcNlist[i], delim)
                                                                    renameList.append([dstDirFile, tempRN1])
                                                                    totalDstRename = totalDstRename + 1 #Global variable
                                                            #}13
                                                    #}12
                                            #}11
                                            elif numDiff < 0:#{11
                                                    for i in range(srcLen, dstLen, 1):#{12
                                                            tempRM0 = func.buildPath(dstDir, dstNlist[i], delim)
                                                            removeList.append(tempRM0)
                                                            totalDstRemove = totalDstRemove + 1 #Global variable
                                                    #}12
                                                    for i in range(0, srcLen, 1):#{12
                                                            if srcNlist[i] != dstNlist[i]:#{13
                                                                    tempRN1 = func.buildPath(dstDir, srcNlist[i], delim)
                                                                    renameList.append([dstDirFile, tempRN1])
                                                                    totalDstRename = totalDstRename + 1 #Global variable
                                                            #}13
                                                    #}12
                                            #}11
                                            else:#{11
                                                    for i in range(0, srcLen, 1):#{12
                                                            if srcNlist[i] != dstNlist[i]:#{13
                                                                    tempRN1 = func.buildPath(dstDir, srcNlist[i], delim)
                                                                    renameList.append([dstDirFile, tempRN1])
                                                                    totalDstRename = totalDstRename + 1 #Global variable
                                                            #}13
                                                    #}12
                                            #}11
                                        #}10
                                        toRemove = False
                                        sameFileSrc.append(srcObjList[d]) #file that is the same
                                        break
                                    #}9
                                #}8
                            #}7
                            elif srcFsize > dstFsize:#{7
                                break
                            #}7
                        #}6
                    #}5
                    #Condition for dst file removal is if the file does not exist in src
                    #Or dst file exist in src, but it's more than 2 years old
                    if toRemove == True:#{5
                        #provision for multi-copy files
                        if dstFnum == 1:#{6
                            removeList.append(dstDirFile) 
                            totalDstRemove = totalDstRemove + 1 #Global variable
                        #}6
                        else:#{6
                            nList = dstObjList[c].fileNames
                            totalDstRemove = totalDstRemove + dstFnum
                            for i in nList:#{7
                                tempRM = func.buildPath(dstDir, i, delim)
                                removeList.append(tempRM)
                            #}7
                        #}6
                    #}5
                #}4
            #}3
        #}2
        #To copy srcDir files that does not exist in dstDir to dstDir
        if len(srcObjList) == 0:#{2
            return 1
        #}2
        else:#{2
            #This if clause is for when dst dir match src dir, but it's empty
            #Only empty of files, but there may be sub-folders
            if len(dstObjList) == 0:#{3
                for d in range(len(srcObjList)):#{4
                    if srcObjList[d].num == 1:#{5
                        checkNcopyList.append([srcDir, dstDir, srcObjList[d].fileNames[0], srcObjList[d].fileNames[0]])
                        totalSrcCopy = totalSrcCopy + 1 #Global variable
                    #}5
                    else:#{5
                        nList = srcObjList[d].fileNames
                        totalSrcCopy = totalSrcCopy + srcObjList[d].num
                        for i in nList:#{6
                            checkNcopyList.append([srcDir, dstDir, i, i])
                        #}6
                    #}5
                #}4
            #}3
            else:#{3
                #If src file is not in the sameFileSrc list, then it's to be copied to dst
                #srcToCopy = list(set(sameFileSrc)^set(srcFileList)) #remove same elements between 2 1D lists
                for i in srcObjList:#{4
                    if not i in sameFileSrc:#{5
                        srcToCopy.append(i)
                    #}5
                #}4
                for d in range(len(srcToCopy)):#{4
                    if srcToCopy[d].num == 1:#{5
                        checkNcopyList.append([srcDir, dstDir, srcToCopy[d].fileNames[0], srcToCopy[d].fileNames[0]])
                        totalSrcCopy = totalSrcCopy + 1 #Global variable
                    #}5
                    else:#{5
                        nList = srcToCopy[d].fileNames
                        totalSrcCopy = totalSrcCopy + srcToCopy[d].num
                        for i in nList:#{6
                            checkNcopyList.append([srcDir, dstDir, i, i])
                        #}6
                    #}5
                #}4
            #}3
        #}2
        return 1
    #}1
#}0

#First subfolders in dst that does not exist in src are removed include all files
#"Copy" files in subfolders of srcDir into subfolders of dstDir
#Subfolders that does not exist in dstDir is created and then files copied in
#Only files that are not already in dst are copied
def backupCopy(srcDir, dstDir, exlSrcDir, exlDstDir):#{0
    entity0 = entityc.entity(srcDir, dstDir, delim)
    srcDir = entity0.srcDir
    dstDir = entity0.dstDir
    dst_drive = entity0.dst_drive
    esList = listExl(exlSrcDir)
    edList = listExl(exlDstDir)
    print('Analysing sync from ' + srcDir + ' to ' + dstDir)
    print('Source directories to exclude:')
    print(esList)
    print('Destination directories to exclude:')
    print(edList)
    isExlSrc = False
    isExlDst = False
    
    if not os.path.isdir(srcDir) or not os.path.isdir(dstDir) or srcDir == dstDir:#{1
        print('Error: source or destination directory not found\n')
        return 0
    #}1
    else:#{1
        dstFolderList = []
        srcFolderList = []
        dstRemoved = []
        #totalFiles = 0
        sameFolderSrc = []
        
        #Global variables reset
        global totalSrcFile
        global totalDstFile
        global totalSrcCopy
        global totalDstRemove
        global totalDstRename
        totalSrcFile = 0
        totalDstFile = 0
        totalSrcCopy = 0
        totalDstRemove = 0
        totalDstRename = 0
        rmtreeList.clear()
        copytreeList.clear()
        renameList.clear()
        removeList.clear()
        checkNcopyList.clear()
        
        #Copying files from the srcDir to dstDir ignoring all subfolders
        if not dstDir in edList and not srcDir in esList:#{2
            compareNcopy(srcDir, dstDir)
        #}2
        for folderName, subFolders, fileNames in os.walk(dstDir):#{2
            for edDir in edList:#{3
                if edDir in folderName:#{4
                    isExlDst = True
                #}4
            #}3
            if isExlDst == True:#{3
                isExlDst = False
                continue
            #}3
            else:#{3
                tWorkFolder = folderName.split(delim)
                workFolder = tWorkFolder[len(tWorkFolder)-1]
                if workFolder != pycache and folderName != dstDir:#{4
                    dstFolder = folderName.replace(dstDir, '')
                    dstFolderList.append(dstFolder)
                #}4
            #}3
        #}2
        dstFolderList.sort(key=lambda dstFolderList: len(dstFolderList))
        #dstFolderList is replaced with sort result sorted by string length
        #FolderList actually contains pathnames minus the dst/srcDir path
        
        for folderName, subFolders, fileNames in os.walk(srcDir):#{2
            for esDir in esList:#{3
                if esDir in folderName:#{4
                    isExlSrc = True
                #}4
            #}3
            if isExlSrc == True:#{3
                isExlSrc = False
                continue
            #}3
            else:#{3
                tWorkFolder = folderName.split(delim)
                workFolder = tWorkFolder[len(tWorkFolder)-1]
                if workFolder != pycache and folderName != srcDir:#{4
                    srcFolder = folderName.replace(srcDir, '')
                    srcFolderList.append(srcFolder)
                #}4
            #}3
        #}2
        srcFolderList.sort(key=lambda srcFolderList: len(srcFolderList))
        #srcFolderList is replaced with sort result sorted by string length
        #Loop through dstFolderList, remove dstFolder not in srcFolderList
        #   store dstFolder in srcFolderList on sameFolderList
        if len(dstFolderList) != 0:#{2
            for d in range(len(dstFolderList)):#{3
                if not dstFolderList[d] in srcFolderList:#{4
                    done = False
                    #If dstFolder already removed or is a subfolder to an already removed folder
                    #then do nothing
                    for c in range(len(dstRemoved)):#{5
                        if dstRemoved[c] in dstFolderList[d]:#{6
                            done = True
                            break
                        #}6
                    #}5
                    if done == False:#{5
                        tf = dstDir + dstFolderList[d]
                        cpt = sum([len(cc) for aa, bb, cc in os.walk(tf)])
                        totalDstFile = totalDstFile + cpt #Assign global variable
                        totalDstRemove = totalDstRemove + cpt #Assign global variable
                        rmtreeList.append(tf)
                        dstRemoved.append(dstFolderList[d])
                    #}5
                #}4
                else:#{4
                    sameFolderSrc.append(dstFolderList[d])
                #}4
            #}3
        #}2
        #Loop through srcFolderList, copy src to dst
        #Does not care about dstFolder that was removed in the last bit of code
        #Works with sameFolderList only
        if len(srcFolderList) != 0:#{2
            for c in range(len(srcFolderList)):#{3
                srcFolder = srcFolderList[c]
                #if not srcFolder in srcCopied:
                #if src folder does not exist in dst
                #   then use shutil.copytree to copy entire dir 
                if not srcFolder in sameFolderSrc:#{4
                    src = srcDir + srcFolder
                    dst = dstDir + srcFolder
                    
                    #The srcFolderList is sorted by string length
                    #so if src dir is part of previously "copied" dir 
                    #then do nothing
                    #do not use os.path.isdir(dst) to check
                    #because no files are copied at this point
                    toCp = True
                    for pp in copytreeList:#{5
                        if pp[0] in src:#{6
                            toCp = False
                            break
                        #}6
                    #}5
                    if toCp == True:#{5
                        cpt = sum([len(cc) for aa, bb, cc in os.walk(src)])
                        totalSrcCopy = totalSrcCopy + cpt
                        totalSrcFile = totalSrcFile + cpt
                        copytreeList.append([src, dst])
                    #}5
                    #Improvement:
                    #   for src dir that doesn't have matching dst dir, do not need to compareNcopy
                    #   All content (sub-folder+files) can be copied directly
                    #   without needing to compare, use shutil.copytree
                #}4
                #else src folder does exist in dst
                #   then straight to compareNcopy
                else:#{4
                    src = srcDir + srcFolder
                    dst = dstDir + srcFolder
                    compareNcopy(src, dst)
                #}4
            #}3
        #}2
        sync_size_est(dst_drive)
        filecmp.clear_cache()
        print('Total source file count: ' + str(totalSrcFile))
        print('Total destination file count: ' + str(totalDstFile))
        print('Total source file to copy: ' + str(totalSrcCopy))
        print('Total destination file to remove: ' + str(totalDstRemove))
        print('Total destination file to rename: ' + str(totalDstRename))
        if totalSrcFile != totalDstFile - totalDstRemove + totalSrcCopy:#{2
            print("Issue encountered, please investigate")
        #}2
        else:#{2
            print("No issue encountered")
        #}2
        print('Analysis finished\n')
        #print("copytreeList: " + str(copytreeList))
        #print("rmtreeList: " + str(rmtreeList))
        #print("renameList: " + str(renameList))
        #print("removeList: " + str(removeList))
        #print("checkNcopyList: " + str(checkNcopyList))
        #print("agedFileList: " + str(agedFileList) + '\n')
        return 1
    #}1
#}0

#globalCompare compares across folders
def globalCompare(targetDir, cmpMode, exlDir):#{0
    entity0 = entityc.entity(targetDir, targetDir, delim)
    targetDir = entity0.targetDir
    eList = listExl(exlDir)
    print('Directories to exclude:')
    print(eList)
    isExl = False
    
    cwd = os.getcwd()
    if not os.path.isdir(targetDir):#{1
        print('Error: Target directory not found\n')
        return ''
    #}1
    else:#{1
        fileList = []
        nameList = []
        dupFileList.clear()
        opCounter = 0
        cpCounter = 0
        dnCounter = 0
        totalFiles = 0      
        for folderName, subFolders, fileNames in os.walk(targetDir):#{2
            for eDir in eList:#{3
                if eDir in folderName:#{4
                    isExl = True
                #}4
            #}3
            if isExl == True:#{3
                isExl = False
                continue
            #}3
            else:#{3
                for fileName in fileNames:#{4
                    if fileName != thumbs:#{5
                        totalFiles = totalFiles + 1
                        tPath = func.buildPath(folderName, fileName, delim)
                        fSize = os.path.getsize(tPath)
                        mTime = os.path.getmtime(tPath)
                        fileList.append([folderName, fileName, fSize])
                        nameList.append([folderName, fileName, mTime])
                    #}5
                #}4
            #}3
        #}2     
        #Now a list of all files and dir is ready
        if len(fileList) == 0:#{2
            print('There are no files in target directory\n')
            return ''
        #}2
        else:#{2
            cMode = ''
            if cmpMode == 0:#{3
                cMode = 'Filecmp.cmp (file content)'
            #}3
            else:#{3
                cMode = 'Hashlib (Checksum:SHA256)'
            #}3
            c = 0
            dupName = []
            dupList = []
            nameList.sort(key=lambda x: x[1]) #sort in order of file name
            while c < (len(nameList)-1):#{3
                nc = c + 1
                dir1 = nameList[c][0]
                dir2 = nameList[nc][0]
                file1 = nameList[c][1]     
                file2 = nameList[nc][1] #file to be removed from nameList if same
                mtime1 = nameList[c][2]
                mtime2 = nameList[nc][2]
                if file1 == file2:#{4
                    #print(file1 + ' => ' + file2)
                    df1 = func.buildPath(dir1, file1, delim)
                    df2 = func.buildPath(dir2, file2, delim)
                    if mtime1 > mtime2:#{5
                        df3 = 'latter'
                    #}5
                    elif mtime2 > mtime1:#{5
                        df3 = 'former'
                    #}5
                    else:#{5
                        df3 = 'either'
                    #}5
                    dupName.append(df1 + ' == ' + df2 + ', Remove: ' + df3)
                    dnCounter = dnCounter + 1
                    del nameList[nc]
                    continue #effect is c is not incremented
                #}4
                c = c + 1
            #}3
            c = 0
            print('Finding duplicated files across all sub-directories...')
            fileList.sort(key=lambda x: x[2]) #sort fileList against fSize (file size)
            while c < (len(fileList)-1):#{3
                nc = c + 1
                opCounter = opCounter + 1
                file1 = fileList[c][1]     
                file2 = fileList[nc][1]     
                size1 = fileList[c][2]
                size2 = fileList[nc][2]
                dir1 = fileList[c][0]
                dir2 = fileList[nc][0]
                df1 = func.buildPath(dir1, file1, delim)
                df2 = func.buildPath(dir2, file2, delim)
                #cmpMode 0-filecmp, 1-hashlib
                if size1 == size2 and size1 != 0:#{4
                    if fCompare(df1, df2, cmpMode):#{5 
                        f1ct = os.path.getctime(df1) 
                        f2ct = os.path.getctime(df2)
                        f1at = os.path.getatime(df1)
                        f2at = os.path.getatime(df2)
                        f1t = ([f1ct, f1at])
                        f2t = ([f2ct, f2at])
                        f1t.sort()
                        f2t.sort()
                        if f1t[len(f1t)-1] > f2t[len(f2t)-1]:#{6
                            dupFileList.append(df2)
                            del fileList[nc]
                            cpCounter = cpCounter + 1
                            tStr = df1 + ',==,' + df2 + ', remove: latter'
                            dupList.append(tStr)
                            continue #effect is c is not incremented
                        #}6
                        else:#{6
                            dupFileList.append(df1)
                            del fileList[c]
                            cpCounter = cpCounter + 1
                            tStr = df1 + ',==,' + df2 + ', remove: former'
                            dupList.append(tStr)
                            continue #effect is c is not incremented
                        #}6    
                    #}5
                #}4
                c = c + 1
            #}3
            filecmp.clear_cache()
            outputFile = open(cwd + delim + 'findDupFiles_report.txt', 'a', encoding='utf8') #encoding arg is for writing nonEng char 
            outputFile.write('\n')
            outputFile.write('Target directory: ' + targetDir + '\n')
            outputFile.write('Find duplicated files across all sub-directories\n')
            if len(dupList) > 0:#{3
                outputFile.write('Files with duplicated content:\n')
                for i in dupList:#{4
                    outputFile.write(i + '\n')
                #}4
            #}3
            if len(dupName) > 0:#{3
                outputFile.write('Files with duplicated names:\n')
                for i in dupName:#{4
                    outputFile.write(i + '\n')
                #}4
            #}3
            outputFile.write('Method of file comparison: ' + cMode + '\n')
            outputFile.write('Total file count: ' + str(totalFiles) + '\n')
            outputFile.write('Comparison Ops: ' + str(opCounter) + '\n')
            outputFile.write('Duplicated files: ' + str(cpCounter) + '\n')
            outputFile.write('Duplicated fileNames: ' + str(dnCounter) + '\n')
            outputFile.write('Only files with duplicated content are included in deletion\n')
            outputFile.write('Duplicated file naming require user investigation\n')
            outputFile.close()
            print('Method of file comparison: ' + cMode)
            print('Total file count: ' + str(totalFiles))
            print('Duplicated files: ' + str(cpCounter))
            print('Duplicated fileNames: ' + str(dnCounter))
            print('Only files with duplicated content are included in deletion')
            print('Duplicated file naming require user investigation')
            print('Please find analysis report in ' + cwd + delim + 'findDupFiles_report.txt')
            print('Analysis completed\n')
            ret = str(totalFiles) + '-' + str(dnCounter) + '-' + str(cpCounter)
            return ret
        #}2
    #}1
#}0

#compareLocal compare only files within a folder
#localCompare returns a string 
def localCompare(targetDir, cmpMode, exlDir):#{0
    entity0 = entityc.entity(targetDir, targetDir, delim)
    targetDir = entity0.targetDir
    eList = listExl(exlDir)
    print('Directories to exclude:')
    print(eList)
    isExl = False
    
    cwd = os.getcwd()
    if not os.path.isdir(targetDir):#{1
        print('Error: Target directory not found\n')
        return ''
    #}1
    else:#{1
        #Variable init and definition
        dupFileList.clear()
        dupList = []
        opCounter = 0
        cpCounter = 0
        totalFiles = 0
        cMode = ''
        if cmpMode == 0:#{2
            cMode = 'Filecmp.cmp (file content)'
        #}2
        else:#{2
            cMode = 'Hashlib (Checksum:SHA256)'
        #}2
        print('Finding duplicated files within each sub-directory...') 
        for folderName, subFolders, fileNames in os.walk(targetDir):#{2
            fileList = []
            c = 0
            for eDir in eList:#{3
                if eDir in folderName:#{4
                    isExl = True
                #}4
            #}3
            if isExl == True:#{3
                isExl = False
                continue
            #}3
            else:#{3
                for fileName in fileNames:#{4
                    if fileName != thumbs:#{5
                        totalFiles = totalFiles + 1
                        fsize = os.path.getsize(func.buildPath(folderName, fileName, delim))
                        fileList.append([fileName,fsize])
                    #}5
                #}4
                if len(fileList) != 0:#{4
                    fileList.sort(key=lambda x: x[1]) #sort fileList against fSize (file size)
                    while c < (len(fileList)-1):#{5
                        nc = c + 1
                        opCounter = opCounter + 1
                        file1 = fileList[c][0]     #
                        file2 = fileList[nc][0]     #File to remove if same
                        ff1 = func.buildPath(folderName, file1, delim)
                        ff2 = func.buildPath(folderName, file2, delim)
                        size1 = fileList[c][1]
                        size2 = fileList[nc][1]
                        if size1 == size2 and size1 != 0:#{6
                            if fCompare(ff1, ff2, cmpMode):#{7
                                #File with the latest creation time or access time is kept
                                f1ct = os.path.getctime(ff1)
                                f1at = os.path.getatime(ff1)
                                f2ct = os.path.getctime(ff2)
                                f2at = os.path.getatime(ff2)
                                f1t = ([f1ct, f1at])
                                f2t = ([f2ct, f2at])
                                f1t.sort()
                                f2t.sort()
                                if f1t[len(f1t)-1] > f2t[len(f2t)-1]:#{8
                                    dupFileList.append(ff2)
                                    del fileList[nc] #list is auto re-indexed after element removed
                                    cpCounter = cpCounter + 1
                                    tStr = ff1 + ',==,' + ff2 + ', remove: ' + ff2
                                    dupList.append(tStr)
                                    continue #effect is c is not incremented
                                #}8
                                else:#{8
                                    dupFileList.append(ff1)
                                    del fileList[c]
                                    cpCounter = cpCounter + 1
                                    tStr = ff1 + ',==,' + ff2 + ', remove: ' + ff1
                                    dupList.append(tStr)
                                    continue #effect is c is not incremented
                                #}8
                            #}7
                        #}6
                        c = c + 1
                    #}5
                #}4
            #}3
        #}2
        filecmp.clear_cache()
        outputFile = open(cwd + delim + 'findDupFiles_report.txt', 'a', encoding='utf8') #encoding arg is for writing nonEng char 
        outputFile.write('\n')
        outputFile.write('Target directory: ' + targetDir + '\n')
        outputFile.write('Find duplicated files within each sub-directory\n')
        if len(dupList) > 0:#{2
            outputFile.write('Files with duplicated content:\n')
            for i in dupList:#{3
                outputFile.write(i + '\n')
            #}3
        #}2
        outputFile.write('Method of file comparison: ' + cMode + '\n')
        outputFile.write('Total file count: ' + str(totalFiles) + '\n')
        outputFile.write('Comparison Ops: ' + str(opCounter) + '\n')
        outputFile.write('Duplicated files: ' + str(cpCounter) + '\n')
        outputFile.close()
        print('Method of file comparison: ' + cMode)
        print('Total file count: ' + str(totalFiles))
        print('Duplicated files: ' + str(cpCounter))
        print('Please find analysis report in ' + cwd + delim + 'findDupFiles_report.txt')
        print('Analysis completed\n')
        ret = str(totalFiles) + '-0-' + str(cpCounter)
        return ret
    #}1
#}0

#return number of items deleted, if an exception is thrown then return 0 immediately
#Do not delete any folder starts with '.' and files like '.sys' and '.dll'
#targetName is full pathname, targetType is True for folder..
def delDirFile(wd, targetName, isFolder, exlDir):#{0
    entity0 = entityc.entity(wd, wd, delim)
    wd = entity0.targetDir
    eList = listExl(exlDir)
    print('Directories to exclude:')
    print(eList)
    isExl = False
    
    if not os.path.isdir(wd):#{1
        print('Error: target directory not found\n')
        return 0
    #}1
    else:#{1
        workFolder = ''
        cpCounter = 0
        delDFList.clear()
        if isFolder == False:#{2
            checkTar = targetName.split('.')
            ext = checkTar[len(checkTar)-1]
            if ext == 'sys' or ext == 'dll' or len(checkTar) == 1:#{3
                print('Error: file extension must be specified and cannot be .sys or .dll\n')
                return 0
            #}3
        #}2
        else:#{2
            checkTar = targetName.split('.')
            ext = checkTar[0]
            if ext == '':#{3
                print('Error: folder name cannot start with "."\n')
                return 0
            #}3
        #}2
        print('Finding specified file/folder for deletion...')
        for folderName, subFolders, fileNames in os.walk(wd):#{2
            for eDir in eList:#{3
                if eDir in folderName:#{4
                    isExl = True
                #}4
            #}3
            if isExl == True:#{3
                isExl = False
                continue
            #}3
            else:#{3
                tWorkFolder = folderName.split(delim)
                workFolder = tWorkFolder[len(tWorkFolder)-1]
                #print('Folder inside ' + workFolder)
                if isFolder == False:#{4
                    for fileName in fileNames:#{5
                        if fileName.lower() == targetName.lower():#{6
                            target = func.buildPath(folderName, fileName, delim)
                            delDFList.append(target)
                            cpCounter = cpCounter + 1
                        #}6
                    #}5
                #}4
                else:#{4
                    if folderName != wd:#{5
                        if workFolder.lower() == targetName.lower():#{6
                            #Add to delete list
                            delDFList.append(folderName)
                            cpCounter = cpCounter + 1
                        #}6
                    #}5
                #}4
            #}3
        #}2
        print('Number of instances found: ' + str(cpCounter))
        print('Analysis completed\n')
        return cpCounter
    #}1
#}0
if __name__ == '__main__':#{0
    print('Module has no standalone function')
#}0
