import csv
import m_functions as func
import m_class_entity as entityc
from m_gVar import * #contains global variables

#Hash key, file name, modification date 

#cwd = os.getcwd()
#now = datetime.datetime.now()
#now = str(now)

def mergeRecord(tarDir, merFile, fileList):#{0
    if not os.path.isfile(merFile):#{1
        print('Merge file not found')
        return 0
    #}1
    else:#{1
        merRet = loadRecord(merFile)
        if merRet == 0:#{2
            print('Merge file reading error')
            return 0
        #}2
        else:#{2
            merDir = merRet[0]
            merTable = merRet[2]
            counter = 0
            if tarDir != merDir:#{3
                print('Path naming discrepancy')
                return 0
            #}3
            else:#{3
                for i in range(len(merTable)):#{4
                    #fName = fileList[i].split(delim)
                    #fName = fName[len(fName)-1]
                    fName = fileList[i].replace(tarDir, '')
                    if delim == '/':#{5
                        fName = fName.replace(delim, '\\')
                    #}5
                    mName = merTable[i].fileName
                    if fName != mName:#{5
                        print('Record entry mismatch')
                        return 0
                    #}5
                    else:#{5
                        counter = counter + 1
                    #}5
                #}4
                ret = [counter, merTable]
                return ret
            #}3
        #}2
    #}1
#}0
#Load data from file and opt for CSV record generation
def genRecord(tarDir, merFile):#{0
    exDir = []
    file_list = func.listFile(tarDir, delim, exDir, thumbs)
    if len(file_list) == 0:#{1
        print('Target directory is empty')
        return 0
    #}1
    else:#{1
        merRes = 0
        mCounter = 0
        mTable = []
        if merFile != '':#{2
            merRes = mergeRecord(tarDir, merFile, file_list)
            if type(merRes) == list:#{3
                mCounter = merRes[0]
                mTable = merRes[1]
            #}3
            else:#{3
                merRes = 1
            #}3
        #}2
        if merRes == 1:#{2
            print('Record merge failed')
            return 0
        #}2
        else:#{2
            print('Generating CSV record file from: ' + tarDir)
            now = datetime.datetime.now()
            now = str(now)
            now = now.replace(':', '-')
            tarName = tarDir.split(delim)
            tarName = tarName[len(tarName)-1]
            tarName = 'checksum_' + tarName + '_' + now + '.csv'
            #utf8 - unicode, a is to append
            with open(cwd + delim + tarName, 'a', encoding='utf8') as outputFile:#{3
                outputFile.write('start_checksum_hash_table_/' + tarDir + '/' + now + '\n')
                if merRes != 0:#{4
                    print('Continue from: ' + merFile)
                    print('Of ' + str(len(mTable)) + ' entries')
                    for i in mTable:#{5
                        iHash = i.key
                        fName = i.fileName
                        modTime = i.modTime
                        tStr = iHash + '/' + fName + '/' + str(modTime) + '/1'
                        outputFile.write(tStr + '\n')
                    #}5
                #}4
                print('Total number of files: ' + str(len(file_list)))
                while mCounter < len(file_list):#{4
                    iHash = func.hasher(file_list[mCounter], False, hash_Mode)
                    #fName = file_list[mCounter].split(delim)
                    #fName = fName[len(fName)-1]
                    fName = file_list[mCounter].replace(tarDir, '')
                    if delim == '/':#{5
                        fName = fName.replace(delim, '\\')
                    #}5
                    #print(fName)
                    modTime = os.path.getmtime(file_list[mCounter])  
                    tStr = iHash + '/' + fName + '/' + str(modTime) + '/1'
                    outputFile.write(tStr + '\n')
                    mCounter = mCounter + 1
                #}4
                outputFile.write('end_checksum_hash_table_/' + tarDir + '/' + now + '\n')
            #}3
            print('CSV record file generated at:')
            print(tarName)
            return 1
        #}2
    #}1
#}0
#Load data from record
def loadRecord(tableFile):#{0
    validFile = tableFile.split('.')
    ext = validFile[len(validFile)-1]
    if ext != 'csv':#{1
        print('Input file must be a CSV file')
        return 0
    #}1
    else:#{1
        count = -1
        data_table = []
        ret_table = []
        with open(tableFile, 'r', encoding='utf8') as csv_table:#{2
            read_table = csv.reader(csv_table, delimiter='/') #read_table is not a list
            read_table = list(read_table)
            headerStr = read_table[0][0]
            footerStr = read_table[-1][0]
            #print(headerStr)
            #print(footerStr)
            if headerStr != 'start_checksum_hash_table_' or footerStr != 'end_checksum_hash_table_':#{3
                print('CSV file header or footer error')
                return 0
            #}3
            else:#{3
                if delim == '/':#{4
                    tt = read_table[0]
                    del tt[0]
                    if tt[len(tt)-1] == '':#{5
                        del tt[-1]
                        del tt[-1]
                    #}5
                    else:#{5
                        del tt[-1]
                    #}5
                    n1 = delim.join(tt)
                    ret_table.append(n1)
                    ret_table.append('')
                #}4
                else:#{4
                    ret_table.append(read_table[0][1])
                    ret_table.append(read_table[0][2])
                #}4
                del read_table[-1]
                del read_table[0]
                for i in read_table:#{4
                    if i[3] == '1':#{5
                        item0 = entityc.hashItem(i[0], i[1], i[2], count)
                        #print(i[1])
                        count = count - 1
                        data_table.append(item0)
                    #}5
                    else:#{5
                        print('CSV file entry format error')
                        return 0
                    #}5
                #}4
                ret_table.append(data_table)
                return ret_table #return record_table
            #}3
        #}2
    #}1
