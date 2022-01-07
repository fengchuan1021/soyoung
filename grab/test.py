# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import js2py
tofind='皮肤美容'
from js2py.base import JsObjectWrapper
def walk(b,arr):
    global tofind

    if isinstance(b, str) or isinstance(b, int):
        if b==tofind or str(b)==tofind:
            print(arr)
            exit(0)
    if isinstance(b,dict):

        for key in b:
            tmparr=arr[:]
            tmparr.append(key)
            walk(b[key],tmparr)
    elif isinstance(b,list):
        for i,key in enumerate(b):
            tmparr=arr[:]
            tmparr.append(i)
            walk(b[i],tmparr)


with open('js.txt','r',encoding='utf8') as f:
    a=f.read()

    ttt=js2py.eval_js(a)
    tt=ttt.to_dict()
    walk(tt,[])
