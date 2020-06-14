
class entity:#{0
    def __init__(self, srcDir, dstDir, delim):#{1
        if srcDir == dstDir:#{2
            checkTar = srcDir.split(delim)
            if checkTar[len(checkTar)-1] == '':#{3
                del checkTar[len(checkTar)-1]
            #}3
            if delim == '/':#{3
                dst_drive = '/'
            #}3
            else:#{3
                dst_drive = checkTar[0]
            #}3
            targetDir = delim.join(checkTar)
            self.dst_drive = dst_drive
            self.targetDir = targetDir
            self.srcDir = ''
            self.dstDir = ''
        #}2
        else:#{2
            checkSrc = srcDir.split(delim)
            if checkSrc[len(checkSrc)-1] == '':#{3
                del checkSrc[len(checkSrc)-1]
            #}3
            srcDir = delim.join(checkSrc)
            checkDst = dstDir.split(delim)
            if checkDst[len(checkDst)-1] == '':#{3
                del checkDst[len(checkDst)-1]
            #}3
            if delim == '/':#{3
                dst_drive = '/'
            #}3
            else:#{3
                dst_drive = checkDst[0]
            #}3
            dstDir = delim.join(checkDst)
            self.dst_drive = dst_drive
            self.srcDir = srcDir
            self.dstDir = dstDir
            self.targetDir = ''
        #}2
    #}1
#}0
class hashItem:#{0
    def __init__(self, key, name, mtime, count):#{1
        self.key = key
        self.fileName = name
        self.rename = '' #to store new name
        self.modTime = mtime
        self.valTime = 0 #record latest validation time (Not used)
        self.counter = count #for validation function
        self.toRename = 0 #for renamed files
        self.toKeep = 0 
        self.toReview = 0 #for modified or corrupted files
    #}1
#}0
