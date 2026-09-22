@echo off
setlocal enabledelayedexpansion

echo ===================================================================
echo Compiling IIT Bombay PhD Thesis
echo ===================================================================

if not exist ".build" mkdir .build

echo [1/4] Running initial pdflatex pass...
pdflatex -aux-directory=.build -interaction=nonstopmode main.tex
if errorlevel 1 goto error

echo [2/4] Generating bibliography and index...
bibtex .build\main
makeindex .build\main.idx

echo [3/4] Running second pdflatex pass...
pdflatex -aux-directory=.build -interaction=nonstopmode main.tex
if errorlevel 1 goto error

echo [4/4] Running final pdflatex pass...
pdflatex -aux-directory=.build -interaction=nonstopmode main.tex
if errorlevel 1 goto error

echo ===================================================================
echo SUCCESS: Thesis compiled successfully!
echo Final output: main.pdf
echo All auxiliary build files kept cleanly inside .build\
echo ===================================================================
goto end

:error
echo ===================================================================
echo ERROR: Compilation encountered an error. Check .build\main.log for details.
echo ===================================================================
exit /b 1

:end
