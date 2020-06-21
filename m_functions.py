import hashlib
import filecmp
import m_class_entity as entityc

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
def fCompare(f1, f2, method):#{0
    if method == 0:#{1
        #filecmp shallow=True - compare file metadata(os.stat)
        #filecmp shallow=False - compare file content (Recommanded)
        return filecmp.cmp(f1, f2, shallow=False)
    #}1
    elif method == 1:#{1
        fileHash1 = hasher(f1, False, hash_Mode)
        fileHash2 = hasher(f2, False, hash_Mode)
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
    #Clear the readonly bit and reattempt the removal
    os.chmod(path, stat.S_IWRITE)
    func(path)
#}0
if __name__ == '__main__':#{0
    print('Module has no standalone function')
#}0
