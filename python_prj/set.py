#!/usr/bin/env python
#coding: utf-8
"""
use Entry widgets directly
lay out by rows with fixed-width labels: this and grid are best for forms
"""

from Tkinter import *

import serial
import time
import sys
import readline
import struct

fields = {
    u'端口号': "port",
    u'网关ID': "id",
    u'手机号': "phone",
    u'服务器': "upstreams",
    u'白名单': "whitelist",
}

ACTION_SET = 0
ACTION_DEL = 1

ser = None

logger = None

def log_print(log):
    global logger
    print log
    if logger:
        logger.insert(END, time.strftime("%F %T", time.localtime()).strip())
        logger.insert(END, "    %s" % log)
        logger.select_set(END)
        logger.yview(END)

def fetch(entries):
    for item in entries:
        log_print('%s => "%s"' % (item, entries[item].get()))

def setid(_id):
    serialWrite("setid %s\n" % _id)
    if serialRead() == True:
        log_print("Set id (%s) success" % _id)
    else:
        log_print("Set id (%s) failed" % _id)

def delid(_id):
    serialWrite("delid\n")
    if serialRead() == True:
        log_print("delete id success")
    else:
        log_print("delete id failed")

def setphone(_phone):
    serialWrite("setphone %s\n" % _phone)
    if serialRead() == True:
        log_print("Set phone (%s) success" % _phone)
    else:
        log_print("Set phone (%s) failed" % _phone)

def delphone(_phone):
    serialWrite("delphone\n")
    if serialRead() == True:
        log_print("Delete phone (%s) success" % _phone)
    else:
        log_print("Delete phone (%s) failed" % _phone)
    #log_print("Delete phone is unsupport, You can use a new one overide the old one")

def addus(_upstreams):
    for us in _upstreams.split(','):
        serialWrite("addus %s\n" % us)
        if serialRead() == True:
            log_print("Add upstream (%s) success" % us)
        else:
            log_print("Add upstream (%s) failed" % us)

def delus(_upstream):
    serialWrite("delus %s\n" % _upstream)
    if serialRead() == True:
        log_print("Delete upstream (%s) success" % _upstream)
    else:
        log_print("Delete upstream (%s) failed" % _upstream)

def addwl(_pns):
    for wl in _pns.split(','):
        serialWrite("addwl %s\n" % wl)
        if serialRead() == True:
            log_print("Add %s to whitelist success" % wl)
        else:
            log_print("Add %s to whitelist failed" % wl)

def delwl(_pn):
    serialWrite("delwl %s\n" % _pn)
    if serialRead() == True:
        log_print("Delete %s from whitelist success" % _pn)
    else:
        log_print("Delete %s from whitelist failed" % _pn)

def reboot():
    serialWrite("reboot\n")
    if serialRead() == True:
        log_print("reboot lite3g success")
    else:
        log_print("reboot lite3g failed")

def clearConfig():
    serialWrite("clearconf\n")
    if serialRead() == True:
        log_print("clear configure success")
    else:
        log_print("clear configure failed")

cmdMap = {
    "id": [setid, delid],
    "phone": [setphone, delphone],
    "upstreams": [addus, delus],
    "whitelist": [addwl, delwl],
}

def cmdExec(action, item, ent):
    cmdMap[item][action](ent.get())
    now = time.time()
    response = ser.readline().strip()
    while response:
        if response:
            log_print(response.decode())
        if time.time() - now >= 0.1:
            print "here?"
            break
        response = ser.readline().strip()

def serialClose():
    global ser
    if ser and ser.isOpen():
        ser.close()

def serialWrite(cmd):
    global ser

    ser.flushInput() #flush input buffer, discarding all its contents
    ser.flushOutput() #flush output buffer, aborting current output 
    if ser and ser.isOpen():
        for b in cmd:
            ser.write(b)
            time.sleep(0.03)

def serialOpen(ent):
    global ser
    ser = serial.Serial()
    ser.port = ent.get()
    ser.baudrate = 115200
    ser.timeout = 0.5;
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    ser.writeTimeout = 10

#    ser = serial.Serial(ent.get(), 115200, rtscts=0, timeout=None)
#    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
#    ser.parity = serial.PARITY_NONE #set parity check: no parity
#    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#    ser.writeTimeout = 10

#   try:
    ser.open()
 #   except Exception, e:
 #       log_print("error open serial port: " + str(e))
 #       sys.exit(-1)

    log_print("Open serial success")
    serialWrite("settime %d\n" % time.time())
    serialRead()

def serialRead():
    global ser
    now = time.time()
    try:
        while True:
            response = ser.readline().strip()
            if time.time() - now >= 5:
                log_print("Get response timeout")
                break
            if not response:
                continue
            if response.startswith('[TRUE]') or response.startswith('[FALSE]'):
                log_print(response.decode())
                if response.startswith('[TRUE]'):
                    return True
                return False
            else:
                log_print(response.decode())
                #log.write('%s: %s\n' % (time.ctime(), response.decode()))
                #log_print('%f: %s' % (time.time(),time.strftime("%T"), response.decode())
    except Exception, e1:
        log_print("Error: " + str(e1))
        return False

