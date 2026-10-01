param([string]$QuartusBin = 'C:/intelFPGA_lite/21.1/quartus/bin64', [string]$Python = 'python', [switch]$Compilar)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskNetlist = Join-Path $PSScriptRoot 'netlist'
New-Item -ItemType Directory -Force -Path $taskNetlist | Out-Null
Get-ChildItem -LiteralPath $taskRoot -Filter '*.bdf' | ForEach-Object {
    $taskBdf = Join-Path $taskNetlist $_.Name
    Copy-Item -LiteralPath $_.FullName -Destination $taskBdf
    $ErrorActionPreference = 'Continue'
    & "$QuartusBin/quartus_map.exe" projeto-ula "--convert_bdf_to_verilog=$taskBdf" *> (Join-Path $taskNetlist ($_.BaseName + '.log'))
    $ErrorActionPreference = 'Stop'
    if ($LASTEXITCODE -ne 0) { throw "BDF export failed: $($_.Name)" }
}
& $Python (Join-Path $PSScriptRoot 'auditar_interfaces.py')
if ($LASTEXITCODE -ne 0) { throw 'Interface audit failed.' }
& $Python (Join-Path $PSScriptRoot 'testar_netlists.py')
if ($LASTEXITCODE -ne 0) { throw 'Structural netlist tests failed.' }
if ($Compilar) {
    $ErrorActionPreference = 'Continue'
    & "$QuartusBin/quartus_sh.exe" --flow compile projeto-ula *> (Join-Path $PSScriptRoot 'compilacao_quartus.log')
    $ErrorActionPreference = 'Stop'
    if ($LASTEXITCODE -ne 0) { throw 'Quartus full compile failed.' }
    Get-Content -LiteralPath (Join-Path $PSScriptRoot 'compilacao_quartus.log') -Tail 8
}
