# Revit bridge: sends JSON-RPC to mcp-servers-for-revit (port 8080) and returns the parsed result.
# Usage:  . .\revit.ps1 ;  Invoke-Revit -Method say_hello
#         Invoke-RevitCode -Code 'return document.Title;'
#         Invoke-RevitCode -File script.cs
param()

function Invoke-Revit {
    param([string]$Method, [hashtable]$Params = @{}, [int]$TimeoutSec = 600, [int]$Port = 8080)
    $id = [guid]::NewGuid().ToString("N")
    $req = @{ jsonrpc = "2.0"; method = $Method; params = $Params; id = $id } | ConvertTo-Json -Depth 10 -Compress
    $client = New-Object System.Net.Sockets.TcpClient
    $client.ReceiveTimeout = $TimeoutSec * 1000
    $client.Connect("127.0.0.1", $Port)
    $stream = $client.GetStream()
    $bytes = [Text.Encoding]::UTF8.GetBytes($req)
    $stream.Write($bytes, 0, $bytes.Length)
    $ms = New-Object System.IO.MemoryStream
    $buf = New-Object byte[] 65536
    $result = $null
    while ($true) {
        $n = $stream.Read($buf, 0, $buf.Length)
        if ($n -le 0) { break }
        $ms.Write($buf, 0, $n)
        $txt = [Text.Encoding]::UTF8.GetString($ms.ToArray())
        try { $result = $txt | ConvertFrom-Json; break } catch { }
    }
    $client.Close()
    if ($null -eq $result) { return [Text.Encoding]::UTF8.GetString($ms.ToArray()) }
    return $result
}

function Invoke-RevitCode {
    param([string]$Code, [string]$File, [object[]]$Parameters = @(), [int]$TimeoutSec = 600)
    if ($File) { $Code = [IO.File]::ReadAllText($File, [Text.Encoding]::UTF8) }
    $r = Invoke-Revit -Method "send_code_to_revit" -Params @{ code = $Code; parameters = $Parameters } -TimeoutSec $TimeoutSec
    return $r
}
