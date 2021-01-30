from m_gVar import * #contains global variables
import m_FileOps1_1 as fOps
import m_class_entity as entityc
import m_functions as func
from operator import itemgetter

#Reports on age of files in tarDir
#base on creation and access time
def checkAge(tarDir, exDir):#{0
    #under 1yr, >1yr, >2yr, >3yr, >4yr, >5yr
    ageList = [0, 0, 0, 0, 0, 0]
    perList = []
    file_list = func.listFile(tarDir, delim, exDir, thumbs)
    totalFile = len(file_list)
    for i in file_list:#{1
        ct = os.path.getctime(i)
        ctt = time.ctime(ct)
        ctt = ctt.split(' ')
        ctt = int(ctt[len(ctt)-1])
        at = os.path.getatime(i)
        att = time.ctime(at)
        att = att.split(' ')
        att = int(att[len(att)-1])
        if att > ctt:#{2
            diffYr = nowYr - att
        #}2
        else:#{2
            diffYr = nowYr - ctt
        #}2
        if diffYr < len(ageList)-1:#{2
            ageList[diffYr] = ageList[diffYr] + 1
            #if diffYr == 3:
            #    print(i)
        #}2
        elif diffYr >= len(ageList)-1:#{2
            ageList[len(ageList)-1] = ageList[len(ageList)-1] + 1
        #}2
    #}1
    for i in ageList:#{1
        tt = (i/totalFile)*100
        tts = tt + 0.5
        if int(tts) == int(tt):#{2
            tt = int(tt)
        #}2
        else:#{2
            tt = int(tt+1)
        #}2
        perList.append(int(tt))
    #}1
    print('File age report on: ' + tarDir)
    print('Excluding: ' + exDir)
    print('Total number of files: ' + str(totalFile))
    print('Files under 1 year old: ' + str(ageList[0]) + '~' + str(perList[0]) + '%')
    print('Files 1 year old: ' + str(ageList[1]) +  '~' + str(perList[1]) + '%')
    print('Files 2 years old: ' + str(ageList[2]) +  '~' + str(perList[2]) + '%')
    print('Files 3 years old: ' + str(ageList[3]) +  '~' + str(perList[3]) + '%')
    print('Files 4 years old: ' + str(ageList[4]) +  '~' + str(perList[4]) + '%')
    print('Files 5 years or older: ' + str(ageList[5]) +  '~' + str(perList[5]) + '%')
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
        esList = func.listExl(exlSrcDir, delim)
        edList = func.listExl(exlDstDir, delim)
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
            tfTotal = sum([len(cc) for aa, bb, cc in os.walk(tf)])
            try:#{3
                shutil.rmtree(tf)
                totalDstRemove = totalDstRemove + tfTotal
            #}3
            except:#{3
                tfLeft = sum([len(cc) for aa, bb, cc in os.walk(tf)])
                tfRM = tfTotal - tfLeft
                totalDstRemove = totalDstRemove + tfRM
                print('dir removal error on: ' + tf)
                continue
            #}3
        #}2
        for rmf in removeList:#{2
            try:#{3
                os.remove(rmf)
                totalDstRemove = totalDstRemove + 1
            #}3
            except OSError:#{3
                print('OSerror during file removal: ' + rmf)
                continue
            #}3
            #print('Remove: ' + rmf)
        #}2
    #}1
    if iMode == 3 or iMode == 2:#{1
        for rnf in renameList:#{2
            try:#{3
                os.rename(rnf[0], rnf[1])
                totalDstRename = totalDstRename + 1
            #}3
            except OSError:#{3
                print('OSerror during file rename: ' + rnf)
                continue
            #}3
            #print('Rename: ' + rnf[0] + ' -> ' + rnf[1])
        #}2
    #}1
    cpTreeErr = []
    cpFileErr = []
    if iMode == 3 or iMode == 1:#{1
        #copytree function create dst directory path automatically
        for cpt in copytreeList:#{2
            try:#{3
                shutil.copytree(cpt[0], cpt[1])
                temp = sum([len(cc) for aa, bb, cc in os.walk(cpt[1])])
                totalSrcCopy = totalSrcCopy + temp
            #}3
            except Error as err:#{3
                print('Error during directory copy')
                print('src name: ' + str(err.args[0]))
                print('dst name: ' + str(err.args[1]))
                print('exception: ' + str(err.args[2]))
                cpTreeErr.append(cpt)
                continue
            #}3
        #}2
        for cptErr in cpTreeErr:#{2
            copytreeList.remove(cptErr)
        #}2
        for cpf in checkNcopyList:#{2
            tempDst = func.buildPath(cpf[1], cpf[3], delim)
            #print('Folder copy ' + cpf[0] + ' to ' + cpf[1])
            if fOps.checkNcopy(cpf[0], cpf[1], cpf[2], cpf[3], delim) == True:#{3
                totalSrcCopy = totalSrcCopy + 1
            #}3
            else:#{3
                cpFileErr.append(cpf)
            #}3
        #}2
        for cpfErr in cpFileErr:#{2
            checkNcopyList.remove(cpfErr)
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
#Test the function of backupCopy 
def testSync(srcDir, dstDir):#{0
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
        shutil.rmtree(testSrcDir[0], onerror=func.remove_readonly)
        shutil.rmtree(testDstDir[0], onerror=func.remove_readonly)
        return True
    #}1
    else:#{1
        print("Test failed")
        #shutil.rmtree(testSrcDir[0], onerror=func.remove_readonly)
        #shutil.rmtree(testDstDir[0], onerror=func.remove_readonly)
        return False
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
        srcFileList.sort(key=itemgetter(2)) #sort fileList against fSize (file size)
        #srcFileList.sort(key=lambda x: x[2])
        
        dstFileList.sort(key=itemgetter(2)) #sort fileList against fSize (file size)
        #dstFileList.sort(key=lambda x: x[2])

        #at0 = datetime.datetime.now()
        #sec0 = at0.second
        #msec0 = at0.microsecond
        #print(srcFileList)
        func.loadFileObj(srcFileList, srcObjList, False, delim, cmp_Mode, hash_Mode)
        func.loadFileObj(dstFileList, dstObjList, False, delim, cmp_Mode, hash_Mode)
        
        #at1 = datetime.datetime.now()
        #sec1 = at1.second
        #msec1 = at1.microsecond
        #t0 = sec0 + msec0/1000000
        #t1 = sec1 + msec1/1000000
        #dt = t1 - t0
        #profile1.append(dt)
        '''
        print(srcDir + ' vs ' + dstDir)
        for i in srcObjList:
            ts = i.fileNames
            print(ts)
        print('\n')
        for i in dstObjList:
            ts = i.fileNames
            print(ts)
        print('\n')
        '''
        #srcObjList.sort(key=lambda x: x.fileSize)
        #dstObjList.sort(key=lambda x: x.fileSize)

        #at0 = datetime.datetime.now()
        #sec0 = at0.second
        #msec0 = at0.microsecond
        
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
                                #last arg passed in from GUI for filecmp shallow=True/False
                                if func.fCompare(dstDirFile, srcDirFile, cmp_Mode, hash_Mode, True):#{8
                                    #And its corresponding srcFile is added to srcToCopy list
                                    #By not adding it to the sameFileSrc list
                                    #before the file is re-copied
                                    #dstFile to be kept, but renamed to be same as corresponding srcFile
                                    if dstFnum == 1 and srcFnum == 1:#{9
                                        if dstFile != srcFile:#{10
                                            #This is to check for files with same size, mod-time but different content
                                            #only thing indicates that they are different files is their file names and content
                                            #If file names mismatch then do a file content comparison
                                            #to verify two files are in fact the same, if not then continue
                                            if not func.fCompare(dstDirFile, srcDirFile, cmp_Mode, hash_Mode, False):#{11
                                                continue
                                            #}11
                                            tempRN1 = func.buildPath(dstDir, srcFile, delim)
                                            renameList.append([dstDirFile, tempRN1])
                                            totalDstRename = totalDstRename + 1 #Global variable
                                        #}10
                                        toRemove = False
                                        sameFileSrc.append(srcObjList[d]) #file that is the same
                                        continue
                                    #}9
                                    else:#{9
                                        srcNlist = srcObjList[d].fileNames.copy() 
                                        dstNlist = dstObjList[c].fileNames.copy()
                                        #print(srcNlist)
                                        #print(dstNlist)
                                        toRM = []
                                        for i in srcNlist:#{10
                                            if i in dstNlist:#{11
                                                dstNlist.remove(i)
                                                toRM.append(i) #not to remove elements while looping
                                            #}11
                                        #}10
                                        #When there is a total mismatch in file names, do a file content compare
                                        #to verify two files are in fact the same, if not continue
                                        if len(toRM) == 0:#{10
                                            if not func.fCompare(dstDirFile, srcDirFile, cmp_Mode, hash_Mode, False):#{11
                                                continue
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
                                        continue
                                    #}9
                                #}8
                            #}7
                            #if nothing matches then do nothing
                            #src file will be in srcToCopy list by not being in sameFileSrc list
                            #dst file will add to delete list by toRemove not being set to False
                            #this is the only place to break out of looping srcFileList
                            #coz file size is sorted from small to large
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
        #at1 = datetime.datetime.now()
        #sec1 = at1.second
        #msec1 = at1.microsecond
        #t0 = sec0 + msec0/1000000
        #t1 = sec1 + msec1/1000000
        #dt = t1 - t0
        #profile2.append(dt)
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
    esList = func.listExl(exlSrcDir, delim)
    edList = func.listExl(exlDstDir, delim)
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
        global profile1Num
        global profile2Num 
        global profile3Num
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

        #code profiling
        profile1.clear()
        profile2.clear()
        profile3.clear()
        profile1Num = 0
        profile2Num = 0
        profile3Num = 0
        
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
        #print(profile1)
        #print(profile2)
        #profile1Num = sum(profile1)/len(profile1)
        #profile2Num = sum(profile2)/len(profile2)
        #print('step 1 profile: ' + str(profile1Num))
        #print('step 2 profile: ' + str(profile2Num))
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
        rets = len(rmtreeList)+len(copytreeList)+len(renameList)+\
               len(removeList)+len(checkNcopyList)
        if rets == 0:#{2
            return 0
        #}2
        else:#{2
            return 1
        #}2
    #}1
#}0

if __name__ == '__main__':#{0
    print('Module has no standalone function')
#}0
