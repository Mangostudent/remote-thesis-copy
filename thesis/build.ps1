# PowerShell build script for IIT Bombay PhD Thesis
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "Compiling IIT Bombay PhD Thesis" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

if (-not (Test-Path ".build")) {
    New-Item -ItemType Directory -Path ".build" | Out-Null
}

Write-Host "[1/4] Running initial pdflatex pass..." -ForegroundColor Yellow
pdflatex "-aux-directory=.build" -interaction=nonstopmode main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Error "pdflatex failed on initial pass. Check .build\main.log"
    exit 1
}

Write-Host "[2/4] Generating bibliography and index..." -ForegroundColor Yellow
bibtex .build\main
makeindex .build\main.idx

Write-Host "[3/4] Running second pdflatex pass..." -ForegroundColor Yellow
pdflatex "-aux-directory=.build" -interaction=nonstopmode main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Error "pdflatex failed on second pass. Check .build\main.log"
    exit 1
}

Write-Host "[4/4] Running final pdflatex pass..." -ForegroundColor Yellow
pdflatex "-aux-directory=.build" -interaction=nonstopmode main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Error "pdflatex failed on final pass. Check .build\main.log"
    exit 1
}

Write-Host "===================================================================" -ForegroundColor Green
Write-Host "SUCCESS: Thesis compiled successfully!" -ForegroundColor Green
Write-Host "Final output: main.pdf" -ForegroundColor Green
Write-Host "All auxiliary build files kept cleanly inside .build\" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
