from tkinter import *

root = Tk()
l = Listbox(root)
l.pack()
for x in range(10):
    l.insert(END, x)
l.itemconfig(2, bg='white', fg='red')
l.itemconfig(4, bg='green', fg='white')
l.itemconfig(5, bg='cyan', fg='white')
root.mainloop()
