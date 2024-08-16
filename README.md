##### master

[![GitHub license](https://img.shields.io/github/license/srounet/pymem.svg)](https://github.com/srounet/Pymem/)
[![Build status](https://ci.appveyor.com/api/projects/status/sfdvrtuh9qa2f3aa/branch/master?svg=true)](https://ci.appveyor.com/project/srounet/pymem/branch/master)
[![codecov](https://codecov.io/gh/srounet/Pymem/branch/master/graph/badge.svg)](https://codecov.io/gh/srounet/Pymem/branch/master)
[![Discord](https://img.shields.io/discord/342944948770963476.svg)](https://discord.gg/xaWNac8)
[![Documentation Status](https://readthedocs.org/projects/pymem/badge/?version=latest)](https://pymem.readthedocs.io/?badge=latest)

[![Discord](https://img.shields.io/discord/342944948770963476.svg)](https://discord.gg/5rR62JZj)
[![Documentation Status](https://readthedocs.org/projects/pymem/badge/?version=latest)](https://pymem.readthedocs.io/?badge=latest)


Pymems
======
Pymems是对Pymem的扩展

使用方法
============
```python
from pymem import Pymems
pms=Pymems("notepad.exe")
pms.inject_python_interpreter()
code='r=1+1'
result=pms.remote_exec(code,"r")
print(f"exec({code})>>{result}")
```

变更说明：

一、新增一个Pymems类，大部分功能继承pymem,区别部分如下:

    1. Pymems废弃了inject_python_shellcode执行python代码的方法
    2. Pymems新增一个remote_exec(code:str,[return_var_name:str])方法,可以在远端python.dll中执行代码并返回返回值
    3. Pymems除了继承pymem原有的构造函数参数外，新增一个参数multi_link(默认为False),如果为True,则可以允许连接一个已被其他Pymems连接的远端python.dll
	4. Pymems新增get_window_hwnds和get_window_hwnd方法,获取进程的窗口

二、对原版Pymem的修正:

    Pymem.read_string可以自动读取到[end_flag(默认b'\0')]为止,最长限制默认为[byte=99999(0为不限制长度)]
    pymem.inject_python_shellcode新增一个参数[need_wait(默认True)]来决定是否阻塞等待shellcode执行完成
    pymem.inject_python_shellcode现在允许执行非ascii编码的代码,参数[encoding(默认'utf-8')]可指定编码方式
    pymem.start_thread新增一个参数[need_wait(默认True)]来决定是否阻塞等待线程执行完成
    pymem.inject_dll的filepath参数可以接受str或bytes(utf-16le编码)

Pymem
=====

A python library to manipulate Windows processes

Installation
============
```sh
pip install pymem
# with speedups
pip install pymem[speed]
```

Documentation
=============
You can find pymem documentation on readthedoc there: http://pymem.readthedocs.io/

Issues And Contributions
========================
Feel free to add issues and make pull-requests :)

Discord Support
===============
For questions and support, join us on discord https://discord.gg/xaWNac8