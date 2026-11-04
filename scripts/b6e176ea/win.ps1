param([string]$Cmd = "list", [string]$Arg = "", [string]$Arg2 = "")
# helper for LIRA dialogs: list top windows of LiraSapr, list child controls, close a window, set an edit text, click a button
if (-not ([System.Management.Automation.PSTypeName]"WinH").Type) {
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class WinH { public delegate bool P(IntPtr h, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr par, P p, IntPtr l);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, string l);
[DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, StringBuilder l);
public static string Txt(IntPtr h){ var sb=new StringBuilder(512); SendMessage(h,0x000D,(IntPtr)512,sb); return sb.ToString(); }
public static List<string> L(uint pid){ var r=new List<string>(); EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p==pid && IsWindowVisible(h)){ var sb=new StringBuilder(256); GetWindowText(h,sb,256); r.Add(h.ToString()+" | "+sb.ToString()); } return true; }, IntPtr.Zero); return r; }
public static List<string> C(IntPtr par){ var r=new List<string>(); EnumChildWindows(par,(h,l)=>{ var cn=new StringBuilder(128); GetClassName(h,cn,128); r.Add(h+" | "+cn+" | "+Txt(h)); return true; }, IntPtr.Zero); return r; } }
"@
}
$lp = (Get-Process LiraSapr).Id
switch ($Cmd) {
  "list" { [WinH]::L([uint32]$lp) }
  "kids" { [WinH]::C([IntPtr][long]$Arg) }
  "close" { [WinH]::PostMessage([IntPtr][long]$Arg, 0x10, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "closed" }
  "set" { [WinH]::SendMessage([IntPtr][long]$Arg, 0x000C, [IntPtr]::Zero, $Arg2) | Out-Null; [WinH]::Txt([IntPtr][long]$Arg) }
  "click" { [WinH]::PostMessage([IntPtr][long]$Arg, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "clicked" }
}
