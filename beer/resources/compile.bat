@echo off
rem Set environment if not done already:
rem -------------------------------------
rem set ver=2.6
rem set PATH=C:/mcstas-%ver%/bin;%PATH%
rem set MCSTAS=C:/mcstas-%ver%/lib
rem set MCSTAS_CFLAGS=-O2
rem set MCSTAS_CC=gcc

rem Take instrument file base name as argument
rem -------------------------------------------
set name=%1

if [%MCSTAS%]==[] (
	echo Environment variable MCSTAS not defined. Edit %0 to set its value. 
	pause
	exit 3
)

if [%MCSTAS_CC%]==[] (
	echo Environment variable MCSTAS_CC not defined. Edit %0 to set its value. 
	pause
	exit 3
)

if [%name%]==[] (
	echo No instrument name given, assumes 'BEER_reference'
	set name=BEER_reference
)
echo Compiling %name%

mcstas -o %name%.c %name%.instr
%MCSTAS_CC% %MCSTAS_CFLAGS% -o %name%.exe %name%.c -I %MCSTAS%/libs/mcpl %MCSTAS%/libs/mcpl/libmcpl.a

:end


