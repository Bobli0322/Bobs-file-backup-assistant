import os
import shutil
import m_functions as func

#Check if dst exists before copy file
#If exists then modify name to prevent overwrite
#return False if an OSError exception is thrown otherwise return True
def checkNcopy(srcDir, dstDir, srcName, dstName, delim):#{0
    try:#{1
        cpCounter = 0 
        while os.path.isfile(func.buildPath(dstDir, dstName, delim)):#{2
            #modift fileName assign to new string var
            cpCounter = cpCounter + 1
            dstName = dstName.split('.')
            dstName.insert(len(dstName)-1, str(cpCounter))
            dstName[0:len(dstName)-1] = ['-'.join(dstName[0:len(dstName)-1])]
            dstName = '.'.join(dstName)
        #}2
        src = func.buildPath(srcDir, srcName, delim)
        dst = func.buildPath(dstDir, dstName, delim)
        shutil.copy2(src, dst)
        return True
    #}1
    except OSError:#{1
        print('OSError during file copying')
        return False
    #}1
#}0
#Check if dst exists before move file
#If exists then modify name
#return False if an OSError exception is thrown otherwise return True
def checkNmove(srcDir, dstDir, srcName, dstName, delim):#{0
    try:#{1
        cpCounter = 0 
        while os.path.isfile(func.buildPath(dstDir, dstName, delim)):#{2
            #modift fileName assign to new string var
            cpCounter = cpCounter + 1
            dstName = dstName.split('.')
            dstName.insert(len(dstName)-1, str(cpCounter))
            dstName[0:len(dstName)-1] = ['-'.join(dstName[0:len(dstName)-1])]
            dstName = '.'.join(dstName)
        #}2
        src = func.buildPath(srcDir, srcName, delim)
        dst = func.buildPath(dstDir, dstName, delim)
        shutil.move(src, dst)
        return True
    #}1
    except OSError:#{1
        print('OSError during file moving')
        return False
    #}1
#}0
if __name__ == '__main__':#{0
    print('Module has no standalone function')
#}0

    
