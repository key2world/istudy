from tkinter import *
from tkinter.filedialog import askopenfilename

import PIL
from PIL import ImageTk


def selectPath():
    path_ = askopenfilename()
    path.set(path_)
    img_open = PIL.Image.open(e1.get())
    img = ImageTk.PhotoImage(img_open)
    l1.config(image=img)
    l1.image = img


root = Tk()
root.title("图片分析")
root.geometry("600x600+450+150")

path = StringVar()

Label(root, text="目标路径:", font=(13)).grid(row=0, column=0)

e1 = Entry(root, text=path, font=(13)).grid(row=0, column=1)

Button(root, text="路径选择", command=selectPath, font=(13)).grid(row=0, column=2)

l1 = Label(root).place(x=10, y=60, anchor="nw")

# Label(root, text="图片是：", font=(20)).place(x=10, y=40, anchor="nw")
# var = "sadasdasd"
# w = Label(root, text=var, font=(20)).place(x=10, y=60, anchor="nw")

root.mainloop()
