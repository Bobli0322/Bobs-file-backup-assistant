import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import m_FileManager1_7 as cmp
import m_Checksum as cks
import threading
import time
import queue, math, os

#Ver 1.1 For the file backup function, delete files and folers in destination directory
#       that do not exist in source directory, thus create a mirror between source and destination
#       For remove duplicates function, remove duplicates base on file creation and access time
#Ver 1.2 disable all buttons while file operation is happening
#Ver 1.3 Put file opeartion on separate thread apart from GUI main loop
#Ver 1.4 Add call_back function to catch when file operation thread finishes, to display results on screen
#       call_back function is scheduled by root.after function for periodic execution
#Ver 1.4.1 add animation
#Ver 1.5 
#        Add a file explorer for subfolder selection
#        check read/write permission for target folders
#Ver 1.6 (New feature, major rework, Operational tested)
#        For frame1, replaced start button with two buttons
#        1st analyse button -> 2nd sync button
#        This is to accommodate [cmp 1_7] separating data analysis from processing
#
#        Add radio buttons for file sync mode selection
#        remove file extension checkbox from frame2
#
#Ver 1.6.1 (Operational tested)
#        Minor bug fixes
#        Have rename only sync mode
#        Checksum record generation and validation
#        Exclude directories
#        Report on files with same names

#Degree value must convert to radina before calculation
#|a0 b0| |x|
#|a1 b1| |y|
#retX = a0*x+b0*y
#retY = a1*x+b1*y
#+angle = clockwise, -angle = counter-clockwise
def rotatePoint(ori, point, angle):#{0
   x0 = ori[0]
   y0 = ori[1]
   x1 = point[0]
   y1 = point[1]
   x = x1 - x0
   y = y1 - y0
   a0 = math.cos(math.radians(angle))
   a1 = math.sin(math.radians(angle))
   b0 = -math.sin(math.radians(angle))
   b1 = math.cos(math.radians(angle))
   retX = a0*x+b0*y
   retY = a1*x+b1*y
   retX = retX + x0
   retY = retY + y0
   retCoord = (retX, retY)
   return retCoord
#}0

window = tk.Tk()
window.title('Bob\'s File Manager')
window.geometry('565x550')
bitmaps = ["hourglass", "question", "warning"]
points = [11,11,11,33,33,33,33,11]
oriPoint = (22,22)

c = 0
while c < 50:#{0
   window.rowconfigure(c, weight=1)
   window.columnconfigure(c, weight=1)
   c += 1
#}0
n = ttk.Notebook(window)
n.grid(row=1, column=0, columnspan=50, rowspan=50, sticky='NESW')
canvas0 = tk.Canvas(window, width=40, height=40, background="black")
canvas0.grid(column=49, row=4, columnspan=1, sticky='NW')
#canvas0.create_bitmap(17,17,bitmap=bitmaps[0])
#canvas0.create_oval(3,3,30,30)
canvas0.create_polygon(points, fill="red")
f1 = ttk.Frame(n)
f2 = ttk.Frame(n)
f3 = ttk.Frame(n)
f4 = ttk.Frame(n)
n.add(f1, text='File Backup')
n.add(f2, text='Remove Duplicates')
n.add(f3, text='File Deletion')
n.add(f4, text='Checksum')

opResult = queue.Queue()
thread = 0
#----------------Frame 1 variables----------------------------
srcStr = tk.StringVar()
dstStr = tk.StringVar()
exlSrcStr = tk.StringVar()
exlDstStr = tk.StringVar()
var15 = tk.IntVar()  #add V=1, subtract V=2, mirror V=3, V=0 no selection
var16 = tk.IntVar()  #Option for checksum after file transfer

#----------------Frame 2 variables----------------------------
var25 = tk.IntVar() #Global V=1 or local compare V=2, v=0 no selection
tar2Str = tk.StringVar() #string for target dir
exl2Str = tk.StringVar() #string for excluded dir
var26 = tk.IntVar()  #Option for checksum compare

#----------------Frame 3 variables----------------------------
var31 = tk.IntVar() #Folder val=1 or File val=2
typeArg3 = False
tar3Str = tk.StringVar()
exl3Str = tk.StringVar() #string for excluded dir

#----------------Frame 4 variables----------------------------
gen4Str = tk.StringVar()
gen41Str = tk.StringVar()
val41Str = tk.StringVar()
val42Str = tk.StringVar()
var4 = tk.IntVar()

#----------------OS check----------------------------------------
if cmp.delim == '\\':#{0
   print('Current OS: Windows')
#}0
elif cmp.delim == '/':#{0
   print('Current OS: Linux')
#}0
print('Delimiter: ' + cmp.delim) #delim is in m_gVar which cmp module includes

