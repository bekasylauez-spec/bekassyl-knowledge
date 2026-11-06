$S="C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\4caa2bcf-418f-4319-ab71-13934baee5b7\scratchpad"; $N="$S\net"
Remove-Item "$env:TEMP\acadjob_b2\job.txt","$env:TEMP\acadjob_b2\listening.txt","$env:TEMP\acadjob_b2\done.txt" -ErrorAction SilentlyContinue
Remove-Item "$S\w\Б2 Ригели.dwl","$S\w\Б2 Ригели.dwl2" -ErrorAction SilentlyContinue
$p=Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList "`"$S\w\Б2 Ригели.dwg`" /nologo /b `"$N\boot.scr`"" -PassThru
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type @"
using System;using System.Runtime.InteropServices;using System.Text;
public class W5{public delegate bool P(IntPtr h,IntPtr l);[DllImport("user32")]public static extern bool EnumWindows(P p,IntPtr l);[DllImport("user32")]public static extern int GetWindowThreadProcessId(IntPtr h,out int pid);[DllImport("user32")]public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);[DllImport("user32")]public static extern bool IsWindowVisible(IntPtr h);[DllImport("user32")]public static extern IntPtr SendMessage(IntPtr h,int m,IntPtr w,IntPtr l);}
"@
for($i=0;$i -lt 120;$i++){ Start-Sleep 2; if(Test-Path "$env:TEMP\acadjob_b2\listening.txt"){ $real = (Get-Process acad | Where-Object { $_.MainWindowTitle -like "*Б2 Ригели*" } | Sort-Object StartTime -Descending | Select-Object -First 1).Id; "listening $real"; $real | Set-Content "$N\pid.txt"; break }
  $script:dlg=$null; [W5]::EnumWindows({param($h,$l) $pp=0;[W5]::GetWindowThreadProcessId($h,[ref]$pp)|Out-Null; if($pp -eq $p.Id -and [W5]::IsWindowVisible($h)){$sb=New-Object Text.StringBuilder 256;[W5]::GetWindowText($h,$sb,256)|Out-Null; if($sb.ToString() -like 'Информация о прокси*'){$script:dlg=$h}}; $true},[IntPtr]::Zero)|Out-Null
  if($script:dlg){ $w=[Windows.Automation.AutomationElement]::FromHandle($script:dlg); $ok=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition) | ? { $_.Current.Name -eq 'ОК' } | select -First 1; [W5]::SendMessage([IntPtr]$ok.Current.NativeWindowHandle,0x00F5,[IntPtr]0,[IntPtr]0)|Out-Null } }