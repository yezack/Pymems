def pymems_remote_call_init_temp_function():
    import ctypes, traceback, json, struct, time,mmap,os
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL('kernel32.dll')
    OutputDebugStringW = ctypes.windll.kernel32.OutputDebugStringW
    OutputDebugStringW.argtypes = [wintypes.LPCWSTR]
    OutputDebugStringW.restype = None
    def __debug_print(s):
        OutputDebugStringW(str(s))
    exec_local_name_space = {"exit_flag": None}

    try:
        OpenProcess = kernel32.OpenProcess
        OpenProcess.restype = ctypes.c_void_p

        CloseHandle = kernel32.CloseHandle
        CloseHandle.restype = ctypes.c_long
        CloseHandle.argtypes = [
            ctypes.c_void_p
        ]

        GetLastError = kernel32.GetLastError
        GetLastError.restype = ctypes.c_ulong

        VirtualAlloc = kernel32.VirtualAlloc
        VirtualAlloc.restype = ctypes.c_void_p
        VirtualAlloc.argtypes = (
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_ulong,
            ctypes.c_ulong
        )
        WriteProcessMemory = kernel32.WriteProcessMemory
        WriteProcessMemory.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t)
        ]
        WriteProcessMemory.restype = ctypes.c_long

        ReadProcessMemory = kernel32.ReadProcessMemory
        ReadProcessMemory.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t)
        )
        ReadProcessMemory.restype = ctypes.c_long

        def __remote_call(arg):
            code_obj = json.loads(ctypes.string_at(arg).decode("utf-8"))
            return_var_name = code_obj.get("return_var_name", None)
            result_addr = code_obj.get("result_addr", None)
            code = code_obj["code"]
            try:
                exec_local_name_space[return_var_name] = None
                exec(code, exec_local_name_space)
                if return_var_name:
                    r = {"error": 0, "result": exec_local_name_space.get(return_var_name, None)}
                    #__debug_print(f"执行结果:{return_var_name}=" + str(r))
                    try:
                        json.dumps(r["result"])
                    except (TypeError, OverflowError):
                        r["result"] = str(r["result"])
                else:
                    r = {"error": 0, "result": None}
                    #__debug_print("执行成功")
            except Exception as e:
                error_msg = traceback.format_exc()
                r = {"error": 1, "message": error_msg}
                #__debug_print("执行错误: " + str(error_msg))
            try:
                return_b = json.dumps(r).encode("utf-8") + b'\0\0'
                return_b_addr = VirtualAlloc(None, len(return_b), 0x3000, 0x40)
                WriteProcessMemory(-1, return_b_addr, return_b, len(return_b), None)
                WriteProcessMemory(-1, result_addr, struct.pack("P", return_b_addr), ctypes.sizeof(ctypes.c_void_p),
                                   None)
                #__debug_print(f"运行结果存储在: " + str(return_b_addr))
            except Exception as e:
                error_msg = traceback.format_exc()
                #__debug_print("解析错误: " + str(error_msg))
            return 0

        CALLBACK_FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)
        __remote_call_back = CALLBACK_FUNC_TYPE(__remote_call)
        remote_call_ptr = ctypes.cast(__remote_call_back, ctypes.c_void_p).value

        tg = f"pymems_remote_inject_info_{os.getpid()}"
        m = mmap.mmap(-1, 1024, tagname=tg, access=mmap.ACCESS_WRITE)
        m.seek(0)
        dt =json.dumps({"remote_call_ptr": remote_call_ptr})
        m.write(dt.encode('utf-8'))
        m.flush()
        __debug_print(f"已设定[{tg}]>>{dt}")
        while exec_local_name_space.get("exit_flag") != 0x258EAFA5:
            time.sleep(0.01)
        m.close()
        __debug_print("我退出了(exit_flag主动)")

    except Exception as e:
        error_msg = traceback.format_exc()
        __debug_print(error_msg)


pymems_remote_call_init_temp_function()
