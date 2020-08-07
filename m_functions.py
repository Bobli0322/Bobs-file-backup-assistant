import os
import hashlib
import filecmp
import m_class_entity as entityc

#Nested loops
#Return a list that contains file path for tar(target dir)
#excluding dir path in exlDir
#excluding Thumbs.db files
#File count would be different from windows folder property number
#because fold property count Thumbs.db files as well
def listFile(tar, delim, exlDir, thumbs):#{0
    tempList = []
    tempList2= []
    fList = []
    fileList = []
    isExDir = False
    elements = os.listdir(tar)
    exDir = listExl(exlDir, delim)
    if len(elements) != 0:#{1
        for e in elements:#{2
            if e.lower() != thumbs.lower():#{3
                f = tar + delim + e
                for edDir in exDir:#{4
                    if edDir in f:#{5
                        isExDir = True
                    #}5
                #}4
                if isExDir == True:#{4
                    isExDir = False
                #}4
                else:#{4
                    #print(f)
                    if os.path.isdir(f):#{5
                        #fg = f[1:]
                        fList.append(f)
                        tempList.append(f)
                        #listSrc(f)
                    #}5
                    elif os.path.isfile(f):#{5
                        fileList.append(f)
                    #}5
                #}4
            #}3
        #}2
    #}1
    while len(tempList) != 0:#{1
        tempList2 = tempList[:] #list slicing is faster than copy.copy
        tempList.clear()
        for i in tempList2:#{2
            elements = os.listdir(i)
            if len(elements) != 0:#{3
                for j in elements:#{4
                    if j.lower() != thumbs.lower():#{5
                        f = i + delim + j
                        for edDir in exDir:#{6
                            if edDir in f:#{7
                                isExDir = True
                            #}7
                        #}6
                        if isExDir == True:#{6
                            isExDir = False
                        #}6
                        else:#{6
                            #print(f)
                            if os.path.isdir(f):#{7
                                fList.append(f)
                                tempList.append(f)
                            #}7
                            elif os.path.isfile(f):#{7
                                fileList.append(f)
                            #}7
                        #}6
                    #}5
                #}4
            #}3
        #}2
    #}1
    return fileList
#}0
#fileList must be sort in order of file size in calling function
def loadFileObj(fileList, objList, isDup, delim, cmp_Mode, hash_Mode):#{0
    if len(fileList) == 0:#{1
        return 0
    #}1
    else:#{1
        sList = []
        strucList = []
        oList = []
        sizeC = 0
        #tCount = 0
        for i in range(len(fileList)):#{2
            if fileList[i][2] != sizeC and sizeC != 0:#{3
                tList = sList.copy()
                strucList.append(tList)
                #print(sList)
                sList.clear()
                sizeC = fileList[i][2]
                sList.append(fileList[i])
                if i == len(fileList)-1:#{4
                    tList = sList.copy()
                    strucList.append(tList)
                #}4
            #}3
            else:#{3
                sizeC = fileList[i][2]
                sList.append(fileList[i])
                if i == len(fileList)-1:#{4
                    tList = sList.copy()
                    strucList.append(tList)
                #}4
            #}3
        #}2
        #for i in strucList:
        #    print(i)
        #    tCount = tCount + len(i)
        #print(str(tCount))
        #tCount = 0
        for i in strucList:#{2
            cmpList = i.copy()
            if len(cmpList) > 1:#{3
                dupIndex = []
                for j in range(len(i)):#{4
                    dIndex = []
                    dirFile0 = buildPath(i[j][0], i[j][1], delim)
                    for k in range(len(cmpList)):#{5
                        dirFile1 = buildPath(cmpList[k][0], cmpList[k][1], delim)
                        if fCompare(dirFile0, dirFile1, cmp_Mode, hash_Mode, False) == True:#{6
                            dIndex.append(j)
                            dIndex.append(k)
                        #}6
                    #}5
                    dIndex = set(dIndex)
                    dIndex = list(dIndex)
                    dIndex.sort()
                    tdIndex = dIndex.copy()
                    dupIndex.append(tdIndex)
                #}4
                tdupIndex = set(tuple(element) for element in dupIndex) #set of tuples
                tdi = []
                for j in tdupIndex:#{4
                    tj = list(j)
                    tdi.append(tj)
                #}4
                for j in tdi:#{4
                    tj = []
                    for k in j:#{5
                        tj.append(i[k])
                    #}5
                    oList.append(tj)
                #}4
            #}3
            else:#{3
                oList.append(cmpList)
            #}3
        #}2
        for i in oList:#{2
            #print(i)
            fNames = []
            fDirs = []
            num = len(i)
            if isDup == True and num == 1:#{3
                continue
            #}3
            else:#{3
                #tCount = tCount + num
                fsize = i[0][2]
                for j in i:#{4
                    fNames.append(j[1])
                #}4
                for j in i:#{4
                    fDirs.append(j[0])
                #}4
                fDir = set(fDirs)
                if len(fDir) == 1:#{4
                    fDir = list(fDir)
                    item0 = entityc.iFile(num, fNames, fDir, fsize)
                #}4
                else:#{4
                    item0 = entityc.iFile(num, fNames, fDirs, fsize)
                #}4
                objList.append(item0)
            #}3
        #}2
        #print(str(tCount))
        return 1
    #}1
