import m_functions as func
import m_class_entity as entityc
from m_gVar import * #contains global variables

#remove targeted dir and file
def delete(isFolder):#{0
    global delCount
    delCount = 0
    print('Removing target..')
    if isFolder == True:#{1
        for tarDir in delDFList:#{2
            try:#{3
                shutil.rmtree(tarDir)
                delCount = delCount + 1
            #}3
            except:#{3
                print('dir removal error on: ' + tarDir)
                continue
            #}3
        #}2
    #}1
    else:#{1
        for tarFile in delDFList:#{2
            try:#{3
                os.remove(tarFile)
                delCount = delCount + 1
            #}3
            except OSError:#{3
                print('OSError during file removal')
                continue
            #}3
        #}2
    #}1
    delDFList.clear()
    print('Completed, ' + str(delCount) + ' instances removed.\n')
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
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
            return True
        #}2
        else:#{2
            print("Test failed")
            shutil.rmtree(testTarDir[0], onerror=func.remove_readonly)
            return False
        #}2
    #}1
    else:#{1
        delDirFile(tarDir, "testFile.txt", isFolder, '')
        delete(isFolder)
        if os.path.isdir(testTarDir[1]):#{2
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
#return number of items deleted, if an exception is thrown then return 0 immediately
#Do not delete any folder starts with '.' and files like '.sys' and '.dll'
#targetName is full pathname, targetType is True for folder..
def delDirFile(wd, targetName, isFolder, exlDir):#{0
    entity0 = entityc.entity(wd, wd, delim)
    wd = entity0.targetDir
    eList = func.listExl(exlDir, delim)
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
        for i in delDFList:#{2
            print(str(i))
        #}2
        print('Analysis completed\n')
        return cpCounter
    #}1
#}0