#}0
def dupRecord():#{0
    global genTable
    global recordTable
    genTable_dupList = []
    recordTable_dupList = []
    recordTable.sort(key=lambda x: x.key)
    genTable.sort(key=lambda x: x.key)
    c = 0
    while c < (len(recordTable)-1):#{1
        nc = c + 1
        if recordTable[c].key == recordTable[nc].key:#{2
            fn1 = recordTable[c].fileName
            fn2 = recordTable[nc].fileName
            recordTable_dupList.append(fn1 + ' == ' + fn2)
        #}2
        c = c + 1
    #}1
    c = 0
    while c < (len(genTable)-1):#{1
        nc = c + 1
        if genTable[c].key == genTable[nc].key:#{2
            fn1 = genTable[c].fileName
            fn2 = genTable[nc].fileName
            genTable_dupList.append(fn1 + ' == ' + fn2)
        #}2
        c = c + 1
    #}1
    if len(genTable_dupList) == 0 and len(recordTable_dupList) == 0:#{1
        return 1
    #}1
    else:#{1
        print('Duplicates in original record:')
        for i in recordTable_dupList:#{2
            print(i)
        #}2
        print('Duplicates in new record:')
        for i in genTable_dupList:#{2
            print(i)
        #}2
        return 0
    #}1
#}0
#csvName1 is updating(original) record file, csvName is the new file
def validRecord(csvName, csvName1):#{0
    if not os.path.isfile(csvName) or not os.path.isfile(csvName1):#{1
        print('CSV file missing')
        return 0
    #}1
    elif csvName == csvName1:#{1
        print('Cannot validate a record against itself')
        return 0
    #}1
    else:#{1
        csv0 = loadRecord(csvName)
        csv1 = loadRecord(csvName1)
        if csv0 == 0 or csv1 == 0:#{2
            print('CSV file reading error')
            return 0
        #}2
        else:#{2
            print('Validating ' + csvName1)
            global genTable #only need to specify global when when need to assign
            global recordTable
            global recordDir
            global csvName0
            genTable.clear()
            recordTable.clear()
            recordDir = ''
            csvName0 = ''
            csvName0 = csvName1
            now = datetime.datetime.now()
            now = str(now)
            recordTable = csv1[2]
            genTable = csv0[2]
            recordDir = csv1[0]
            genDir = csv0[0]
            res = dupRecord()
            if res == 0:#{3
                print('Records contain duplicates, cannot update')
                print('Recommend:')
                print('Manually remove duplicates in original record')
                print('Remove duplicates in file, then re-generate new record')
                print('Update original record to fix any discrepancy')
                return 0
            #}3
            else:#{3
                keepCount = 0
                renameCount = 0
                reviewCount = 0
                insertCount = 0
                removeCount = 0
                count = len(genTable) + len(recordTable)
                counter = 0
                toRename = []
                toMod = []
                toCorrupt = [] 
                while counter < count:#{4
                    for i in genTable:#{5
                        i.counter = i.counter + 1
                        cc = i.counter
                        if cc >= 0 and cc < len(recordTable):#{6
                            lHash = recordTable[cc].key
                            iHash = i.key
                            lName = recordTable[cc].fileName
                            iName = i.fileName
                            lmTime = recordTable[cc].modTime
                            imTime = i.modTime
                            if lHash == iHash and lName != iName:#{7 
                                #print(lName + ' => ' + iName)
                                i.toRename = i.toRename + 1 #to rename on record
                                recordTable[cc].toRename = recordTable[cc].toRename + 1
                                recordTable[cc].rename = iName
                                toRename.append([lName, iName])
                                #print(gHash + ' = ' + lHash)
                                renameCount = renameCount + 1
                            #}7
                            elif lName == iName and lHash != iHash:#{7
                                i.toReview = i.toReview + 1 #to review
                                recordTable[cc].toReview = recordTable[cc].toReview + 1
                                if lmTime == imTime:#{8
                                    toCorrupt.append(lName)
                                #}8
                                else:#{8
                                    toMod.append(lName)
                                #}8
                                reviewCount = reviewCount + 1
                            #}7
                            elif lHash == iHash and lName == iName:#{7
                                i.toKeep = i.toKeep + 1
                                recordTable[cc].toKeep = recordTable[cc].toKeep + 1
                                keepCount = keepCount + 1
                            #}7
                            else:#{7
                                if lmTime == imTime and lHash != iHash and lName != iName:#{8
                                    recordTable[cc].toReview = recordTable[cc].toReview + 1
                                    toCorrupt.append(lName)
                                #}8
                            #}7
                        #}6
                    #}5
                    counter = counter + 1
                    #print(str(counter))
                #}4
                #'a' is to append
                with open(cwd + delim + 'checksum_report.txt', 'a', encoding='utf8') as outputFile:#{4
                    outputFile.write(now + ' Checksum: updating ' + recordDir + ' record with ' + genDir + '\n')
                    if len(toRename) != 0:#{5
                        outputFile.write('Records to rename:\n')
                        for i in toRename:#{6
                            outputFile.write('Rename from ' + i[0] + ' to ' + i[1] + '\n')
                        #}6
                    #}5
                    if len(toMod) != 0:#{5
                        outputFile.write('Records modified:\n')
                        for i in toMod:#{6
                            outputFile.write('Review: ' + i + ' (file could be modified)\n')
                        #}6
                    #}5
                    if len(toCorrupt) != 0:#{5
                        outputFile.write('Records corrupted:\n')
                        for i in toCorrupt:#{6
                            outputFile.write('Review: ' + i + ' (file could be corrupted)\n')
                        #}6
                    #}5
                    outputFile.write('Records to remove:\n')
                    for i in recordTable:#{5
                        if i.toKeep == 0 and i.toRename == 0 and i.toReview == 0:#{6
                            removeCount = removeCount + 1
                            outputFile.write('Remove: ' + i.fileName + '\n')
                        #}6
                    #}5
                    outputFile.write('Records to insert:\n')
                    for i in genTable:#{5
                        if i.toKeep == 0 and i.toRename == 0 and i.toReview == 0:#{6
                            insertCount = insertCount + 1
                            outputFile.write('Insert: ' + i.fileName + '\n')
                        #}6
                    #}5
                    outputFile.write('Checksum report finished\n\n')
                #}4
                ret = renameCount + insertCount + removeCount
                print('Validation finished')
                print('To keep: ' + str(keepCount))
                print('To rename: ' + str(renameCount))
                print('To review: ' + str(reviewCount))
                print('To insert: ' + str(insertCount))
                print('To remove: ' + str(removeCount))
                if ret == 0:#{4
                    print('No auto update')
                #}4
                else:#{4
                    print('Click update button to auto update')
                #}4
                print('Find checksum validation report in: ' + cwd + delim + 'checksum_report.txt')
                return ret
            #}3
        #}2
    #}1
