@echo off
set PATH=C:/mcstas-2.5/bin;%PATH%
set MCSTAS=C:/mcstas-2.5/lib
set MCSTAS_CC=gcc
set MCSTAS_TOOLS=C:/mcstas-2.5/lib/tools/Perl
rem set mcmd=perl C:/mcstas-2.4/lib/perlbin/mcrun.pl

set name=BEER_primary
if [%name%]==[] (
	echo Provide instrument file name without extension as a parameter.
	goto end
)
echo Compiling %name%

mcstas -o %name%.c %name%.instr
%MCSTAS_CC% -o %name%.exe %name%.c -I %MCSTAS%/libs/mcpl %MCSTAS%/libs/mcpl/libmcpl.a

:end

pause
