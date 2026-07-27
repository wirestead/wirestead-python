$ErrorActionPreference = "Continue"

$candidates = @(
  "${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\cdb.exe",
  "${env:ProgramFiles}\Windows Kits\10\Debuggers\x64\cdb.exe"
)

$cdb = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $cdb) {
  $roots = @("${env:ProgramFiles(x86)}\Windows Kits", "${env:ProgramFiles}\Windows Kits")
  foreach ($root in $roots) {
    if (Test-Path $root) {
      $cdb = Get-ChildItem -Path $root -Filter cdb.exe -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*\Debuggers\x64\cdb.exe" } |
        Select-Object -ExpandProperty FullName -First 1
      if ($cdb) {
        break
      }
    }
  }
}

if (-not $cdb) {
  Write-Host "cdb.exe not found; skipping native TcpServer diagnostic."
  exit 0
}

$probe = Join-Path $env:RUNNER_TEMP "wirestead_tcp_start_probe.py"
@'
import wirestead

print(wirestead.__file__, flush=True)
server = wirestead.TcpServer(0)
print("before start", flush=True)
print(server.start(), flush=True)
print("listening", server.listening(), flush=True)
server.stop()
print("stopped", flush=True)
'@ | Set-Content -Path $probe -Encoding UTF8

Write-Host "Using debugger: $cdb"
Write-Host "Python executable: $((Get-Command python).Source)"
& $cdb -lines -c "sxe av; g; kb; q" python -X faulthandler $probe
if ($LASTEXITCODE -ne 0) {
  Write-Host "Native TcpServer diagnostic exited with $LASTEXITCODE."
}

exit 0
