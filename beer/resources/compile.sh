#!/bin/bash
# Set environment if not done already:
# ------------------------------------------------
# ver=2.6
# MCSTAS=/usr/share/mcstas/$ver
# MCSTAS_CC=gcc
# MCSTAS_CFLAGS=-O2

if [ -z "$MCSTAS" ]
	echo Environment variable MCSTAS not defined. Edit $0 to set its value. 
	exit 3
fi

if [ -z "$MCSTAS_CC" ]
	echo Environment variable MCSTAS_CC not defined. Edit %0 to set its value.  
	exit 3
fi

if [ -z "$1" ]
then
	echo Provide instrument file base name as argument.
	echo No instrument name given, assumes 'BEER_reference'.
	INS=BEER_reference
else
   INS=$1
fi

echo Compiling $INS
mcstas -o $INS.c $INS.instr
$MCSTAS_CC $MCSTAS_CFLAGS -o $INS.exe $INS.c -lm -I $MCSTAS/libs/mcpl $MCSTAS/libs/mcpl/libmcpl.a
rm $INS.c
