@echo off
set outpath=%1
rmdir /S/Q %outpath%
BEER_primary.exe -n 1e8 -d %outpath%
