param([string]$Dwg, [string]$Src, [string]$Json)
# run V4OPS (v4.cs) in my own full AutoCAD 2021 (profile «МК 2021», SPDS loaded): needed to clone/transform SPDS objects
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"
$dll = "$SP\net\v4g_" + (Get-Date -Format HHmmssfff) + ".dll"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acad\accoremgd.dll" /r:"$acad\acdbmgd.dll" /r:"$acad\acmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" "$SP\net\v4.cs"
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
Copy-Item $Src $Dwg -Force
Remove-Item "$Json.log" -ErrorAction SilentlyContinue
$scr = @("(setvar `"SECURELOAD`" 0)", "(setvar `"FILEDIA`" 0)", "_.NETLOAD", "`"$dll`"", "V4OPS", "_.QSAVE", "(setvar `"FILEDIA`" 1)", "(setvar `"SECURELOAD`" 1)", "_.QUIT", "") -join "`r`n"
[IO.File]::WriteAllText("$SP\w\v4gui.scr", $scr, [Text.Encoding]::GetEncoding(1251))
$env:V4_JSON = $Json
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class WOk2 { public delegate bool P(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
[DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l);
public static string Ok(int pid, string title){ string seen=""; EnumWindows((h,l)=>{int p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)){var s=new StringBuilder(256); GetWindowText(h,s,256); if(s.ToString()==title){ SendMessage(h,0x0111,(IntPtr)1,IntPtr.Zero);} else if(s.Length>0 && !s.ToString().StartsWith("Autodesk")) seen+=s+";";} return true;}, IntPtr.Zero); return seen; } }
"@
$p = Start-Process "$acad\acad.exe" -ArgumentList "`"$Dwg`" /nologo /p `"МК 2021`" /b `"$SP\w\v4gui.scr`"" -PassThru
$other = ""
for ($i = 0; $i -lt 300 -and -not $p.HasExited; $i++) { Start-Sleep 2; $o = [WOk2]::Ok($p.Id, "Информация о прокси-объектах"); if ($o) { $other = $o } }
"exited $($p.HasExited) after $($i*2)s; other windows: $other"
if (Test-Path "$Json.log") { Get-Content "$Json.log" -Encoding UTF8 } else { "no log" }

