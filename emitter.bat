@echo off

setlocal EnableDelayedExpansion

set "filename=cooja_packets.testlog"

for /f "delims=" %%i in (%filename%) do (
  echo %%i
)

echo "end of file"