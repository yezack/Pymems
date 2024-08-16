import mmap,json,os
import ctypes
from ctypes import wintypes
from pymem import *

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
GetParent = ctypes.windll.user32.GetParent

class Pymems(Pymem):
    def __init__(
            self,
            process_name: typing.Union[str, int] = None,
            exact_match: bool = False,
            ignore_case: bool = True,
            multi_link: bool = False
    ):
        self.__remote_shell_addr = None
        super().__init__(process_name, exact_match, ignore_case)
        tg = f"pymems_mulit_link_lock_{self.process_id}"
        dt=self.__getMmapData(tg)
        if dt:
            if not multi_link:
                raise RuntimeError(f"进程[{self.process_id}]已被[{dt.decode('utf-8')}]连接,multi_link参数未启用不允许重复连接。")
            else:
                print(f"进程[{self.process_id}]已被[{dt.decode('utf-8')}]连接,multi_link参数已启用允许重复连接。")

        self.__mmap_content = mmap.mmap(-1, 1024, tagname=tg, access=mmap.ACCESS_WRITE)
        self.__mmap_content.seek(0)
        self.__mmap_content.write(str(os.getpid()).encode('utf-8'))
        self.__mmap_content.flush()


    def remote_exec(self, code:str, return_var_name=None):
        if not self._python_injected:
            raise RuntimeError("请先执行pymems.inject_python_interpreter")
        if not self.__remote_shell_addr:
            self.inject_python_remote_sheller()

        result_addr = self.allocate(ctypes.sizeof(ctypes.c_void_p))
        self.write_ctype(result_addr, ctypes.c_void_p(0))
        code_obj = {
            "return_var_name": return_var_name,
            "result_addr": result_addr,
            "code": code
        }
        code_b = json.dumps(code_obj).encode('utf-8') + b'\0\0'
        code_addr = self.allocate(len(code_b))
        written = ctypes.c_ulonglong(0) if '64bit' in platform.architecture() else ctypes.c_ulong(0)
        pymem.ressources.kernel32.WriteProcessMemory(
            self.process_handle,
            code_addr,
            code_b,
            len(code_b),
            ctypes.byref(written)
        )
        self.start_thread(self.__remote_shell_addr, code_addr)
        result_b_addr = int.from_bytes(self.read_bytes(result_addr, ctypes.sizeof(ctypes.c_void_p)), byteorder="little")
        self.free(result_addr)
        if result_b_addr:
            result_s = self.read_string(result_b_addr)
            self.free(result_b_addr)
            result_j = json.loads(result_s)
            if result_j["error"] == 0:
                return result_j["result"]
            else:
                print(f"执行代码错误:" + str(result_j["message"]))
                return None
        pass

    def inject_python_shellcode(self, shellcode, need_wait=True):
        raise AttributeError("pymems.inject_python_shellcode不可访问,使用pymems.remote_exec执行代码")

    def inject_python_remote_sheller(self):
        tag=f"pymems_remote_inject_info_{self.process_id}"
        dt_bytes = self.__getMmapData(tag)
        if not dt_bytes:
            print(f"未获取到[{tag}],重新注入代码.")
            code = open("pymem/__pymems_remote_call_code.py", encoding="utf-8").read()
            super().inject_python_shellcode(code, need_wait=False)
        import time
        for _ in range(1000):
            if dt_bytes: break
            dt_bytes = self.__getMmapData(f"pymems_remote_inject_info_{self.process_id}")
            time.sleep(0.003)
        else:
            raise RuntimeError("pymems获取Shell入口失败")
        dt_info = json.loads(dt_bytes.decode("utf-8"))
        self.__remote_shell_addr = dt_info["remote_call_ptr"]
        print(f"远程sheller入口:{hex(self.__remote_shell_addr)}")
        return

    def __getMmapData(self, tag):
        m = mmap.mmap(-1, 1024, tagname=tag, access=mmap.ACCESS_READ)
        m.seek(0)
        rslt = m.read(1024).rstrip(b'\x00')
        m.close()
        return rslt

    def get_window_hwnds(self):
        hwnds = []
        pid=self.process_id
        def __enum_windows_proc(hwnd, lParam):
            window_pid = wintypes.DWORD()
            GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            if window_pid.value == pid and GetParent(hwnd)==0:
                hwnds.append(hwnd)
            return True
        EnumWindows(EnumWindowsProc(__enum_windows_proc), 0)
        return hwnds
    
    def get_window_hwnd(self):
        hwnds=self.get_window_hwnds()
        return hwnds[0] if hwnds else None

