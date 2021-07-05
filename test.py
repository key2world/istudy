from tkinter import *
from tkinter.filedialog import askopenfilename

import PIL
from PIL import ImageTk

import bd

var = ""


def choosepic():
    global var
    path_ = askopenfilename()
    print(path_)

    var = bd.ww(path_)

    path.set(path_)
    img_open = PIL.Image.open(e1.get())
    img = ImageTk.PhotoImage(img_open)
    l1.config(image=img)
    l1.image = img

    w = Label(root, text=var, font=(13))
    w.pack()


root = Tk()
root.title("图片分析")
root.geometry("600x600+450+150")
path = StringVar()

Label(root, text="目标路径:", font=(13)).pack()
Button(root, text='选择图片', command=choosepic, font=(13)).pack()

e1 = Entry(root, text=path)
e1.pack()
l1 = Label(root, height=450)
l1.pack()

root.mainloop()