#}0
#Generate a new CSV file with time stamp with record_table dir
def updateRecord(isPartial):#{0
    act = 0
    for i in recordTable:#{1
        if i.toKeep == 0 and i.toRename == 0 and i.toReview == 0:#{2
            if isPartial == False:#{3
                recordTable.remove(i)
                act = act + 1
            #}3
        #}2
        elif i.toRename > 0:#{2
            i.fileName = i.rename
            act = act + 1
        #}2
    #}1
    for i in genTable:#{1
        if i.toKeep == 0 and i.toRename == 0 and i.toReview == 0:#{2
            recordTable.append(i)
            act = act + 1
        #}2
    #}1
    if act > 0:#{1
        recordTable.sort(key=lambda x: x.fileName)
        print('Updating CSV record: ' + csvName0)
        now = datetime.datetime.now()
        now = str(now)
        #csvName0 is the full path of updating record file user specified
        #w is to write or overwrite
        with open(csvName0, 'w', encoding='utf8') as outputFile:#{2
            outputFile.write('start_checksum_hash_table_/' + recordDir + '/' + now + '\n')
            for i in recordTable:#{3
                tStr = str(i.key) + '/' + str(i.fileName) + '/' + str(i.modTime) + '/1'
                outputFile.write(tStr + '\n')
            #}3
            outputFile.write('end_checksum_hash_table_/' + recordDir + '/' + now + '\n')
        #}2
        print('Record update finished')
        return 1
    #}1
    else:#{1
        print(csvName0 + ' is already up-to-date')
        return 0
    #}1
#}0
                
#Rule for file storage
#- No duplicated files
#- No reused file names
#Main purpose of this code is to detect corrupted file against a checksum record 
#Also detect changes need to be made to the checksum record like renamed files + modified files
#Checksum record is stored in CSV file
#
#First function is to load data from a directory and generate CSV record file
#Second function is to validate original checksum record against the newly generated record
#
#Complete record update both insert and remove records from the original record
#Partial record update only insert but never remove entries
#
#Before updating the record, generate a report stating
#   - what to rename, insert, remove, and review
#
#When loading CSV file, check header, footer, and everything inbetween is properly formatted
#before doing anything else
if __name__ == '__main__':#{0
    print('standalone function')
#}0
