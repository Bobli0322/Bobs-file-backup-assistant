import os
import hashlib
import filecmp
import m_class_entity as entityc

#Nested loops
#Return a list that contains file path for tar(target dir)
#excluding dir path in exlDir
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
#}0
