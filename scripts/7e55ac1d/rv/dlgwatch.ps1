# Clicks "Р—Р°РіСЂСѓР·РёС‚СЊ РѕРґРёРЅ СЂР°Р·" for the RB Builder unsigned add-in prompt and OK on the ModPlus info box, until done.txt appears.
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W2 { [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, int m, IntPtr w, IntPtr l); }
"@
$done = Join-Path $env:LOCALAPPDATA "rvjob\done.txt"
$root = [Windows.Automation.AutomationElement]::RootElement
$t0 = Get-Date
while (-not (Test-Path $done) -and ((Get-Date) - $t0).TotalMinutes -lt 15) {
    try {
        $txt = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "ContentText")))
        if ($txt -and $txt.Current.Name -match "RB Builder") {
            $b = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "CommandButton_1002")))
            if ($b) { [W2]::SendMessage([IntPtr]$b.Current.NativeWindowHandle, 0xF5, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; "clicked load once" }
        }
        $m = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "TbMessage")))
        if ($m) {
            $vp = $null
            if ($m.TryGetCurrentPattern([Windows.Automation.ValuePattern]::Pattern, [ref]$vp) -and $vp.Current.Value -match "ModPlus") {
                $ok = $root.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, "BtOk")))
                $ip = $null
                if ($ok -and $ok.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern, [ref]$ip)) { $ip.Invoke(); "closed ModPlus" }
            }
        }
    } catch { }
    Start-Sleep -Seconds 3
}
if (Test-Path $done) { "DONE"; Get-Content $done -Encoding UTF8 } else { "TIMEOUT" }
