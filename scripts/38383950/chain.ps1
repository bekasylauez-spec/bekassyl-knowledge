param([string[]]$Steps = @('01','10','11','12','90'))
$R = "D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit"
$run = "D:\Бекасыл КЖ КМ\_Стандарт_КЖ\скрипттер\run_cs.ps1"
$map = @{ '01' = @('b109_01_frame.cs', $false, '_b109_01.txt'); '10' = @('b109_10_bases.cs', $true, '_b109_10.txt'); '11' = @('b109_11_tube_nodes.cs', $true, '_b109_11.txt');
          '12' = @('b109_12_beam_nodes.cs', $true, '_b109_12.txt'); '90' = @('b109_90_clash.cs', $true, '_b109_90.txt'); 'q20' = @('b109_q20_audit.cs', $false, '_audit.txt') }
foreach ($s in $Steps) {
  $m = $map[$s]; $a = @('-ExecutionPolicy', 'Bypass', '-File', $run, '-File', "$R\$($m[0])", '-Log', "$R\$($m[2])", '-Timeout', '1500')
  if ($m[1]) { $a += @('-Lib', "$R\b109_lib.cs") }
  $o = & powershell @a
  "=== $s"; $o | Select -Last 6
}
