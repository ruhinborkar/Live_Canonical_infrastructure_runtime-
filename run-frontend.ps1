$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
Set-Location "$PSScriptRoot\frontend"
if (-not (Test-Path "node_modules")) { npm.cmd install }
npm.cmd run dev
