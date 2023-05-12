@echo off

setlocal EnableDelayedExpansion

set "filename=cooja.testlog"

for /f "delims=" %%i in (%filename%) do (
  echo %%i
)

echo "end of file"