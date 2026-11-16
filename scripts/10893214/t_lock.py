import ctypes, sys
from ctypes import wintypes
k = ctypes.WinDLL("kernel32", use_last_error=True)
k.CreateFileW.restype = wintypes.HANDLE
k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
INVALID = wintypes.HANDLE(-1).value
def locked(path):
    h = k.CreateFileW(path, 0x80000000, 0, None, 3, 0, None)   # GENERIC_READ, share none, OPEN_EXISTING
    if h == INVALID or h is None:
        return "LOCKED(err %d)" % ctypes.get_last_error()
    k.CloseHandle(h)
    return "free"
base = r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1"
for sid, names in (("10893214-c5f6-4902-9f78-d792a6f31f71", ["b03l2y45e", "b84xserg2"]),
                   ("94c03bfb-48e3-4972-8913-5871021722f0", ["b26hu7ykn", "b3e50b2e3", "b78n8o2pv", "bll765u4t", "bubkov4zq"])):
    for n in names:
        p = base + "\\" + sid + "\\tasks\\" + n + ".output"
        print(sid[:8], n, locked(p))