#----------------General functions----------------------------
def disable_Btn():#{0
   btn1.config(state=tk.DISABLED)
   btn12.config(state=tk.DISABLED)
   btn2.config(state=tk.DISABLED)
   btn3.config(state=tk.DISABLED)
   btnClr1.config(state=tk.DISABLED)
   btnClr2.config(state=tk.DISABLED)
   btnClr3.config(state=tk.DISABLED)
   btnSrcf1.config(state=tk.DISABLED)
   btnDstf1.config(state=tk.DISABLED)
   btnDirf2.config(state=tk.DISABLED)
   btnDirf3.config(state=tk.DISABLED)
   entrySrc1.config(state=tk.DISABLED)
   entryDst1.config(state=tk.DISABLED)
   entryTar2.config(state=tk.DISABLED)
   entryTar3.config(state=tk.DISABLED)
   entryName3.config(state=tk.DISABLED)
   rdbtn21.config(state=tk.DISABLED)
   rdbtn22.config(state=tk.DISABLED)
   rdbtn31.config(state=tk.DISABLED)
   rdbtn32.config(state=tk.DISABLED)
   chkb2.config(state=tk.DISABLED)
   btn11.config(state=tk.DISABLED)
   btn22.config(state=tk.DISABLED)
   btn33.config(state=tk.DISABLED)
   rdbtn11.config(state=tk.DISABLED)
   rdbtn12.config(state=tk.DISABLED)
   rdbtn13.config(state=tk.DISABLED)
   chkb1.config(state=tk.DISABLED)
   entryExlSrc.config(state=tk.DISABLED)
   entryExlDst.config(state=tk.DISABLED)
   btnExlSrc.config(state=tk.DISABLED)
   btnExlDst.config(state=tk.DISABLED)
   entryExl2.config(state=tk.DISABLED)
   btnExl2.config(state=tk.DISABLED)
   entryExl3.config(state=tk.DISABLED)
   btnExl3.config(state=tk.DISABLED)
   #Frame 4
   entryGen4.config(state=tk.DISABLED)
   entryValid41.config(state=tk.DISABLED)
   entryValid42.config(state=tk.DISABLED)
   btn4.config(state=tk.DISABLED)
   btn41.config(state=tk.DISABLED)
   btnDirGen4.config(state=tk.DISABLED)
   btnDirVal41.config(state=tk.DISABLED)
   btnDirVal42.config(state=tk.DISABLED)
   btnClr4.config(state=tk.DISABLED)
   entryGen41.config(state=tk.DISABLED)
   btnDirGen41.config(state=tk.DISABLED)
   rdbtn41.config(state=tk.DISABLED)
   rdbtn42.config(state=tk.DISABLED)
   btn42.config(state=tk.DISABLED)
#}0
def enable_Btn():#{0
   btn1.config(state=tk.NORMAL)
   btn12.config(state=tk.NORMAL)
   btn2.config(state=tk.NORMAL)
   btn3.config(state=tk.NORMAL)
   btnClr1.config(state=tk.NORMAL)
   btnClr2.config(state=tk.NORMAL)
   btnClr3.config(state=tk.NORMAL)
   btnSrcf1.config(state=tk.NORMAL)
   btnDstf1.config(state=tk.NORMAL)
   btnDirf2.config(state=tk.NORMAL)
   btnDirf3.config(state=tk.NORMAL)
   entrySrc1.config(state=tk.NORMAL)
   entryDst1.config(state=tk.NORMAL)
   entryTar2.config(state=tk.NORMAL)
   entryTar3.config(state=tk.NORMAL)
   entryName3.config(state=tk.NORMAL)
   rdbtn21.config(state=tk.NORMAL)
   rdbtn22.config(state=tk.NORMAL)
   rdbtn31.config(state=tk.NORMAL)
   rdbtn32.config(state=tk.NORMAL)
   chkb2.config(state=tk.NORMAL)
   entryExlSrc.config(state=tk.NORMAL)
   entryExlDst.config(state=tk.NORMAL)
   btnExlSrc.config(state=tk.NORMAL)
   btnExlDst.config(state=tk.NORMAL)
   entryExl2.config(state=tk.NORMAL)
   btnExl2.config(state=tk.NORMAL)
   entryExl3.config(state=tk.NORMAL)
   btnExl3.config(state=tk.NORMAL)
   btn11.config(state=tk.DISABLED)
   btn22.config(state=tk.DISABLED)
   btn33.config(state=tk.DISABLED)
   rdbtn11.config(state=tk.DISABLED)
   rdbtn12.config(state=tk.DISABLED)
   rdbtn13.config(state=tk.DISABLED)
   chkb1.config(state=tk.DISABLED)
   #Frame 4
   entryGen4.config(state=tk.NORMAL)
   entryValid41.config(state=tk.NORMAL)
   entryValid42.config(state=tk.NORMAL)
   btn4.config(state=tk.NORMAL)
   btn41.config(state=tk.NORMAL)
   btnDirGen4.config(state=tk.NORMAL)
   btnDirVal41.config(state=tk.NORMAL)
   btnDirVal42.config(state=tk.NORMAL)
   btnClr4.config(state=tk.NORMAL)
   entryGen41.config(state=tk.NORMAL)
   btnDirGen41.config(state=tk.NORMAL)
   rdbtn41.config(state=tk.DISABLED)
   rdbtn42.config(state=tk.DISABLED)
   btn42.config(state=tk.DISABLED)
#}0
#if arg2 is empty then only validate arg1
def validArg0(arg1, arg2):#{0
   if arg2 == '':#{1
      if (cmp.delim == '\\' and (not ':' in arg1 or not '\\' in arg1)) or \
         (cmp.delim == '/' and not '/' in arg1):#{2
         return 0
      #}2
      else:#{2
         return 1
      #}2
   #}1
   else:#{1
      if arg1 == arg2:#{2
         return 0
      #}2
      elif (cmp.delim == '\\' and (not ':' in arg1 or not '\\' in arg1)) or \
         (cmp.delim == '/' and not '/' in arg1):#{2
         return 0
      #}2
      elif (cmp.delim == '\\' and (not ':' in arg2 or not '\\' in arg2)) or \
         (cmp.delim == '/' and not '/' in arg2):#{2
         return 0
      #}2
      else:#{2
         return 1
      #}2
   #}1
#}0
def validArg(exlArg):#{0
   ob = []
   cb = []
   if exlArg == '':#{1
      return 1
   #}1
   else:#{1
      if (cmp.delim == '\\' and (not ':' in exlArg or not '\\' in exlArg)) or \
         (cmp.delim == '/' and not '/' in exlArg):#{2
         return 0
      #}2
      for i in range(len(exlArg)):#{2
         if exlArg[i] == '<':
            ob.append(i)
         elif exlArg[i] == '>':
            cb.append(i)
      #}2
      exlArg1 = len(ob)
      exlArg2 = len(cb)
      if exlArg1 != exlArg2:#{2
         return 0
      #}2
      for i in range(exlArg1):#{2
         tl = cb[i] - ob[i]
         if tl < 0:#{3
            return 0
         #}3
      #}2
      return 1
   #}1