#}0
def hasher(tar, isStr, hMode):#{0
    if isStr == True:#{1
        if hMode == 'sha256':#{2
            strHash = hashlib.sha256(tar.encode()).hexdigest()
            return strHash
        #}2
        elif hMode == 'md5':#{2
            strHash = hashlib.md5(tar.encode()).hexdigest()
            return strHash
        #}2
        else:#{2
            return 0
        #}2
    #}1
    else:#{1
        #blocksize = 4096
        blocksize = 65536
        if hMode == 'sha256':#{2
            hasher = hashlib.sha256()
            with open(tar, 'rb') as afile:#{3
                buf = afile.read(blocksize)
                while len(buf) > 0:#{4
                    hasher.update(buf)
                    buf = afile.read(blocksize)
                #}4
            #}3
            fileHash = hasher.hexdigest()
            return fileHash
        #}2
        elif hMode == 'md5':#{2
            hasher = hashlib.md5()
            with open(tar, 'rb') as afile:#{3
                buf = afile.read(blocksize)
                while len(buf) > 0:#{4
                    hasher.update(buf)
                    buf = afile.read(blocksize)
                #}4
            #}3
            fileHash = hasher.hexdigest()
            #print(fileHash)
            return fileHash
        #}2
        else:#{2
            return 0
        #}2
    #}1
#}0
def fCompare(f1, f2, method, hMode, isShallow):#{0
    if method == 0:#{1
        #filecmp shallow=True - compare file metadata(os.stat)
        #filecmp shallow=False - compare file content
        #   (Recommanded if file size is small)
        return filecmp.cmp(f1, f2, shallow=isShallow)
        #return filecmp.cmp(f1, f2)
    #}1
    elif method == 1:#{1
        fileHash1 = hasher(f1, False, hMode)
        fileHash2 = hasher(f2, False, hMode)
        if fileHash1 == fileHash2:#{2
            return True
        #}2
        else:#{2
            return False
        #}2
    #}1
#}0
def listExl(exlDir, delim):#{0
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
def buildPath(path1, path2, delim):#{0
    #retStr = ''
    if type(path1) == list:#{1
        retStr = delim.join(path1)
    #}1
    elif type(path1) == str:#{1
        retStr = path1 + delim + path2
    #}1
    return retStr
#}0
def remove_readonly(func, path, _):#{0
    #This handler to rmtree err is used only for files this program created
    #Clear the readonly bit and reattempt the removal
    print('Clear the readonly bit and reattempt dir removal')
    os.chmod(path, stat.S_IWRITE)
    func(path)
#}0
def dirRemoval_err(func, path, _):#{0
    #This handler to rmtree err is for display each file inside dir
    #notify about the error but take no action
    print('rmtree error: ' + path)
#}0
if __name__ == '__main__':#{0
    print('Module has no standalone function')
    dd = '\\'
    #tt = 'Thumbs.db' 
    #ee = ''
    tar = 'D:\\tempDir\\JobAppHis'
    #tar = 'D:\\MyPics\\gkl\\Rira'
    #tar = 'P:\\MyDoc\\Programming\\Audio\\Proj\\sSound_data\\e08\\d00'
    #res = listFile(tar, dd, ee, tt)
    #n = len(res)
    #print('number of files: ' + str(n))

    sizeList = []
    fileList = []
    objList = []
    for folderName, subFolders, fileNames in os.walk(tar):#{1
        if folderName == tar:#{2
            for fileName in fileNames:#{3
                if fileName.lower() != 'thumbs.db':#{4
                    fsize = os.path.getsize(buildPath(folderName, fileName, '\\'))
                    sizeList.append(fsize)
                    fileList.append([folderName, fileName, fsize])
                #}4
            #}3
        #}2
    #}1
    fileList.sort(key=lambda x: x[2])
    #print(fileList)
    #(fileList, objList, isDup, delim, cmp_Mode, hash_Mode)
    loadFileObj(fileList, objList, True, dd, 0, 'sha256')
    for i in objList:
        ts = i.fileNames
        print(ts)
#}0
