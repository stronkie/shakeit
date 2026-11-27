#!/bin/sh
# build.sh - Stronkie's Clover Snake: the full game ADF, the demo ADF,
# the hard drive zip and the WHDLoad version (zip + lha).
#   . amiga-toolkit/setup.sh ; VER=0.1 tools/build.sh
set -e
cd "$(dirname "$0")/.."
TK=${AMIGA_TK:?run . amiga-toolkit/setup.sh first}
NAME=StronkiesCloverSnake
EXE=CloverSnake
VOL=CloverSnake
VER=${VER:-0.1}
B=build
mkdir -p $B
printf "VERSION\tmacro\n\tdc.b\t'%s'\n\tendm\n" "$VER" > src/version.i
python3 tools/gen.py >/dev/null
python3 tools/icons.py >/dev/null
readme() { sed -e "s/{VER}/$VER/" -e "s/{DEMO}/$1/" ReadMe.txt; }

# 1. assemble (68000 only)
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -kick1hunks -nosym -o ../$B/$EXE main.s)
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -kick1hunks -nosym -DDEMO=1 -o ../$B/${EXE}Demo main.s)
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -kick1hunks -nosym -o ../$B/Install install.s)
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -nosym -o ../$B/$EXE.slave whdload.s)
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -nosym -DKEYEXIT=\$5f -o ../$B/${EXE}_card.slave whdload.s)   # CF card: Help quits
(cd src && vasmm68k_mot -quiet -m68000 -Fhunkexe -kick1hunks -o ../$B/$EXE.sym main.s)   # with symbols, for the test harness

# 2. the game disk (packed program)
rm -rf $B/disk && mkdir -p $B/disk/s
python3 $TK/tools/pack/crunch.py $B/$EXE $B/disk/$EXE
cp $B/Install $B/disk/
cp $B/icons/CloverSnake.info $B/icons/Install.info $B/icons/ReadMe.txt.info $B/disk/
readme "" > $B/disk/ReadMe.txt
printf '%s\n' "$EXE" > $B/disk/s/startup-sequence
python3 $TK/tools/adf.py build $B/${NAME}_V$VER.adf "$VOL" $B/disk $TK/tools/bootblock.bin
# the Stronkie Soft boot intro before the game (toolkit intro/, build it first)
python3 $TK/tools/add_intro.py $B/${NAME}_V$VER.adf $B/${NAME}_V$VER.adf

# 3. the demo disk
rm -rf $B/demodisk && mkdir -p $B/demodisk/s
python3 $TK/tools/pack/crunch.py $B/${EXE}Demo $B/demodisk/$EXE
cp $B/icons/CloverSnake.info $B/icons/ReadMe.txt.info $B/demodisk/
readme " DEMO (3 of the 12 rounds)" > $B/demodisk/ReadMe.txt
printf '%s\n' "$EXE" > $B/demodisk/s/startup-sequence
python3 $TK/tools/adf.py build $B/${NAME}_Demo.adf "${VOL}Demo" $B/demodisk $TK/tools/bootblock.bin

# 4. hard drive / CF card zip (unpacked program)
rm -rf $B/hd && mkdir -p $B/hd/$NAME
cp $B/$EXE $B/icons/CloverSnake.info $B/icons/ReadMe.txt.info $B/hd/$NAME/
readme "" > $B/hd/$NAME/ReadMe.txt
cp $B/icons/drawer.info $B/hd/$NAME.info
(cd $B/hd && rm -f ../${NAME}_V${VER}_harddrive.zip && zip -qr ../${NAME}_V${VER}_harddrive.zip $NAME $NAME.info)

# 5. WHDLoad (own slave, no Kickstart image; the game unpacked in data/)
rm -rf $B/whd && mkdir -p $B/whd/$NAME/data
cp $B/$EXE $B/whd/$NAME/data/
cp $B/$EXE.slave $B/whd/$NAME/
cp $B/icons/whdload.info $B/whd/$NAME/$NAME.info
readme "" > $B/whd/$NAME/ReadMe.txt
cp $B/icons/ReadMe.txt.info $B/whd/$NAME/
cp $B/icons/drawer.info $B/whd/$NAME.info
(cd $B/whd && rm -f ../${NAME}_V${VER}_WHDLoad.zip && zip -qr ../${NAME}_V${VER}_WHDLoad.zip $NAME $NAME.info)
python3 tools/whdlha.py $B/whd $NAME $B/${NAME}_V${VER}_WHDLoad.lha
echo "built: $(cd $B && ls ${NAME}_* | tr '\n' ' ')"
