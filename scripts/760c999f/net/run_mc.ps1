param([string]$Dwg, [string]$Src)
# compile mc4.cs, copy $Src -> $Dwg, run MC4REN in my own AutoCAD 2021 (profile «МК 2021», SPDS loaded), auto-dismiss the proxy notice
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"; $mc = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acad\accoremgd.dll" /r:"$acad\acdbmgd.dll" /r:"$acad\acmgd.dll" /r:"$mc\mapimgd.dll" /r:"$mc\mapibasetypes.dll" /out:"$SP\net\mc4.dll" "$SP\net\mc4.cs"
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
Copy-Item $Src $Dwg -Force
Remove-Item "$env:TEMP\mc4_log.txt" -ErrorAction SilentlyContinue
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class WOk { public delegate bool P(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
[DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l);
public static int Ok(int pid, string title){ int n=0; EnumWindows((h,l)=>{int p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)){var s=new StringBuilder(256); GetWindowText(h,s,256); if(s.ToString()==title){ SendMessage(h,0x0111,(IntPtr)1,IntPtr.Zero); n++;}} return true;}, IntPtr.Zero); return n; } }
"@
$p = Start-Process "$acad\acad.exe" -ArgumentList "`"$Dwg`" /nologo /p `"МК 2021`" /b `"$SP\w\mcboot.scr`"" -PassThru
for ($i = 0; $i -lt 150 -and -not $p.HasExited; $i++) { Start-Sleep 2; [void][WOk]::Ok($p.Id, "Информация о прокси-объектах") }
"exited $($p.HasExited) after $($i*2)s"
if (Test-Path "$env:TEMP\mc4_log.txt") { Get-Content "$env:TEMP\mc4_log.txt" -Encoding UTF8 } else { "no log" }