def serialLoad(entries):
    global ser

    lite3g_id = ""
    phone_number = ""
    upstreams = []
    whitelist = []

    log_print("load configurations")

    serialWrite("getthis\n")
    if serialRead() == True:
        response = ser.readline().strip()
        while not response.startswith('This is'):
            response = ser.readline().strip()
        fields = response.split(',')
        lite3g_id = fields[0].strip().split()[-1]
        phone_number = fields[1].strip()
        log_print("lite3g_id:%s phone:%s" % (lite3g_id, phone_number))
    else:
        log_print("Get lite3g information failed")

    serialWrite("getus\n")
    if serialRead() == True:
        while True:
            response = ser.readline().strip()
            if response:
                log_print(response)
                if response.startswith('END'):
                    break
                fields = response.split(',')
                if len(fields) == 3 and fields[2].endswith('ms'):
                    upstreams.append(fields[0])

        if len(upstreams) == 0:
            log_print("No upstream server specified")
        else:
            log_print("upstreams: %r" % upstreams)
    else:
        log_print("Get upstreams failed")

    serialWrite("getwl\n")
    if serialRead() == True:
        while True:
            response = ser.readline().strip()
            if response:
                log_print(response)
                if response.startswith('END'):
                    break
                fields = response.split(',')
                if len(fields) > 0:
                    for pn in fields:
                        whitelist.append(pn.strip())
        if len(whitelist) == 0:
            log_print("No whitelist specified")
        else:
            log_print("whitelist: %r" % whitelist)
    else:
        log_print("Get whitelist failed")

    entries['id'].delete(0, END)
    entries['id'].insert(0, lite3g_id)
    entries['phone'].delete(0, END)
    entries['phone'].insert(0, phone_number)
    entries['upstreams'].delete(0, END)
    entries['upstreams'].insert(0, ','.join(upstreams))
    entries['whitelist'].delete(0, END)
    entries['whitelist'].insert(0, ','.join(whitelist))

def makeform(root, fields):
    entries = {}

    field = u'端口号'
    row = Frame(root)
    lab = Label(row, width=10, text=field)
    pent = Entry(row, width=50)

    pent.insert(0, "/dev/ttyUSB0")
    Button(row, text=u'关闭', command=serialClose).pack(side=RIGHT)
    Button(row, text=u'打开', command=(lambda: serialOpen(pent))).pack(side=RIGHT)

    row.pack(side=TOP, fill=X)
    lab.pack(side=LEFT)

    pent.pack(side=RIGHT, expand=YES, fill=X)
    pent.focus()

    entries[fields[field]] = pent

    field = u'网关ID'
    key4 = fields[field]
    row = Frame(root)
    lab = Label(row, width=10, text=field)
    ent4 = Entry(row, width=50)

    Button(row, text=u'删除', command=(lambda: cmdExec(ACTION_DEL, key4, ent4))).pack(side=RIGHT)
    Button(row, text=u'设置', command=(lambda: cmdExec(ACTION_SET, key4, ent4))).pack(side=RIGHT)

    row.pack(side=TOP, fill=X)
    lab.pack(side=LEFT)

    ent4.pack(side=RIGHT, expand=YES, fill=X)
    ent4.focus()

    entries[key4] = ent4

    field = u'手机号'
    key1 = fields[field]
    row = Frame(root)
    lab = Label(row, width=10, text=field)
    ent1 = Entry(row, width=50)

    Button(row, text=u'删除', command=(lambda: cmdExec(ACTION_DEL, key1, ent1))).pack(side=RIGHT)
    Button(row, text=u'设置', command=(lambda: cmdExec(ACTION_SET, key1, ent1))).pack(side=RIGHT)

    row.pack(side=TOP, fill=X)
    lab.pack(side=LEFT)

    ent1.pack(side=RIGHT, expand=YES, fill=X)
    ent1.focus()

    entries[key1] = ent1

    field = u'服务器'
    key2 = fields[field]
    row = Frame(root)
    lab = Label(row, width=10, text=field)
    ent2 = Entry(row, width=50)

    Button(row, text=u'删除', command=(lambda: cmdExec(ACTION_DEL, key2, ent2))).pack(side=RIGHT)
    Button(row, text=u'设置', command=(lambda: cmdExec(ACTION_SET, key2, ent2))).pack(side=RIGHT)

    row.pack(side=TOP, fill=X)
    lab.pack(side=LEFT)

    ent2.pack(side=RIGHT, expand=YES, fill=X)
    ent2.focus()

    entries[key2] = ent2

    field = u'白名单'
    key3 = fields[field]
    row = Frame(root)
    lab = Label(row, width=10, text=field)
    ent3 = Entry(row, width=50)

    Button(row, text=u'删除', command=(lambda: cmdExec(ACTION_DEL, key3, ent3))).pack(side=RIGHT)
    Button(row, text=u'设置', command=(lambda: cmdExec(ACTION_SET, key3, ent3))).pack(side=RIGHT)

    row.pack(side=TOP, fill=X)
    lab.pack(side=LEFT)

    ent3.pack(side=RIGHT, expand=YES, fill=X)
    ent3.focus()

    entries[key3] = ent3

    return entries

def maketext(root):
    frame = Frame(root)
    frame.pack(expand=YES, fill=BOTH)

    sbar = Scrollbar(frame)
    text = Listbox(frame, relief=SUNKEN, height=15)
    sbar.config(command=text.yview)
    text.config(yscrollcommand=sbar.set)
    sbar.pack(side=RIGHT, fill=Y)
    text.pack(side=LEFT, expand=YES, fill=BOTH)

    return text

if __name__ == '__main__':
    root = Tk()
    root.title(u'lite3g配置管理')
    ents = makeform(root, fields)
    logger = maketext(root)
    Button(root, text=u'退出',
           command=sys.exit).pack(side=RIGHT)
    Button(root, text=u'加载',
           command=(lambda: serialLoad(ents))).pack(side=RIGHT)
    Button(root, text=u'清空',
           command=clearConfig).pack(side=RIGHT)
    Button(root, text=u'重启',
           command=reboot).pack(side=RIGHT)

    root.mainloop()

