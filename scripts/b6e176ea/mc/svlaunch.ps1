param([string]$Dwg)
# start MY own AutoCAD instance on $Dwg with the SVLISTEN job listener (separate from the user's AutoCAD);
# closes the «Информация о прокси-объектах» dialog that blocks the startup script on console-saved files
if (Test-Path ($Dwg -replace '\.dwg$','.dwl')) { "OPEN ELSEWHERE"; exit }
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class SvW { public delegate bool P(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
[DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
public static int CloseProxy(uint pid){ int n=0; EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p==pid){ var sb=new StringBuilder(256); GetWindowText(h,sb,256); if(sb.ToString().Contains("прокси")){ PostMessage(h,0x10,IntPtr.Zero,IntPtr.Zero); n++; } } return true; }, IntPtr.Zero); return n; } }
"@
$jd = Join-Path $env:TEMP "acadjob_sv"
New-Item -ItemType Directory -Force $jd | Out-Null
Remove-Item "$jd\listening.txt","$jd\job.txt","$jd\done.txt" -ErrorAction SilentlyContinue
$scr = Join-Path $PSScriptRoot "svboot.scr"
$p = Start-Process -FilePath "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList @("`"$Dwg`"","/nologo","/b","`"$scr`"") -WindowStyle Minimized -PassThru
"pid " + $p.Id
Set-Content (Join-Path $PSScriptRoot "svpid.txt") $p.Id
for ($i = 0; $i -lt 300 -and -not (Test-Path "$jd\listening.txt"); $i++) { Start-Sleep 1; if ([SvW]::CloseProxy([uint32]$p.Id) -gt 0) { "closed proxy dialog" } }
if (Test-Path "$jd\listening.txt") { "listening: " + (Get-Content "$jd\listening.txt") } else { "timeout" }
