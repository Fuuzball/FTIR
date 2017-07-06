import Tkinter as tk

root = tk.Tk()

def keyPress(event):
    print('pressed', event.char)

def click(event):
    #f.focus_set()
    print('clicked at', event.x, event.y)

f = tk.Frame(root, width = 100, height = 100)
f.bind("<Key>", keyPress)
f.bind("<Button-1>", click)
f.pack()

root.mainloop()
