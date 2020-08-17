import sys
import tkinter as tk  # 使用Tkinter前需要先导入
import tkinter.filedialog
import multiprocessing
#from multiprocessing import Process, freeze_support

from guiConfig import *

def do_job():
    print("DL checkButton:")
    for i in range(0, len(dlCheckButton_var)):
        print(dlCheckButton_var[i].get(), end=" ")
    print(" ")
    print("UL checkButton:")
    for i in range(0, len(ulCheckButton_var)):
        print(ulCheckButton_var[i].get(), end=" ")
    print(" ")
    
def openFile():
    fileName_var = tk.StringVar()
    fileName = tk.filedialog.askopenfilename(title='选择文件', filetypes=[("Log files", "*.log"), ("All files", "*.*")]) 
    if fileName != "":
        fileName_var.set(fileName)
        print("Open file:", fileName_var.get())
    else:
        print("didn't open any file!")
        
def createFileMenu(menubar):
    filemenu = tk.Menu(menubar, tearoff=0)
    # 将上面定义的空菜单命名为File，放在菜单栏中，就是装入那个容器中
    menubar.add_cascade(label='File', menu=filemenu)

    # 在File中加入New、Open、Save等小菜单，即我们平时看到的下拉菜单，每一个小菜单对应命令操作。
    filemenu.add_command(label='Open', command=openFile)
    filemenu.add_separator()    # 添加一条分隔线
    filemenu.add_command(label='Exit', command=window.quit) # 用tkinter里面自带的quit()函数

def createEditMenu(menubar):
    # 第7步，创建一个Edit菜单项（默认不下拉，下拉内容包括Cut，Copy，Paste功能项）
    editmenu = tk.Menu(menubar, tearoff=0)
    # 将上面定义的空菜单命名为 Edit，放在菜单栏中，就是装入那个容器中
    menubar.add_cascade(label='Edit', menu=editmenu)
    submenu = tk.Menu(editmenu) # 和上面定义菜单一样，不过此处实在Edit上创建一个空的菜单
    editmenu.add_cascade(label='unit', menu=submenu)

    # 第9步，创建第三级菜单命令，即菜单项里面的菜单项里面的菜单命令（有点拗口，笑~~~）
    unit_var = tk.IntVar()
    unit_var.set(2) # 1 for kbps, 2 for Mbps
    submenu.add_radiobutton(label='kbps', variable=unit_var, value=1, command=do_job)
    submenu.add_radiobutton(label='Mbps', variable=unit_var, value=2, command=do_job)

def createDlFrame(frame_dl):
    #keyWord_Dl=('TBS', 'MacCe', 'StatusPdu', 'DataPdu', 'Rcvd', 'deltaRcvd', 'Sent', 'deltaSent', 'Buffered', 'iniTxPktsRcvd', 'reTxPktsRcvd', 'usedBuffers', 'allocated', 'released', 'numOfBearers')
    frame_dl.place(x=10, y=10, anchor='nw')
    
    for i in range(0, len(keyWord_Dl)):
        tk.Checkbutton(frame_dl, text=keyWord_Dl[i], variable=dlCheckButton_var[i], onvalue=1, offvalue=0, command=do_job)\
        .grid(row=int(i / 2), column=int(i % 2), padx=5, pady=2, ipadx=2, ipady=1, sticky='w')
    # 需要update之后才能获得实际高度
    frame_dl.update()
    print("frame_dl的高度：", frame_dl.winfo_reqheight(), "width", frame_dl.winfo_reqwidth())

def createUlFrame(frame_ul, frame_dl):
    #keyWord_Ul = ('received', 'rlcPduBytes', 'rlcPduPkts', 'zeroTbsPkts')
    frame_ul.place(x=10, y=50 + frame_dl.winfo_height(), anchor='nw')
    
    print("frame_ul anchor y:", 50 + frame_dl.winfo_height())
    for i in range(0, len(keyWord_Ul)):
        tk.Checkbutton(frame_ul, text=keyWord_Ul[i], variable=ulCheckButton_var[i], onvalue=1, offvalue=0, command=do_job)\
        .grid(row=int(i / 2), column=int(i % 2), padx=10, pady=5, ipadx=2, ipady=1, sticky='w')

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # Hack for multiprocessing.freeze_support() to work from a
        # setuptools-generated entry point.
        multiprocessing.freeze_support()
        
    # 第1步，实例化object，建立窗口window
    window = tk.Tk()
    
    # 第2步，给窗口的可视化起名字
    window.title('L2Lo throughput tool')

    # 第3步，设定窗口的大小(长 * 宽)
    window.geometry('800x500')  # 这里的乘是小x
    
    # 第5步，创建一个菜单栏，这里我们可以把他理解成一个容器，在窗口的上方
    menubar = tk.Menu(window)
    # 第6步，创建一个File菜单项（默认不下拉，下拉内容包括New，Open，Save，Exit功能项）
    createFileMenu(menubar)
    
    # 第7步，创建一个Edit菜单项（默认不下拉，下拉内容包括Cut，Copy，Paste功能项）
    createEditMenu(menubar)
    
    # 第11步，创建菜单栏完成后，配置让菜单栏menubar显示出来
    window.config(menu=menubar)

    dlCheckButton_var = [tk.IntVar() for i in range(len(keyWord_Dl))]
    ulCheckButton_var = [tk.IntVar() for i in range(len(keyWord_Ul))]
    # add DL frame
    frame_dl = tk.LabelFrame(window, text='DL', bd = 2, relief = 'ridge')# 第二层frame，左frame，长在主frame上
    createDlFrame(frame_dl)

    # add UL frame 这里用button代替frame，可以有3d效果，便于区分
    frame_ul = tk.LabelFrame(window, text='UL', bd = 2, relief = 'ridge')# 第二层frame，右frame，长在主frame上
    createUlFrame(frame_ul, frame_dl)
    
    # 第12步，主窗口循环显示
    window.mainloop()