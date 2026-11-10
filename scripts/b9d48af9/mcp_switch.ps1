Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type 'using System; using System.Runtime.InteropServices; public class W1 { [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c); }'
$p = Get-Process Revit | ? { $_.MainWindowHandle -ne 0 } | Select -First 1
[W1]::ShowWindow($p.MainWindowHandle,3) | Out-Null; [W1]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep 2
$root = [Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
function FindName($n) { $c = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::NameProperty, $n); $root.FindFirst([Windows.Automation.TreeScope]::Descendants, $c) }
$tab = FindName "Надстройки"
if ($tab) { "tab found: " + $tab.Current.ControlType.ProgrammaticName
  try { $tab.GetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern).Select() } catch { try { $tab.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke() } catch { "tab: " + $_ } } }
Start-Sleep 2
$b = FindName "Revit MCP Switch"
if ($b) { "btn found"; $b.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke(); "invoked" } else { "btn not found" }

