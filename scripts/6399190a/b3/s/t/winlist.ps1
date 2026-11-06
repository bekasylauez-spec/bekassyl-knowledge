param([int]$ProcId, [switch]$CloseDialogs)
Add-Type @"
using System;using System.Runtime.InteropServices;using System.Text;using System.Collections.Generic;
public class WL{
 public delegate bool EP(IntPtr h,IntPtr l);
 [DllImport("user32.dll")]public static extern bool EnumWindows(EP f,IntPtr l);
 [DllImport("user32.dll")]public static extern bool EnumChildWindows(IntPtr p,EP f,IntPtr l);
 [DllImport("user32.dll")]public static extern int GetWindowThreadProcessId(IntPtr h,out int p);
 [DllImport("user32.dll")]public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")]public static extern int GetClassName(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")]public static extern IntPtr PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 public static List<string> Run(int pid,bool close){
  var r=new List<string>();
  EnumWindows((h,l)=>{int p;GetWindowThreadProcessId(h,out p);if(p==pid&&IsWindowVisible(h)){var sb=new StringBuilder(256);GetWindowText(h,sb,256);var cn=new StringBuilder(256);GetClassName(h,cn,256);r.Add(h+" ["+cn+"] "+sb);
   if(cn.ToString()=="#32770"){EnumChildWindows(h,(c,l2)=>{var t=new StringBuilder(256);GetWindowText(c,t,256);r.Add("   child: "+t);return true;},IntPtr.Zero);
    if(close){PostMessage(h,0x0111,(IntPtr)1,IntPtr.Zero);r.Add("   -> IDOK posted");}}}
   return true;},IntPtr.Zero);
  return r;}}
"@
[WL]::Run($ProcId, $CloseDialogs.IsPresent)
