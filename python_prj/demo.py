#!/usr/bin/env python
# coding=utf-8

from Tkinter import*

def get_main_window():
    '''create main window'''
    return Tkinter.Tk()

def set_main_window_size(root):
    '''set size of the main window.'''
    return root.geometry('600x400')

def create_lable(root):
    '''create a lable'''
    return Label(root, text = 'Hongten', fg = 'red')

def lable_pack(lable):
    '''manage and show the compoent'''
    return lable.pack()

def main_loop(root):
    '''main loop'''
    root.mainloop()

def main():
    root = get_main_window()
    root = set_main_window_size(root)
    lable = create_lable(root)
    lable_pack(lable)
    main_loop(root)

if __name__ == '__main__':
    main()


