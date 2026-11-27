#!/bin/sh
# quick build of the game program only (tools/build.sh makes the full release)
cd "$(dirname "$0")/../src" && vasmm68k_mot -quiet -m68000 -Fhunkexe -kick1hunks "$@" main.s
