@echo off
cd /d "%~dp0"
xelatex -interaction=nonstopmode main.tex
if errorlevel 1 goto bad
xelatex -interaction=nonstopmode main.tex
if errorlevel 1 goto bad
echo PDF ready: main.pdf
pause
exit /b 0
:bad
echo XeLaTeX compilation failed.
pause
exit /b 1