#}0
def formatPath(path):#{0
   if cmp.delim == '\\':#{1
      retStr = path.replace('/', '\\')
   #}1
   else:#{1
      retStr = path
   #}1
   return retStr
#}0
def callback():#{0
   global thread #Is this is inside a class then 'self.isThreaded'
   if thread == 1:#{1
      ret = opResult.get()
      #ret = 'Random'
      txt1.insert(tk.END, 'Analysis Completed ' + str(ret) + '\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      btn11.config(state=tk.NORMAL)
      btnClr1.config(state=tk.NORMAL)
      rdbtn11.config(state=tk.NORMAL)
      rdbtn12.config(state=tk.NORMAL)
      rdbtn13.config(state=tk.NORMAL)
      chkb1.config(state=tk.NORMAL)
   #}1
   elif thread == 11:#{1
      txt1.insert(tk.END, 'Sync completed\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   elif thread == 12:#{1
      ret = opResult.get()
      txt1.insert(tk.END, 'Checksum Completed ' + str(ret) + '\n')
      if ret == 1:
         txt1.insert(tk.END, 'Validation successful.\n\n')
      else:
         txt1.insert(tk.END, 'Validation failed.\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   elif thread == 2:#{1
      ret = opResult.get()
      if ret != '':#{2
         ret = ret.split('-')
         totalFiles = int(ret[0])
         dnCounter = int(ret[1])
         cpCounter = int(ret[2])
         txt2.insert(tk.END, 'Analysis completed \n')
         txt2.insert(tk.END, 'Total Files: ' + str(totalFiles) + '\n')
         txt2.insert(tk.END, 'Duplicated fileNames: ' + str(dnCounter) + '\n')
         txt2.insert(tk.END, 'Duplicated files: ' + str(cpCounter) + '\n\n')
         #txt2.insert(tk.END, 'Output File: ' + tarArg + '\\outputFile.txt\n\n')
      #}2
      else:#{2
         txt2.insert(tk.END, 'Error: Target directory not found or is empty\n\n')
      #}2
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      btn22.config(state=tk.NORMAL)
      btnClr2.config(state=tk.NORMAL)
   #}1
   elif thread == 22:#{1
      txt2.insert(tk.END, 'Removal completed\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   elif thread == 3:#{1
      ret = opResult.get()
      txt3.insert(tk.END, 'Analysis completed: ' + str(ret) + ' found\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      btn33.config(state=tk.NORMAL)
      btnClr3.config(state=tk.NORMAL)
   #}1
   elif thread == 33:#{1
      txt3.insert(tk.END, 'Removal completed\n\n')
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   elif thread == 4:#{1
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   elif thread == 41:#{1
      ret = opResult.get()
      if ret == 0:#{2
         enable_Btn()
      #}2
      else:#{2
         rdbtn41.config(state=tk.NORMAL)
         rdbtn42.config(state=tk.NORMAL)
         btn42.config(state=tk.NORMAL)
         btnClr4.config(state=tk.NORMAL)
      #}2
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red") 
   #}1
   elif thread == 42:#{1
      thread = 0
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="red")
      enable_Btn()
   #}1
   else:#{1
      #print('isThreaded: ' + str(thread))
      point1 = points[0:2]
      point2 = points[2:4]
      point3 = points[4:6]
      point4 = points[6:8]
      points[0:2] = rotatePoint(oriPoint, point1, 45)
      points[2:4] = rotatePoint(oriPoint, point2, 45)
      points[4:6] = rotatePoint(oriPoint, point3, 45)
      points[6:8] = rotatePoint(oriPoint, point4, 45)
      canvas0.delete("all")
      canvas0.create_polygon(points, fill="orange")
      window.after(1000, callback)    #Execute evey 1000ms or 1 second
   #}1
#}0

#--------------------Frame 1 Functions-------------------------
def taskF1(srcArg, dstArg, exlSrcArg, exlDstArg):#{0
   global thread
   global opResult
   opResult.put(cmp.backupCopy(srcArg, dstArg, exlSrcArg, exlDstArg))
   #time.sleep(5)
   thread = 1
#}0
def taskF11(iMode1, iCS):#{0
   global thread
   cmp.filing(iMode1, iCS)
   thread = 11
#}0
def taskF12(srcStr, dstStr, exlSrcStr, exlDstStr):#{0
   global thread
   global opResult
   opResult.put(cmp.validate(srcStr, dstStr, exlSrcStr, exlDstStr))
   thread = 12
#}0
def clear_Fields():#{0
   txt1.delete(1.0, tk.END)
   entrySrc1.delete(0, tk.END)
   entryDst1.delete(0, tk.END)
   entryExlSrc.delete(0, tk.END)
   entryExlDst.delete(0, tk.END)
   enable_Btn()
#}0
def browse_Src():#{0
   global srcStr
   filename = filedialog.askdirectory()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      srcStr.set(filename)
   #}1
#}0
def browse_Dst():#{0
   global dstStr
   filename = filedialog.askdirectory()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      dstStr.set(filename)
   #}1
#}0
def browse_ExlSrc():#{0
   global exlSrcStr
   arg = filedialog.askdirectory()
   arg = str(arg)
   if arg != "":#{1
      arg = formatPath(arg)
      arg = '<' + arg + '>'
      ts = exlSrcStr.get()
      arg = ts + arg
      exlSrcStr.set(arg)
   #}1
#}0
def browse_ExlDst():#{0
   global exlDstStr
   arg = filedialog.askdirectory()
   arg = str(arg)
   if arg != "":#{1
      arg = formatPath(arg)
      arg = '<' + arg + '>'
      ts = exlDstStr.get()
      arg = ts + arg
      exlDstStr.set(arg)
   #}1
#}0
def input_Checksum():#{0
   srcArg = str(srcStr.get())
   dstArg = str(dstStr.get())
   exlSrcArg = str(exlSrcStr.get())
   exlDstArg = str(exlDstStr.get())
   #print(srcArg)
   #print(dstArg)
   #text1.insert(tk.END, tStr)
   if srcArg == '' or dstArg == '':#{1
      messagebox.showinfo('Error', 'Please input both src and dst field')
   #}1
   elif validArg0(srcArg, dstArg) == 0:#{1
      messagebox.showinfo('Error', 'Please input valid pathname')
   #}1
   elif not os.path.isdir(srcArg) or not os.path.isdir(dstArg):#{1
      messagebox.showinfo('Error', 'directory not found')
   #}1
   elif validArg(exlSrcArg) == 0 or validArg(exlDstArg) == 0:#{1
      messagebox.showinfo('Error', 'Input parameter invalid')
   #}1
   elif not os.access(srcArg, os.X_OK) or not os.access(dstArg, os.X_OK):
      messagebox.showinfo('Error', 'not enough access right')
   #}1
   else:#{1
      ans = messagebox.askyesno('Confirmation', 'Start checksum?')
      if ans == True:#{2
         disable_Btn()
         txt1.insert(tk.END, 'Checksum ...\n')
         txt1.insert(tk.END, srcArg + ' >> ' + dstArg + '\n')
         threadObj1 = threading.Thread(target=taskF12, args=(srcArg, dstArg, exlSrcArg, exlDstArg))
         #threadObj1.daemon = True
         threadObj1.start()
         callback()
      #}2
   #}1
#}0
def input_sync():#0
   ans = messagebox.askyesno('Confirmation', 'Start backup?')
   if ans == True:#{1
      iMode1 = var15.get()
      iCS = var16.get()
      if iMode1 == 0:#{2
         messagebox.showinfo('Error', 'Please select mode')
      #}2
      else:#{2
         btn11.config(state=tk.DISABLED)
         btnClr1.config(state=tk.DISABLED)
         rdbtn11.config(state=tk.DISABLED)
         rdbtn12.config(state=tk.DISABLED)
         rdbtn13.config(state=tk.DISABLED)
         chkb1.config(state=tk.DISABLED)
         if iMode1 == 3:#{3
            tt = 'Mirror Syncing...\n'
         #}3
         elif iMode1 == 1:#{3
            tt = 'Additive Syncing...\n'
         #}3
         elif iMode1 == 2:#{3
            tt = 'Subtractive Syncing..\n'
         #}3
         txt1.insert(tk.END, tt)
         threadObj1 = threading.Thread(target=taskF11, args=(iMode1, iCS))
         threadObj1.start()
         callback()
      #}2
   #}1
#}0
def input_Valid():#{0
    srcArg = str(srcStr.get())
    dstArg = str(dstStr.get())
    exlSrcArg = str(exlSrcStr.get())
    exlDstArg = str(exlDstStr.get())
    #print(srcArg)
    #print(dstArg)
    #text1.insert(tk.END, tStr)
    if srcArg == '' or dstArg == '':#{1
        messagebox.showinfo('Error', 'Please input both src and dst field')
    #}1
    elif validArg0(srcArg, dstArg) == 0:#{1
        messagebox.showinfo('Error', 'Please input valid pathname')
    #}1
    elif not os.path.isdir(srcArg) or not os.path.isdir(dstArg):#{1
        messagebox.showinfo('Error', 'directory not found')
    #}1
    elif validArg(exlSrcArg) == 0 or validArg(exlDstArg) == 0:#{1
        messagebox.showinfo('Error', 'Input parameter invalid')
    #}1
    #os.X_OK, os.W_OK, os.R_OK
    elif not os.access(srcArg, os.X_OK) or not os.access(dstArg, os.X_OK):#{1
        messagebox.showinfo('Error', 'not enough access right')
    #}1
    elif not cmp.testSync(srcArg, dstArg):#{1
        messagebox.showinfo('Error', 'core function test failed')
    #}1
    else:#{1
        ans = messagebox.askyesno('Confirmation', 'Start analysis?')
        if ans == True:#{2
            disable_Btn()
            txt1.insert(tk.END, 'Analysing...\n')
            txt1.insert(tk.END, srcArg + ' >> ' + dstArg + '\n')
            threadObj1 = threading.Thread(target=taskF1, args=(srcArg, dstArg, exlSrcArg, exlDstArg))
            #threadObj1.daemon = True
            threadObj1.start()
            callback()
        #}2
    #}1
#}0
#-----------End of Frame 1 functions--------------------------------

#------------Frame 2 functions------------------------
def taskF2(tarArg, iMode2, iCS, exl2Arg):#{0
   global thread
   global opResult
   if iMode2 == 1:#{1
      opResult.put(cmp.globalCompare(tarArg, iCS, exl2Arg))
   #}1
   elif iMode2 == 2:#{1
      opResult.put(cmp.localCompare(tarArg, iCS, exl2Arg))
   #}1
   #time.sleep(10)
   thread = 2
#}0
def taskF22():#{0
   global thread
   cmp.dup()
   thread = 22
#}0
def clear_Fields2():#{0
   txt2.delete(1.0, tk.END)
   entryTar2.delete(0, tk.END)
   entryExl2.delete(0, tk.END)
   enable_Btn()
#}0
def browse_Dir2():#{0
   global tar2Str
   filename = filedialog.askdirectory()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      tar2Str.set(filename)
   #}1
#}0
def browse_Exl2():#{0
   global exl2Str
   arg = filedialog.askdirectory()
   arg = str(arg)
   if arg != "":#{1
      arg = formatPath(arg)
      arg = '<' + arg + '>'
      ts = exl2Str.get()
      arg = ts + arg
      exl2Str.set(arg)
   #}1
#}0
def input_dup():#{0
   ans = messagebox.askyesno('Confirmation', 'Start removal?')
   if ans == True:#{1
      btn22.config(state=tk.DISABLED)
      btnClr2.config(state=tk.DISABLED)
      txt2.insert(tk.END, 'Removing duplicated files...\n')
      threadObj1 = threading.Thread(target=taskF22, args=())
      threadObj1.start()
      callback()
   #}1
#}0    
def input_Valid2():#{0
    iMode2 = var25.get()
    iCS = var26.get()
    exl2Arg = str(exl2Str.get())
    tarArg = str(tar2Str.get())
    if tarArg == '':#{1
        messagebox.showinfo('Error', 'Please input target directory')
    #}1
    elif validArg0(tarArg, '') == 0:#{1
        messagebox.showinfo('Error', 'Please input valid pathname')
    #}1
    elif iMode2 == 0:#{1
        messagebox.showinfo('Error', 'Please select operation mode')
    #}1
    elif not os.path.isdir(tarArg):#{1
        messagebox.showinfo('Error', 'directory not found')
    #}1
    elif validArg(exl2Arg) == 0:#{1
        messagebox.showinfo('Error', 'Input parameter invalid')
    #}1
    elif not os.access(tarArg, os.X_OK):
        messagebox.showinfo('Error', 'not enough access right')
    #}1
    elif not cmp.testDup(tarArg, iMode2, iCS):#{1
        messagebox.showinfo('Error', 'core function test failed')
    #}1
    else:#{1
        ans = messagebox.askyesno('Confirmation', 'Start analysis?')
        if ans == True:#{2
            disable_Btn()
            totalFiles = 0
            opCounter = 0
            cpCounter = 0
            txt2.insert(tk.END, 'Analysing duplicated files...\n')
            if iMode2 == 1:#{3
                txt2.insert(tk.END, 'Global mode\n')
            #}3
            elif iMode2 == 2:#{3
                txt2.insert(tk.END, 'Local mode\n')
            #}3
            threadObj2 = threading.Thread(target=taskF2, args=(tarArg, iMode2, iCS, exl2Arg))
            threadObj2.start()
            callback()
        #}2
    #}1
#}0            
#-------------End of Frame 2 functions----------------------------------

#-------------Frame 3 functions-----------------------------------------
def taskF3(tarArg, nameArg, typeArg3, exl3Arg):#{0
   global thread
   global opResult
   opResult.put(cmp.delDirFile(tarArg, nameArg, typeArg3, exl3Arg))
   #time.sleep(5)
   thread = 3
#}0
def taskF33():#{0
   global thread
   cmp.delete(typeArg3)
   thread = 33
#}0
def clear_Fields3():#{0
   txt3.delete(1.0, tk.END)
   entryTar3.delete(0, tk.END)
   entryName3.delete(0, tk.END)
   entryExl3.delete(0, tk.END)
   enable_Btn()
#}0
def browse_Dir3():#{0
   global tar3Str
   filename = filedialog.askdirectory()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      tar3Str.set(filename)
   #}1
#}0
def browse_Exl3():#{0
   global exl3Str
   arg = filedialog.askdirectory()
   arg = str(arg)
   if arg != "":#{1
      arg = formatPath(arg)
      arg = '<' + arg + '>'
      ts = exl3Str.get()
      arg = ts + arg
      exl3Str.set(arg)
   #}1
#}0
def input_del():#{0
   ans = messagebox.askyesno('Confirmation', 'Start deletion?')
   if ans == True:#{1
      btn33.config(state=tk.DISABLED)
      btnClr3.config(state=tk.DISABLED)
      txt3.insert(tk.END, 'Removing target...\n')
      threadObj1 = threading.Thread(target=taskF33, args=())
      threadObj1.start()
      callback()
   #}1
#}0
def input_Valid3():#{0
    global typeArg3
    isFolder = var31.get()
    tarArg = str(tar3Str.get())
    exl3Arg = str(exl3Str.get())
    nameArg = str(entryName3.get())
    if isFolder == 1:#{1
        typeArg3 = True
    #}1
    elif isFolder == 2:#{1
        typeArg3 = False
    #}1    
    if tarArg == '' or nameArg == '':#{1
        messagebox.showinfo('Error', 'Please input to both fields')
    #}1
    elif validArg0(tarArg, '') == 0:#{1
        messagebox.showinfo('Error', 'Please input valid pathname')
    #}1
    elif isFolder == 0:#{1
        messagebox.showinfo('Error', 'Please choose folder or file')
    #}1
    elif not os.path.isdir(tarArg):#{1
        messagebox.showinfo('Error', 'directory not found')
    #}1
    elif validArg(exl3Arg) == 0:
        messagebox.showinfo('Error', 'Input parameter invalid')
    #}1
    elif not os.access(tarArg, os.X_OK):
        messagebox.showinfo('Error', 'not enough access right')
    #}1
    elif not cmp.testDel(tarArg, typeArg3):#{1
        messagebox.showinfo('Error', 'core function test failed')
    #}1
    else:#{1
        ans = messagebox.askyesno('Confirmation', 'Start analysis?')
        if ans == True:#{2
            disable_Btn()
            txt3.insert(tk.END, 'Analysing target...\n')
            threadObj3 = threading.Thread(target=taskF3, args=(tarArg, nameArg, typeArg3, exl3Arg))
            threadObj3.start()
            callback()
        #}2
    #}1
#}0            
#--------------End of Frame 3 functions---------------------------------

#-------------Frame 4 functions-----------------------------------------
def clear_Fields4():#{0
   entryGen4.delete(0, tk.END)
   entryGen41.delete(0, tk.END)
   entryValid41.delete(0, tk.END)
   entryValid42.delete(0, tk.END)
   enable_Btn()
#}0
def task_gen(gen4Arg, gen41Arg):#{0
   global thread
   res = cks.genRecord(gen4Arg, gen41Arg)
   thread = 4
#}0
def task_val(val41Arg, val42Arg):#{0
   global thread
   global opResult
   opResult.put(cks.validRecord(val42Arg, val41Arg)) #val41 is original record
   thread = 41
#}0
def task_upd(isPartial):#{0
   global thread
   #isPartial == 1-Full, 2-Partial
   if isPartial == 1:#{1
      isPart = False
   #}1
   elif isPartial == 2:#{1
      isPart = True
   #}1
   ret = cks.updateRecord(isPart)
   thread = 42
#}0
def gen_record():#{0
   gen4Arg = str(gen4Str.get())
   gen41Arg = str(gen41Str.get())
   #print(gen4Arg)
   if gen4Arg == '':#{1
      messagebox.showinfo('Error', 'Please input directory')
   #}1
   elif validArg0(gen4Arg, '') == 0:#{1
      messagebox.showinfo('Error', 'Please input valid pathname')
   #}1
   elif not os.path.isdir(gen4Arg):#{1
      messagebox.showinfo('Error', 'directory not found')
   #}1
   elif not os.access(gen4Arg, os.R_OK):
      messagebox.showinfo('Error', 'not enough access right')
   #}1
   else:#{1
      ans = messagebox.askyesno('Confirmation', 'Start CSV generation?')
      if ans == True:#{2
         disable_Btn()
         threadObj4 = threading.Thread(target=task_gen, args=(gen4Arg, gen41Arg))
         threadObj4.start()
         callback()
      #}2
   #}1
#}0
def analyse_CSV():#{0
   val41Arg = str(val41Str.get())
   val42Arg = str(val42Str.get())
   #print(gen4Arg)
   if val41Arg == '' or val42Arg == '':#{1
      messagebox.showinfo('Error', 'Please input directory')
   #}1
   elif validArg0(val41Arg, val42Arg) == 0:#{1
      messagebox.showinfo('Error', 'Please input valid pathname')
   #}1
   elif not os.path.isfile(val41Arg) or not os.path.isfile(val42Arg):#{1
      messagebox.showinfo('Error', 'file not found')
   #}1
   elif not os.access(val41Arg, os.R_OK) or not os.access(val42Arg, os.R_OK):
      messagebox.showinfo('Error', 'not enough access right')
   #}1
   else:#{1
      ans = messagebox.askyesno('Confirmation', 'Start record validation?')
      if ans == True:#{2
         disable_Btn()
         threadObj4 = threading.Thread(target=task_val, args=(val41Arg, val42Arg))
         threadObj4.start()
         callback()
      #}2
   #}1
#}0
def update_CSV():#{0
   var4Arg = var4.get() #1-Full, 2-Partial
   if var4Arg == 0:#{1
      messagebox.showinfo('Error', 'Please select mode')
   #}1
   else:#{1
      ans = messagebox.askyesno('Confirmation', 'Start record validation?')
      if ans == True:#{2
         #disable_Btn()
         rdbtn41.config(state=tk.DISABLED)
         rdbtn42.config(state=tk.DISABLED)
         btn42.config(state=tk.DISABLED)
         btnClr4.config(state=tk.DISABLED)
         threadObj4 = threading.Thread(target=task_upd, args=(var4Arg,))
         threadObj4.start()
         callback()
      #}2
   #}1
#}0
def browse_DirGen4():#{0
   global gen4Str
   filename = filedialog.askdirectory()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      gen4Str.set(filename)
   #}1
#}0
def browse_DirGen41():#{0
   global gen41Str
   filename = filedialog.askopenfilename()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      gen41Str.set(filename)
   #}1
#}0
def browse_DirVal41():#{0
   global val41Str
   filename = filedialog.askopenfilename()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      val41Str.set(filename)
   #}1
#}0
def browse_DirVal42():#{0
   global val42Str
   filename = filedialog.askopenfilename()
   filename = str(filename)
   if filename != "":#{1
      filename = formatPath(filename)
      val42Str.set(filename)
   #}1
#}0
#--------------End of Frame 4 functions---------------------------------

# -----------Frame 1 Layouts---------------------
# LABEL
lbl1 = tk.Label(f1, text='Welcome to file backup')
lbl1.grid(column=0, row=0, columnspan=4, sticky='EW')
#lbl1 = tk.Label(text='Welcome Bob\'s backup program')

#Some text to explain function and usage
lblExp11 = tk.Label(f1, text='Destination directory is mirrored to source directory, \
except for duplicated files')
lblExp11.grid(column=0, row=1, columnspan=4, sticky='W')
lblExp12 = tk.Label(f1, text='Including all sub-directories')
lblExp12.grid(column=0, row=2, columnspan=4, sticky='W')

# LABEL
lblSrc1 = tk.Label(f1, text='Backup from:')
lblSrc1.grid(column=0, row=3)

lblExlSrc = tk.Label(f1, text='Excluding:')
lblExlSrc.grid(column=0, row=4)

# Entry field
entrySrc1 = tk.Entry(f1, textvariable=srcStr)
entrySrc1.grid(column=1, row=3, columnspan=4, sticky='EW')

# LABEL
lblDst1 = tk.Label(f1, text='Backup to:')
lblDst1.grid(column=0, row=5)

lblExlDst = tk.Label(f1, text='Excluding:')
lblExlDst.grid(column=0, row=6)

# Entry field
entryDst1 = tk.Entry(f1, textvariable=dstStr)
entryDst1.grid(column=1, row=5, columnspan=4, sticky='EW')

# Entry field for excluded src directories
entryExlSrc = tk.Entry(f1, textvariable=exlSrcStr)
entryExlSrc.grid(column=1, row=4, columnspan=4, sticky='EW')

# Entry field for excluded dst directories
entryExlDst = tk.Entry(f1, textvariable=exlDstStr)
entryExlDst.grid(column=1, row=6, columnspan=4, sticky='EW')

rdbtn11 = tk.Radiobutton(f1, text='Addition', variable=var15, value=1)
rdbtn11.grid(column=1, row=7, sticky='W')
rdbtn11.config(state=tk.DISABLED)

rdbtn12 = tk.Radiobutton(f1, text='Rename', variable=var15, value=2)
rdbtn12.grid(column=2, row=7, sticky='W')
rdbtn12.config(state=tk.DISABLED)

rdbtn13 = tk.Radiobutton(f1, text='Mirror', variable=var15, value=3)
rdbtn13.grid(column=3, row=7, sticky='W')
rdbtn13.config(state=tk.DISABLED)

chkb1 = tk.Checkbutton(f1, text='Checksum', variable=var16)
chkb1.grid(column=4, row=7)
chkb1.config(state=tk.DISABLED)

btn1 = tk.Button(f1, text='Analyse', bg='blue',command=input_Valid)
btn1.grid(column=0, row=8)

btn11 = tk.Button(f1, text='Sync', bg='green',command=input_sync)
btn11.grid(column=0, row=8, sticky='N')
btn11.config(state=tk.DISABLED)

btn12 = tk.Button(f1, text='Checksum', bg='orange',command=input_Checksum)
btn12.grid(column=0, row=8, sticky='S')

btnExlSrc = tk.Button(f1, text='Exclude', bg='purple',command=browse_ExlSrc)
btnExlSrc.grid(column=5, row=4, sticky='N')

btnExlDst = tk.Button(f1, text='Exclude', bg='purple',command=browse_ExlDst)
btnExlDst.grid(column=5, row=6, sticky='N')

# Text field
txt1 = tk.Text(master=f1, height=20, width=50)
txt1.grid(column=1, row=8, columnspan=4, sticky='w')

btnClr1 = tk.Button(f1, text='Clear', bg='yellow',command=clear_Fields)
btnClr1.grid(column=5, row=8, sticky='W')

btnSrcf1 = tk.Button(f1, text='Src', bg='orange',command=browse_Src)
btnSrcf1.grid(column=5, row=3, sticky='W')

btnDstf1 = tk.Button(f1, text='Dst', bg='orange',command=browse_Dst)
btnDstf1.grid(column=5, row=5, sticky='W')
#------------------End of frame 1 Layouts--------------------------

#------------------Frame 2 Layouts--------------------------------
# LABEL
lbl2 = tk.Label(f2, text='Welcome to remove duplicates')
lbl2.grid(column=0, row=0, columnspan=7, sticky='EW')
#lbl1 = tk.Label(text='Welcome Bob\'s backup program')

#Some text to explain function and usage
lblExp21 = tk.Label(f2, text='Local - compares files within each sub-directory of the target directory')
lblExp21.grid(column=0, row=1, columnspan=7, sticky='W')
lblExp22 = tk.Label(f2, text='Global - compares files across all sub-directories of the target directory')
lblExp22.grid(column=0, row=2, columnspan=7, sticky='W')
lblExp23 = tk.Label(f2, text='Newest of the duplicated files are kept')
lblExp23.grid(column=0, row=3, columnspan=7, sticky='W')

# LABEL
lblTar2 = tk.Label(f2, text='Target directory:')
lblTar2.grid(column=0, row=4)

lblExl2 = tk.Label(f2, text='Excluding:')
lblExl2.grid(column=0, row=5)

# Entry field for target dir
entryTar2 = tk.Entry(f2, textvariable=tar2Str)
entryTar2.grid(column=1, row=4, columnspan=6, sticky='EW')

# Entry field for excluded dir
entryExl2 = tk.Entry(f2, textvariable=exl2Str)
entryExl2.grid(column=1, row=5, columnspan=6, sticky='EW')

#Radio button for Gloabl val=1 or Local val=2 compare, val=0 no selection
rdbtn21 = tk.Radiobutton(f2, text='Global', variable=var25, value=1)
rdbtn21.grid(column=1, row=6)

rdbtn22 = tk.Radiobutton(f2, text='Local', variable=var25, value=2)
rdbtn22.grid(column=2, row=6)

chkb2 = tk.Checkbutton(f2, text='Compare Checksum', variable=var26)
chkb2.grid(column=3, row=6)

btn2 = tk.Button(f2, text='Analyse', bg='blue',command=input_Valid2)
btn2.grid(column=0, row=7)

btn22 = tk.Button(f2, text='Remove', bg='green',command=input_dup)
btn22.grid(column=0, row=7, sticky='N')
btn22.config(state=tk.DISABLED)

# Text field
txt2 = tk.Text(master=f2, height=20, width=45)
txt2.grid(column=1, row=7, columnspan=6, sticky='EW')

btnClr2 = tk.Button(f2, text='Clear', bg='yellow',command=clear_Fields2)
btnClr2.grid(column=7, row=7, sticky='W')

btnExl2 = tk.Button(f2, text='Exclude', bg='purple',command=browse_Exl2)
btnExl2.grid(column=7, row=5, sticky='W')

btnDirf2 = tk.Button(f2, text='Dir', bg='orange',command=browse_Dir2)
btnDirf2.grid(column=7, row=4, sticky='W')
#------------------End of Frame 2 Layouts-------------------------------

#------------------Frame 3 Layouts--------------------------------------
# LABEL
lbl3 = tk.Label(f3, text='Welcome to file deletion')
lbl3.grid(column=0, row=0, columnspan=3, sticky='EW')
#lbl1 = tk.Label(text='Welcome Bob\'s backup program')

#Some text to explain function and usage
lblExp31 = tk.Label(f3, text='Delete all instances of the target file/folder in the target directory')
lblExp31.grid(column=0, row=1, columnspan=3, sticky='W')
lblExp32 = tk.Label(f3, text='Files with extension .sys and .dll and foldername starts with "." are not deleted')
lblExp32.grid(column=0, row=2, columnspan=3, sticky='W')

# LABEL
lblTar3 = tk.Label(f3, text='Delete from:')
lblTar3.grid(column=0, row=3)

lblExl3 = tk.Label(f3, text='Excluding:')
lblExl3.grid(column=0, row=4)

# Entry field
entryTar3 = tk.Entry(f3, textvariable=tar3Str)
entryTar3.grid(column=1, row=3, columnspan=2, sticky='EW')

# Entry field for excluded dir
entryExl3 = tk.Entry(f3, textvariable=exl3Str)
entryExl3.grid(column=1, row=4, columnspan=2, sticky='EW')

# LABEL
lblName3 = tk.Label(f3, text='Target Name:')
lblName3.grid(column=0, row=5)

# Entry field
entryName3 = tk.Entry(f3)
entryName3.grid(column=1, row=5, columnspan=2, sticky='EW')

#Radio button for Folder val=1 or File val=2, val=0 no selection
rdbtn31 = tk.Radiobutton(f3, text='Folder', variable=var31, value=1)
rdbtn31.grid(column=1, row=6)

rdbtn32 = tk.Radiobutton(f3, text='File', variable=var31, value=2)
rdbtn32.grid(column=2, row=6)

btn3 = tk.Button(f3, text='Analyse', bg='blue',command=input_Valid3)
btn3.grid(column=0, row=7)

btn33 = tk.Button(f3, text='Delete', bg='green',command=input_del)
btn33.grid(column=0, row=7, sticky='N')
btn33.config(state=tk.DISABLED)

# Text field
txt3 = tk.Text(master=f3, height=20, width=50)
txt3.grid(column=1, row=7, columnspan=2, sticky='w')

btnClr3 = tk.Button(f3, text='Clear', bg='yellow',command=clear_Fields3)
btnClr3.grid(column=3, row=7, sticky='W')

btnDirf3 = tk.Button(f3, text='Dir', bg='orange',command=browse_Dir3)
btnDirf3.grid(column=3, row=3, sticky='W')

btnExl3 = tk.Button(f3, text='Exclude', bg='purple',command=browse_Exl3)
btnExl3.grid(column=3, row=4, sticky='W')
#--------------------End of Frame 3 Layouts----------------------------

#------------------Frame 4 Layouts--------------------------------------
# LABEL
lbl4 = tk.Label(f4, text='Welcome to checksum validation')
lbl4.grid(column=0, row=0, columnspan=5, sticky='EW')

#Some text to explain function and usage
lblExp41 = tk.Label(f4, text='Generate CSV record file')
lblExp41.grid(column=0, row=1, columnspan=5, sticky='EW')
lblExp42 = tk.Label(f4, text='Validate CSV record file')
lblExp42.grid(column=0, row=2, columnspan=5, sticky='EW')
lblExp43 = tk.Label(f4, text='Partial update does not remove entries')
lblExp43.grid(column=1, row=11, columnspan=5, sticky='EW')

# LABEL
lblGen4 = tk.Label(f4, text='Generate CSV from:')
lblGen4.grid(column=0, row=3)

lblGen41 = tk.Label(f4, text='Continue from:')
lblGen41.grid(column=0, row=4)

# Entry field
entryGen4 = tk.Entry(f4, textvariable=gen4Str)
entryGen4.grid(column=1, row=3, columnspan=6, sticky='EW')

entryGen41 = tk.Entry(f4, textvariable=gen41Str)
entryGen41.grid(column=1, row=4, columnspan=6, sticky='EW')

btn4 = tk.Button(f4, text='Generate', bg='blue',command=gen_record)
btn4.grid(column=1, row=6)

# LABEL
lblValid4 = tk.Label(f4, text='CSV record validation:')
lblValid4.grid(column=0, row=7)

lblValid41 = tk.Label(f4, text='Updating:')
lblValid41.grid(column=0, row=8)

lblValid42 = tk.Label(f4, text='with:')
lblValid42.grid(column=0, row=9)

# Entry field
entryValid41 = tk.Entry(f4, textvariable=val41Str)
entryValid41.grid(column=1, row=8, columnspan=6, sticky='EW')

entryValid42 = tk.Entry(f4, textvariable=val42Str)
entryValid42.grid(column=1, row=9, columnspan=6, sticky='EW')

#Radio button for full val=1 or partial val=2, val=0 no selection
rdbtn41 = tk.Radiobutton(f4, text='Full', variable=var4, value=1)
rdbtn41.grid(column=1, row=10)
rdbtn41.config(state=tk.DISABLED)

rdbtn42 = tk.Radiobutton(f4, text='Partial', variable=var4, value=2)
rdbtn42.grid(column=2, row=10)
rdbtn42.config(state=tk.DISABLED)

btn41 = tk.Button(f4, text='Analyse', bg='green',command=analyse_CSV)
btn41.grid(column=1, row=12, sticky='N')

btn42 = tk.Button(f4, text='Update', bg='green',command=update_CSV)
btn42.grid(column=2, row=12, sticky='N')
btn42.config(state=tk.DISABLED)

btnClr4 = tk.Button(f4, text='Clear', bg='yellow',command=clear_Fields4)
btnClr4.grid(column=3, row=12, sticky='W')

btnDirGen4 = tk.Button(f4, text='Dir', bg='orange',command=browse_DirGen4)
btnDirGen4.grid(column=7, row=3, sticky='W')

btnDirGen41 = tk.Button(f4, text='Dir', bg='orange',command=browse_DirGen41)
btnDirGen41.grid(column=7, row=4, sticky='W')

btnDirVal41 = tk.Button(f4, text='Dir', bg='orange',command=browse_DirVal41)
btnDirVal41.grid(column=7, row=8, sticky='W')

btnDirVal42 = tk.Button(f4, text='Dir', bg='orange',command=browse_DirVal42)
btnDirVal42.grid(column=7, row=9, sticky='W')

#--------------------End of Frame 4 Layouts----------------------------
print('Welcome to Bob\'s file management utility program')
print('This console window helps user to monitor progress of file operation')
print('Closing the console window will terminate the program immediately\n')

window.mainloop()
