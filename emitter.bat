@echo off

setlocal EnableDelayedExpansion

set "filename=cooja-14.testlog"

for /f "delims=" %%i in (%filename%) do (
  echo %%i
)

echo "end of file"