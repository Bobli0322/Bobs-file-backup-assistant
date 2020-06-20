import hashlib

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
if __name__ == '__main__':#{0
    print('Module has no standalone function')
#}0
