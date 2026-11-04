param([int]$ProcId, [int]$Seconds = 0)
# list visible windows of an acad process; while waiting, dismiss the SHX (cancel = ignore) and proxy (OK) notices
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class WD { public delegate bool P(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
[DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l);
public static string Run(int pid){ string r=""; EnumWindows((h,l)=>{int p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)){var s=new StringBuilder(256); GetWindowText(h,s,256); var t=s.ToString(); r+="["+t+"] ";
 if(t=="Информация о прокси-объектах") SendMessage(h,0x0111,(IntPtr)1,IntPtr.Zero);
 if(t=="Отсутствуют файлы SHX") SendMessage(h,0x0111,(IntPtr)2,IntPtr.Zero);} return true;}, IntPtr.Zero); return r; } }
"@
$w = ""
for ($i = 0; $i -le $Seconds / 2; $i++) {
    if (-not (Get-Process -Id $ProcId -ErrorAction SilentlyContinue)) { "exited after $($i*2)s"; return }
    $w = [WD]::Run($ProcId)
    if ($Seconds -gt 0) { Start-Sleep 2 }
}
"running: $w"
