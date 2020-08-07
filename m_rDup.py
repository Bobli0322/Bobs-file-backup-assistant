import m_functions as func
import m_class_entity as entityc
from m_gVar import * #contains global variables

def testDup(tarDir, mode, cmpMode):#{0
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
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
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
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
            return False
        #}2
    #}1
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
            print('OSError during file removal')
            continue
        #}2
    #}1
    dupFileList.clear()
    print('Completed, ' + str(dupFileRM) + ' files removed.\n')
#}0
def dup_size_est():#{0
    fsize = 0
    if len(dupFileList) > 0:#{1
        for i in dupFileList:#{2
            fs = os.path.getsize(i)
            fsize = fsize + fs
        #}2
        fsize_gb = fsize*gb_conv
        if fsize_gb < 1:#{2
            fsize_mb = fsize*mb_conv
            print('Space saving: ' + str(fsize_mb) + 'MB')
        #}2
        else:#{2
            print('Space saving: ' + str(fsize_gb) + 'GB')
        #}2
    #}1
#}0
#globalCompare compares across folders
def globalCompare(targetDir, cmpMode, exlDir):#{0
    entity0 = entityc.entity(targetDir, targetDir, delim)
    targetDir = entity0.targetDir
    eList = func.listExl(exlDir, delim)
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
        objList = []
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
            #}3
            else:#{3
                for fileName in fileNames:#{4
                    if fileName.lower() != thumbs.lower():#{5
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
                cMode = 'Filecmp.cmp (shallow=False compare file content)'
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
            fileList.sort(key=lambda x: x[2]) #sort fileList against fSize (file size)
            #loadFileObj populates objList list with list of duplicated files
            func.loadFileObj(fileList, objList, True, delim, cmpMode, hash_Mode)
            print('Finding duplicated files across all sub-directories...')
            if len(objList) != 0:#{3
                for i in objList:#{4
                    timeList = []
                    Bvalue = 0
                    Bindex = 0
                    counter = 0
                    for j in range(len(i.fileNames)):#{5
                        if len(i.fileDir) == 1:#{6
                            k = 0
                        #}6
                        else:#{6
                            k = j
                        #}6
                        path = func.buildPath(i.fileDir[k], i.fileNames[j], delim)
                        ct = os.path.getctime(path)
                        at = os.path.getatime(path)
                        timeList.append(ct)
                        timeList.append(at)
                    #}5
                    while counter < len(timeList):#{5
                        if timeList[counter] > Bvalue:#{6
                            Bvalue = timeList[counter]
                            Bindex = counter
                        #}6
                        counter = counter + 1
                    #}5
                    cd = Bindex//2
                    #cr = Bindex%2
                    #print(str(cd))
                    if len(i.fileDir) == 1:#{5
                        k = 0
                    #}5
                    else:#{5
                        k = cd
                    #}5
                    keepath = func.buildPath(i.fileDir[k], i.fileNames[cd], delim)
                    toKeep = 'To keep:\n' + keepath + '\nIn:\n' + keepath + '\n'
                    #print(toKeep)
                    for j in range(len(i.fileNames)):#{5
                        if j != cd:#{6
                            if len(i.fileDir) == 1:#{7
                                k = 0
                            #}7
                            else:#{7
                                k = j
                            #}7
                            toRM = func.buildPath(i.fileDir[k], i.fileNames[j], delim)
                            toKeep = toKeep + toRM + '\n'
                            dupFileList.append(toRM)
                        #}6
                    #}5
                    dupList.append(toKeep)
                    cpCounter = cpCounter + 1
                #}4
            #}3
            filecmp.clear_cache()
            #encoding arg is for writing nonEng char 
            with open(cwd + delim + 'findDupFiles_report.txt', 'a', encoding='utf8') as outputFile:#{3 
                outputFile.write('\n')
                outputFile.write('Target directory: ' + targetDir + '\n')
                outputFile.write('Find duplicated files across all sub-directories\n')
                if len(dupList) > 0:#{4
                    outputFile.write('Files with duplicated content:\n')
                    for i in dupList:#{5
                        outputFile.write(i + '\n')
                    #}5
                #}4
                if len(dupName) > 0:#{4
                    outputFile.write('Files with duplicated names:\n')
                    for i in dupName:#{5
                        outputFile.write(i + '\n')
                    #}5
                #}4
                outputFile.write('Method of file comparison: ' + cMode + '\n')
                outputFile.write('Total file count: ' + str(totalFiles) + '\n')
                outputFile.write('Comparison Ops: ' + str(opCounter) + '\n')
                outputFile.write('Duplicated files: ' + str(cpCounter) + '\n')
                outputFile.write('Duplicated fileNames: ' + str(dnCounter) + '\n')
                outputFile.write('Only files with duplicated content are included in deletion\n')
                outputFile.write('Duplicated file naming require user investigation\n')
                #outputFile.close() #using "with open" auto close file even with exception
            #}3
            print('Method of file comparison: ' + cMode)
            print('Total file count: ' + str(totalFiles))
            print('Duplicated files: ' + str(cpCounter))
            print('Duplicated fileNames: ' + str(dnCounter))
            dup_size_est()
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
    eList = func.listExl(exlDir, delim)
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
            cMode = 'Filecmp.cmp (shallow=False compare file content)'
        #}2
        else:#{2
            cMode = 'Hashlib (Checksum:SHA256)'
        #}2
        print('Finding duplicated files within each sub-directory...') 
        for folderName, subFolders, fileNames in os.walk(targetDir):#{2
            fileList = []
            objList = []
            c = 0
            for eDir in eList:#{3
                if eDir in folderName:#{4
                    isExl = True
                #}4
            #}3
            if isExl == True:#{3
                isExl = False
            #}3
            else:#{3
                for fileName in fileNames:#{4
                    if fileName.lower() != thumbs.lower():#{5
                        totalFiles = totalFiles + 1
                        fSize = os.path.getsize(func.buildPath(folderName, fileName, delim))
                        #fileList.append([fileName,fsize])
                        fileList.append([folderName, fileName, fSize])
                    #}5
                #}4
                fileList.sort(key=lambda x: x[2])
                #loadFileObj populates objList list with list of duplicated files
                func.loadFileObj(fileList, objList, True, delim, cmpMode, hash_Mode)
                ##for i in objList:#{4
                ##    ts = i.fileNames
                ##    print(ts)
                ##}4
                ##print('\n')
                if len(objList) != 0:#{4
                    for i in objList:#{5
                        timeList = []
                        Bvalue = 0
                        Bindex = 0
                        counter = 0
                        for j in i.fileNames:#{6
                            path = func.buildPath(i.fileDir[0], j, delim)
                            ct = os.path.getctime(path)
                            at = os.path.getatime(path)
                            timeList.append(ct)
                            timeList.append(at)
                        #}6
                        while counter < len(timeList):#{6
                            if timeList[counter] > Bvalue:#{7
                                Bvalue = timeList[counter]
                                Bindex = counter
                            #}7
                            counter = counter + 1
                        #}6
                        cd = Bindex//2
                        #cr = Bindex%2
                        #print(str(cd))
                        toKeep = 'To keep: ' + i.fileNames[cd] + ', to remove:'
                        #print(toKeep)
                        for j in range(len(i.fileNames)):#{6
                            if j != cd:#{7
                                toKeep = toKeep + ' ' + i.fileNames[j]
                                toRM = func.buildPath(i.fileDir[0], i.fileNames[j], delim)
                                dupFileList.append(toRM)
                            #}7
                        #}6
                        toKeep = toKeep + ', at ' + i.fileDir[0]
                        dupList.append(toKeep)
                        cpCounter = cpCounter + 1
                    #}5
                #}4
            #}3
        #}2
        filecmp.clear_cache()
        #encoding arg is for writing nonEng char
        with open(cwd + delim + 'findDupFiles_report.txt', 'a', encoding='utf8') as outputFile:#{2  
            outputFile.write('\n')
            outputFile.write('Target directory: ' + targetDir + '\n')
            outputFile.write('Find duplicated files within each sub-directory\n')
            if len(dupList) > 0:#{3
                outputFile.write('Files with duplicated content:\n')
                for i in dupList:#{4
                    outputFile.write(i + '\n')
                #}4
            #}3
            outputFile.write('Method of file comparison: ' + cMode + '\n')
            outputFile.write('Total file count: ' + str(totalFiles) + '\n')
            outputFile.write('Comparison Ops: ' + str(opCounter) + '\n')
            outputFile.write('Duplicated files: ' + str(cpCounter) + '\n')
            #outputFile.close() #using "with open" auto close file even with exception
        #}2
        print('Method of file comparison: ' + cMode)
        print('Total file count: ' + str(totalFiles))
        print('Duplicated files: ' + str(cpCounter))
        dup_size_est()
        print('Please find analysis report in ' + cwd + delim + 'findDupFiles_report.txt')
        print('Analysis completed\n')
        ret = str(totalFiles) + '-0-' + str(cpCounter)
        return ret
    #}1
#}0
if __name__ == '__main__':#{0
    print('Module has no standalone function')
    #dd = '\\'
    #tt = 'Thumbs.db' 
    ee = ''
    #tar = 'D:\\tempDir\\JobAppHis'
    tar = 'P:\\testDir1'
    #tar = 'P:\\MyDoc\\Programming\\Audio\\Proj\\sSound_data\\e08\\d00'
    #(fileList, objList, isDup, delim, cmp_Mode, hash_Mode)
#}0
