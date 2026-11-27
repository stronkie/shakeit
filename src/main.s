;=====================================================================
; Stronkie's Clover Snake - Amiga 500 (68000, Kickstart 3.1, 1 MB chip)
; Created By Mark Stronks, Stronkie Soft (c) 2026
;
; Inspired by the 1986 MSX game Snake It: eat every clover (the snake
; grows and a white ball pops up somewhere), eat every ball too, keep
; away from the poison mushrooms, the walls and your own tail, catch
; the drifting hearts for a bigger bonus multiplier.
;
; No interrupts, no blitter: the game polls the beam, the keyboard
; (CIA-A) and the joystick once a frame, and draws 8x8 cells with the
; CPU. That keeps it simple and lets it run under the WHDLoad slave
; without a Kickstart image.
;=====================================================================

	ifnd	DEMO
DEMO	equ	0
	endc

	include	"version.i"

; exec / graphics
_LVOForbid	equ	-132
_LVOPermit	equ	-138
_LVOFindTask	equ	-294
_LVOGetMsg	equ	-372
_LVOReplyMsg	equ	-378
_LVOWaitPort	equ	-384
_LVOCloseLibrary equ	-414
_LVOOpenLibrary	equ	-552
_LVOLoadView	equ	-222
_LVOWaitBlit	equ	-228
_LVOWaitTOF	equ	-270

CUSTOM	equ	$dff000
PS	equ	10240			; one bitplane: 40 x 256
SCRSIZE	equ	PS*4

; cells
C_EMPTY	equ	0
C_WALL	equ	1
C_CLOVER equ	2
C_BALL	equ	3
C_MUSH	equ	4
C_SNAKE	equ	5

FIELDX	equ	3			; the field inside the border (screen cells)
FIELDY	equ	4
FIELDW	equ	34
FIELDH	equ	27
STARTPOS equ	25*40+20		; the head at the start (moving up)
LEVSIZE	equ	32+FIELDW*FIELDH
RINGMASK equ	1023
GROWBY	equ	2

	section	code,code
	include	"gfx_gen.s"

	section	code,code
;---------------------------------------------------------------------
Start:	move.l	4.w,a6
	sub.l	a1,a1
	jsr	_LVOFindTask(a6)
	move.l	d0,a4
	tst.l	172(a4)			; pr_CLI
	bne.s	.cli
	lea	92(a4),a0		; from Workbench: the startup message
	jsr	_LVOWaitPort(a6)
	lea	92(a4),a0
	jsr	_LVOGetMsg(a6)
	move.l	d0,WBMsg
.cli:	lea	GfxName(pc),a1
	moveq	#0,d0
	jsr	_LVOOpenLibrary(a6)
	move.l	d0,GfxBase
	beq	.nogfx
	move.l	d0,a6
	move.l	34(a6),OldView
	sub.l	a1,a1
	jsr	_LVOLoadView(a6)
	jsr	_LVOWaitTOF(a6)
	jsr	_LVOWaitTOF(a6)
	jsr	_LVOWaitBlit(a6)
	move.l	4.w,a6
	jsr	_LVOForbid(a6)
	lea	CUSTOM,a5
	move.w	$1c(a5),OldIntena
	move.w	$02(a5),OldDma
	move.w	#$7fff,$9a(a5)		; no interrupts: everything is polled
	move.w	#$7fff,$9c(a5)
	move.w	#$7fff,$96(a5)

	bsr	Main

	lea	CUSTOM,a5
	move.w	#$7fff,$9a(a5)
	move.w	#$7fff,$9c(a5)
	move.w	#$7fff,$96(a5)
	moveq	#0,d0
	move.w	d0,$a8(a5)
	move.w	d0,$b8(a5)
	move.w	d0,$c8(a5)
	move.w	d0,$d8(a5)
	move.l	GfxBase,a6
	move.l	38(a6),$80(a5)		; the system copper list
	move.w	d0,$88(a5)
	move.w	OldDma,d0
	or.w	#$8000,d0
	move.w	d0,$96(a5)
	move.w	OldIntena,d0
	or.w	#$c000,d0
	move.w	d0,$9a(a5)
	move.l	4.w,a6
	jsr	_LVOPermit(a6)
	move.l	GfxBase,a6
	move.l	OldView,a1
	jsr	_LVOLoadView(a6)
	jsr	_LVOWaitTOF(a6)
	jsr	_LVOWaitTOF(a6)
	move.l	a6,a1
	move.l	4.w,a6
	jsr	_LVOCloseLibrary(a6)
.nogfx:	move.l	WBMsg,d0
	beq.s	.x
	move.l	4.w,a6
	jsr	_LVOForbid(a6)
	move.l	WBMsg,a1
	jsr	_LVOReplyMsg(a6)
.x:	moveq	#0,d0
	rts

GfxName:	dc.b	'graphics.library',0
VerString:	dc.b	'$VER: CloverSnake '
		VERSION
		dc.b	' (27.11.2026) Created By Mark Stronks, Stronkie Soft',0
	even

;---------------------------------------------------------------------
Main:	move.b	#$ff,LastKey
	move.b	#1,MusicOn
	move.l	#5000,HiScore
	move.w	#$ace1,Seed
	lea	Palette,a0
	lea	CurPal,a1
	moveq	#15,d0
.p:	move.w	(a0)+,(a1)+
	dbf	d0,.p
	bsr	Cls
	bsr	InitCopper
	moveq	#0,d0
	bsr	SetFade
	bsr	InitSound
	bsr	Intro
.title:	bsr	Title
	tst.w	d0
	bmi.s	.quit
	bsr	Game
	bra.s	.title
.quit:	bsr	StopTune
	rts

;---------------------------------------------------------------------
; the display
InitCopper:
	lea	CopperList,a0
	move.l	#$008e2c81,(a0)+
	move.l	#$00902cc1,(a0)+
	move.l	#$00920038,(a0)+
	move.l	#$009400d0,(a0)+
	move.l	#$01020000,(a0)+
	move.l	#$01040000,(a0)+
	move.l	#$01080000,(a0)+
	move.l	#$010a0000,(a0)+
	move.l	#$01fc0000,(a0)+	; AGA: no fetch mode
	move.l	#$01060c00,(a0)+
	move.l	#Screen,d0
	move.w	#$e0,d1
	moveq	#3,d2
.bp:	move.w	d1,(a0)+
	swap	d0
	move.w	d0,(a0)+
	addq.w	#2,d1
	move.w	d1,(a0)+
	swap	d0
	move.w	d0,(a0)+
	addq.w	#2,d1
	add.l	#PS,d0
	dbf	d2,.bp
	move.l	a0,CopColors
	move.w	#$180,d1
	moveq	#15,d2
.c:	move.w	d1,(a0)+
	clr.w	(a0)+
	addq.w	#2,d1
	dbf	d2,.c
	move.l	#$01004200,(a0)+
	move.l	#$fffffffe,(a0)+
	lea	CUSTOM,a5
	bsr	WaitFrame
	move.l	#CopperList,$80(a5)
	move.w	d0,$88(a5)
	move.w	#$8380,$96(a5)		; DMA on: bitplanes + copper
	rts

; SetFade: d0 = brightness 0..16, CurPal -> the copper list
SetFade:
	movem.l	d0-d4/a0-a1,-(sp)
	lea	CurPal,a0
	move.l	CopColors,a1
	moveq	#15,d4
.l:	move.w	(a0)+,d1
	move.w	d1,d2
	lsr.w	#8,d2
	and.w	#15,d2
	mulu	d0,d2
	lsr.w	#4,d2
	lsl.w	#8,d2
	move.w	d1,d3
	lsr.w	#4,d3
	and.w	#15,d3
	mulu	d0,d3
	lsr.w	#4,d3
	lsl.w	#4,d3
	or.w	d3,d2
	move.w	d1,d3
	and.w	#15,d3
	mulu	d0,d3
	lsr.w	#4,d3
	or.w	d3,d2
	move.w	d2,2(a1)
	addq.l	#4,a1
	dbf	d4,.l
	movem.l	(sp)+,d0-d4/a0-a1
	rts

FadeIn:	movem.l	d0,-(sp)
	moveq	#0,d0
.l:	bsr	SetFade
	bsr	WaitFrame
	addq.w	#1,d0
	cmp.w	#16,d0
	ble.s	.l
	movem.l	(sp)+,d0
	rts

FadeOut:
	movem.l	d0,-(sp)
	moveq	#16,d0
.l:	bsr	SetFade
	bsr	WaitFrame
	subq.w	#1,d0
	bpl.s	.l
	movem.l	(sp)+,d0
	rts

;---------------------------------------------------------------------
; once a frame: wait for line 300, read the keyboard, the joystick,
; play the sound
WaitFrame:
	movem.l	d0-d1,-(sp)
.w1:	move.l	CUSTOM+4,d0
	and.l	#$1ff00,d0
	cmp.l	#300<<8,d0
	beq.s	.w1
.w2:	move.l	CUSTOM+4,d0
	and.l	#$1ff00,d0
	cmp.l	#300<<8,d0
	bne.s	.w2
	movem.l	(sp)+,d0-d1
	addq.l	#1,FrameCount
	bsr	PollInput
	bsr	SoundFrame
	rts

; WaitFrames: d0 = frames; stops early on fire (returns d0 = -1 then)
WaitFrames:
	clr.b	FireHit
.l:	bsr	WaitFrame
	tst.b	FireHit
	bne.s	.f
	subq.w	#1,d0
	bgt.s	.l
	moveq	#0,d0
	rts
.f:	clr.b	FireHit
	moveq	#-1,d0
	rts

PollInput:
	movem.l	d0-d2/a0,-(sp)
	move.b	$bfed01,d0		; CIA-A ICR: a key?
	btst	#3,d0
	beq.s	.nokey
	move.b	$bfec01,d0
	bset	#6,$bfee01		; handshake
	not.b	d0
	ror.b	#1,d0
	moveq	#2,d2
.h1:	move.b	CUSTOM+6,d1
.h2:	cmp.b	CUSTOM+6,d1
	beq.s	.h2
	dbf	d2,.h1
	bclr	#6,$bfee01
	moveq	#0,d1
	move.b	d0,d1
	and.w	#$7f,d1
	lea	KeyTab,a0
	tst.b	d0
	bmi.s	.up
	move.b	#1,(a0,d1.w)
	move.b	d1,LastKey
	cmp.b	#$37,d1			; M: music on / off
	bne.s	.nokey
	not.b	MusicOn
	bra.s	.nokey
.up:	clr.b	(a0,d1.w)
.nokey:	bsr	ReadJoy
	movem.l	(sp)+,d0-d2/a0
	rts

; joystick port 2 + cursor keys + space / return
ReadJoy:
	move.w	CUSTOM+$0c,d0
	moveq	#0,d2
	btst	#1,d0
	beq.s	.nr
	or.b	#2,d2
.nr:	btst	#9,d0
	beq.s	.nl
	or.b	#8,d2
.nl:	move.w	d0,d1
	lsr.w	#1,d1
	eor.w	d0,d1
	btst	#0,d1
	beq.s	.nd
	or.b	#4,d2
.nd:	btst	#8,d1
	beq.s	.nu
	or.b	#1,d2
.nu:	lea	KeyTab,a0
	tst.b	$4c(a0)
	beq.s	.k1
	or.b	#1,d2
.k1:	tst.b	$4e(a0)
	beq.s	.k2
	or.b	#2,d2
.k2:	tst.b	$4d(a0)
	beq.s	.k3
	or.b	#4,d2
.k3:	tst.b	$4f(a0)
	beq.s	.k4
	or.b	#8,d2
.k4:	move.b	JoyDir,d1
	move.b	d2,JoyDir
	not.b	d1
	and.b	d2,d1
	or.b	d1,JoyHit
	moveq	#0,d2
	btst	#7,$bfe001
	bne.s	.nf
	moveq	#1,d2
.nf:	tst.b	$40(a0)			; space
	beq.s	.ns
	moveq	#1,d2
.ns:	tst.b	$44(a0)			; return
	beq.s	.nt
	moveq	#1,d2
.nt:	move.b	Fire,d1
	move.b	d2,Fire
	not.b	d1
	and.b	d2,d1
	or.b	d1,FireHit
	rts

;---------------------------------------------------------------------
; drawing
Cls:	lea	Screen,a0
	move.w	#SCRSIZE/16-1,d0
	moveq	#0,d1
.l:	move.l	d1,(a0)+
	move.l	d1,(a0)+
	move.l	d1,(a0)+
	move.l	d1,(a0)+
	dbf	d0,.l
	rts

; CopyPic: a0 = a picture (4 planes)
CopyPic:
	lea	Screen,a1
	move.w	#SCRSIZE/16-1,d0
.l:	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	dbf	d0,.l
	rts

; DrawTile: d0 = column, d1 = row, d2 = tile
DrawTile:
	movem.l	d0-d2/a0-a1,-(sp)
	lea	Screen,a0
	mulu	#320,d1
	add.l	d1,a0
	add.w	d0,a0
	lea	Tiles,a1
	lsl.w	#5,d2
	add.w	d2,a1
	moveq	#7,d0
.l:	move.b	(a1)+,(a0)
	move.b	(a1)+,PS(a0)
	move.b	(a1)+,PS*2(a0)
	move.b	(a1)+,PS*3(a0)
	lea	40(a0),a0
	dbf	d0,.l
	movem.l	(sp)+,d0-d2/a0-a1
	rts

; DrawPos: d0 = cell (row*40+col), d2 = tile (TileMap not changed)
DrawPos:
	movem.l	d0-d1,-(sp)
	moveq	#0,d1
	move.w	d0,d1
	divu	#40,d1
	move.w	d1,d0
	swap	d1
	exg	d0,d1
	bsr	DrawTile
	movem.l	(sp)+,d0-d1
	rts

; SetCell: d0 = cell, d2 = tile: remember it and draw it
SetCell:
	move.l	a0,-(sp)
	lea	TileMap,a0
	add.w	d0,a0
	add.w	d0,a0
	move.w	d2,(a0)
	move.l	(sp)+,a0
	bra.s	DrawPos

; RedrawCell: d0 = cell
RedrawCell:
	movem.l	d2/a0,-(sp)
	lea	TileMap,a0
	add.w	d0,a0
	add.w	d0,a0
	move.w	(a0),d2
	bsr	DrawPos
	movem.l	(sp)+,d2/a0
	rts

; DrawText: a0 = text (0 at the end), d0 = column, d1 = row, d2 = font
DrawText:
	movem.l	d0-d3/a0,-(sp)
	move.w	d2,d3
.l:	moveq	#0,d2
	move.b	(a0)+,d2
	beq.s	.x
	cmp.b	#96,d2
	blo.s	.u
	sub.b	#32,d2
.u:	sub.w	#32,d2
	add.w	d3,d2
	bsr	DrawTile
	addq.w	#1,d0
	bra.s	.l
.x:	movem.l	(sp)+,d0-d3/a0
	rts

; CenterText: a0 = text, d1 = row, d2 = font
CenterText:
	movem.l	d0/a0,-(sp)
	moveq	#0,d0
.c:	tst.b	(a0)+
	beq.s	.e
	addq.w	#1,d0
	bra.s	.c
.e:	lsr.w	#1,d0
	neg.w	d0
	add.w	#20,d0
	move.l	4(sp),a0
	bsr	DrawText
	movem.l	(sp)+,d0/a0
	rts

; DrawNum: d0.l = value, d1 = digits, d2 = column, d3 = row, d4 = font
; (leading zeros are spaces)
DrawNum:
	movem.l	d0-d6/a0,-(sp)
	lea	NumBuf+12,a0
	clr.b	(a0)
	move.w	d1,d5
	subq.w	#1,d5
	moveq	#0,d6			; digits made
.l:	bsr	Div10
	add.b	#'0',d1
	tst.w	d6
	beq.s	.d
	tst.l	d0
	bne.s	.d
	cmp.b	#'0',d1
	bne.s	.d
	moveq	#' ',d1
.d:	move.b	d1,-(a0)
	addq.w	#1,d6
	dbf	d5,.l
	; the digits were made right to left: blank the leading zeros
	lea	NumBuf+12,a0
	sub.w	d6,a0
	move.l	a0,-(sp)
.z:	cmp.b	#'0',(a0)
	bne.s	.zd
	tst.b	1(a0)
	beq.s	.zd
	move.b	#' ',(a0)+
	bra.s	.z
.zd:	move.l	(sp)+,a0
	move.w	d2,d0
	move.w	d3,d1
	move.w	d4,d2
	bsr	DrawText
	movem.l	(sp)+,d0-d6/a0
	rts

; Div10: d0.l / 10 -> d0.l, remainder in d1.w (uses d2)
Div10:	move.l	d2,-(sp)
	moveq	#0,d1
	swap	d0
	move.w	d0,d1
	divu	#10,d1
	move.w	d1,d2
	swap	d0
	move.w	d0,d1
	divu	#10,d1
	swap	d2
	move.w	d1,d2
	swap	d1
	move.l	d2,d0
	move.l	(sp)+,d2
	rts

; ShowMsg: a0 = text, d1 = row: a band across the field with the text
ShowMsg:
	movem.l	d0-d2,-(sp)
	moveq	#FIELDX,d0
	moveq	#T_EMPTY,d2
.b:	bsr	DrawTile
	addq.w	#1,d0
	cmp.w	#FIELDX+FIELDW,d0
	blt.s	.b
	move.w	#T_FONTY,d2
	bsr	CenterText
	movem.l	(sp)+,d0-d2
	rts

; HideMsg: d1 = row: the field cells back
HideMsg:
	movem.l	d0-d1,-(sp)
	mulu	#40,d1
	add.w	#FIELDX,d1
	move.w	d1,d0
	moveq	#FIELDW-1,d1
.l:	bsr	RedrawCell
	addq.w	#1,d0
	dbf	d1,.l
	movem.l	(sp)+,d0-d1
	rts

;---------------------------------------------------------------------
; random numbers (xorshift 16)
Rand:	move.w	Seed,d0
	move.w	d0,d1
	lsl.w	#7,d1
	eor.w	d1,d0
	move.w	d0,d1
	lsr.w	#8,d1
	lsr.w	#1,d1
	eor.w	d1,d0
	move.w	d0,d1
	lsl.w	#8,d1
	eor.w	d1,d0
	move.w	d0,Seed
	rts

; RandN: d0 = n -> d0 = 0..n-1 (keeps d1)
RandN:	movem.l	d1-d2,-(sp)
	move.w	d0,d2
	bsr	Rand
	mulu	d2,d0
	clr.w	d0
	swap	d0
	movem.l	(sp)+,d1-d2
	rts

;---------------------------------------------------------------------
; sound: channels 0+1 music, 2+3 effects; all four loop their wave
; all the time, only the period and the volume change
InitSound:
	lea	CUSTOM,a5
	moveq	#3,d0
.c:	moveq	#0,d1
	bsr	SetWave
	dbf	d0,.c
	moveq	#0,d0
	move.w	d0,$a8(a5)
	move.w	d0,$b8(a5)
	move.w	d0,$c8(a5)
	move.w	d0,$d8(a5)
	move.w	#400,$a6(a5)
	move.w	#400,$b6(a5)
	move.w	#400,$c6(a5)
	move.w	#400,$d6(a5)
	move.w	#$00ff,$9e(a5)		; no modulation
	move.w	#$820f,$96(a5)		; audio DMA on
	rts

; SetWave: d0 = channel, d1 = wave
SetWave:
	movem.l	d0-d1/a0-a1,-(sp)
	lea	CUSTOM+$a0,a0
	lsl.w	#4,d0
	add.w	d0,a0
	lea	WaveTab,a1
	mulu	#6,d1
	add.w	d1,a1
	move.l	(a1)+,(a0)
	move.w	(a1),4(a0)
	movem.l	(sp)+,d0-d1/a0-a1
	rts

; PlaySfx: d0 = effect
PlaySfx:
	movem.l	d0-d1/a0-a1,-(sp)
	lea	SfxTab,a0
	add.w	d0,d0
	add.w	d0,d0
	move.l	(a0,d0.w),a1
	lea	SfxPtr,a0
	moveq	#0,d0
	tst.l	(a0)
	beq.s	.got
	moveq	#1,d0
	tst.l	4(a0)
	beq.s	.got
	move.w	SfxNext,d0
	eor.w	#1,SfxNext
.got:	move.w	(a1)+,d1
	addq.w	#2,d0
	bsr	SetWave
	subq.w	#2,d0
	add.w	d0,d0
	add.w	d0,d0
	move.l	a1,(a0,d0.w)
	movem.l	(sp)+,d0-d1/a0-a1
	rts

SoundFrame:
	movem.l	d0-d3/a0-a2,-(sp)
	lea	CUSTOM+$c0,a2		; channel 2
	lea	SfxPtr,a0
	moveq	#1,d3
.s:	move.l	(a0),d0
	beq.s	.sn
	move.l	d0,a1
	move.w	(a1)+,d0
	beq.s	.se
	move.w	(a1)+,d1
	move.w	d0,6(a2)
	move.w	d1,8(a2)
	move.l	a1,(a0)
	bra.s	.sn
.se:	clr.w	8(a2)
	clr.l	(a0)
.sn:	addq.l	#4,a0
	lea	16(a2),a2
	dbf	d3,.s
	; music
	lea	CUSTOM+$a0,a2
	tst.b	MusicOn
	beq	.mute
	tst.l	MusPtr
	beq	.mute
	lea	MusPtr,a0
	lea	MusState,a1
	moveq	#0,d3			; channel 0 and 1
.m:	subq.w	#1,(a1)			; frames left of the note
	bgt.s	.env
	move.l	(a0),a2
.rd:	move.w	(a2)+,d0
	cmp.w	#$ffff,d0
	bne.s	.nl
	move.l	8(a0),a2		; loop
	bra.s	.rd
.nl:	move.w	(a2)+,(a1)
	move.l	a2,(a0)
	move.w	d0,4(a1)		; period
	clr.w	2(a1)			; age
.env:	lea	CUSTOM+$a0,a2
	move.w	d3,d0
	lsl.w	#4,d0
	add.w	d0,a2
	move.w	4(a1),d0
	beq.s	.rest
	move.w	d0,6(a2)
	moveq	#22,d1			; melody volume (music kept down)
	tst.w	d3
	beq.s	.v
	moveq	#30,d1			; bass
.v:	move.w	2(a1),d2
	lsr.w	#2,d2
	sub.w	d2,d1
	cmp.w	#7,d1
	bge.s	.v2
	moveq	#7,d1
.v2:	cmp.w	#2,(a1)
	bgt.s	.v3
.rest:	moveq	#0,d1
.v3:	move.w	d1,8(a2)
	addq.w	#1,2(a1)
	addq.l	#4,a0
	addq.l	#6,a1
	addq.w	#1,d3
	cmp.w	#2,d3
	blt	.m
	bra.s	.x
.mute:	clr.w	8(a2)
	clr.w	$18(a2)
.x:	movem.l	(sp)+,d0-d3/a0-a2
	rts

; StartTune: a0 = melody, a1 = bass
StartTune:
	movem.l	d0-d1,-(sp)
	move.l	a0,MusPtr
	move.l	a1,MusPtr+4
	move.l	a0,MusStart
	move.l	a1,MusStart+4
	lea	MusState,a0
	move.w	#1,(a0)
	move.w	#1,6(a0)
	clr.w	4(a0)
	clr.w	10(a0)
	moveq	#0,d0
	moveq	#1,d1			; melody: PU16
	bsr	SetWave
	moveq	#1,d0
	moveq	#2,d1			; bass: TRI32
	bsr	SetWave
	movem.l	(sp)+,d0-d1
	rts

StopTune:
	clr.l	MusPtr
	clr.l	MusPtr+4
	clr.w	CUSTOM+$a8
	clr.w	CUSTOM+$b8
	rts

;---------------------------------------------------------------------
Intro:	bsr	Cls
	lea	IntroPic,a0
	bsr	CopyPic
	lea	TxPresents(pc),a0
	moveq	#22,d1
	move.w	#T_FONTW,d2
	bsr	CenterText
	bsr	FadeIn
	move.w	#110,d0
	bsr	WaitFrames
	bsr	FadeOut
	rts

;---------------------------------------------------------------------
; the title: returns d0 = 0 to play, -1 to quit
Title:	lea	TuneTitleMel,a0
	lea	TuneTitleBas,a1
	bsr	StartTune
.page1:	bsr	Cls
	lea	TitlePic,a0
	bsr	CopyPic
	bsr	TitleTexts
	bsr	FadeIn
	move.w	#600,TitleTimer
	bra.s	.loop
.page2:	bsr	FadeOut
	bsr	HowToPage
	bsr	FadeIn
	move.w	#650,TitleTimer
	move.b	#1,TitlePage
.loop:	clr.b	FireHit
	move.b	#$ff,LastKey
.wait:	bsr	WaitFrame
	move.b	LastKey,d0
	move.b	#$ff,LastKey
	cmp.b	#$45,d0			; Esc: back to Workbench
	beq	.quit
	cmp.b	#$22,d0			; Ctrl + Alt + D: developer mode
	bne.s	.nodev
	lea	KeyTab,a0
	tst.b	$63(a0)
	beq.s	.nodev
	tst.b	$64(a0)
	bne.s	.dev
	tst.b	$65(a0)
	beq.s	.nodev
.dev:	not.b	DevMode
	moveq	#SFX_HEART,d0
	bsr	PlaySfx
	tst.b	TitlePage
	bne.s	.nodev
	bsr	TitleTexts
.nodev:	tst.b	FireHit
	bne.s	.start
	subq.w	#1,TitleTimer
	bgt.s	.wait
	tst.b	TitlePage
	beq	.page2
	clr.b	TitlePage
	bsr	FadeOut
	bra	.page1
.start:	clr.b	FireHit
	clr.b	TitlePage
	moveq	#SFX_START,d0
	bsr	PlaySfx
	bsr	FadeOut
	bsr	StopTune
	moveq	#0,d0
	rts
.quit:	bsr	FadeOut
	moveq	#-1,d0
	rts

TitleTexts:
	lea	TxPress(pc),a0
	moveq	#21,d1
	move.w	#T_FONTY,d2
	bsr	CenterText
	lea	TxHi(pc),a0
	moveq	#11,d0
	moveq	#23,d1
	move.w	#T_FONTW,d2
	bsr	DrawText
	move.l	HiScore,d0
	moveq	#7,d1
	moveq	#21,d2
	moveq	#23,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	lea	TxCredit(pc),a0
	moveq	#25,d1
	move.w	#T_FONTW,d2
	bsr	CenterText
	lea	TxVersion(pc),a0
	moveq	#26,d1
	move.w	#T_FONTW,d2
	bsr	CenterText
	lea	TxControls(pc),a0
	moveq	#28,d1
	move.w	#T_FONTC,d2
	bsr	CenterText
	lea	TxKeys(pc),a0
	moveq	#29,d1
	move.w	#T_FONTC,d2
	bsr	CenterText
	moveq	#31,d1
	lea	TxBlank(pc),a0
	move.w	#T_FONTW,d2
	moveq	#0,d0
	bsr	DrawText
	if	DEMO
	lea	TxDemoTitle(pc),a0
	moveq	#1,d0
	move.w	#T_FONTG,d2
	bsr	DrawText
	endc
	tst.b	DevMode
	beq.s	.nd
	lea	TxDevMode(pc),a0
	moveq	#31,d0
	move.w	#T_FONTC,d2
	bsr	DrawText
.nd:	rts

HowToPage:
	bsr	Cls
	lea	HowTo(pc),a2
.l:	move.b	(a2)+,d1		; row (0 = the end)
	beq.s	.x
	ext.w	d1
	move.b	(a2)+,d0		; column
	ext.w	d0
	moveq	#0,d2
	move.b	(a2)+,d2		; font: 0 white, 1 yellow, 2 green, 3 cyan
	lea	Fonts(pc),a0
	add.w	d2,d2
	move.w	(a0,d2.w),d2
	move.b	(a2)+,d3		; a tile in front (0 = none)
	beq.s	.t
	movem.l	d0-d2,-(sp)
	subq.w	#2,d0
	ext.w	d3
	move.w	d3,d2
	bsr	DrawTile
	movem.l	(sp)+,d0-d2
.t:	move.l	a2,a0
	bsr	DrawText
.n:	tst.b	(a2)+
	bne.s	.n
	bra.s	.l
.x:	rts

Fonts:	dc.w	T_FONTW,T_FONTY,T_FONTG,T_FONTC

TxPresents:	dc.b	'PRESENTS',0
TxPress:	dc.b	'PRESS FIRE TO START',0
TxHi:		dc.b	'HI-SCORE',0
TxCredit:	dc.b	'CREATED BY MARK STRONKS, STRONKIE SOFT',0
TxVersion:	dc.b	'@ 2026  -  VERSION '
		VERSION
		if	DEMO
		dc.b	' DEMO'
		endc
		dc.b	0
TxControls:	dc.b	'JOYSTICK IN PORT 2 OR CURSOR KEYS',0
TxKeys:		dc.b	'M MUSIC  P PAUSE  ESC QUIT',0
TxBlank:	dc.b	'                                        ',0
TxDevMode:	dc.b	'DEV MODE',0
		if	DEMO
TxDemoTitle:	dc.b	'DEMO: 3 ROUNDS',0
		endc
	even
; how to play: row, column, font, tile, text
HowTo:	dc.b	1,14,1,0,'HOW TO PLAY',0
	dc.b	3,3,0,0,'STEER YOUR SNAKE ACROSS THE MEADOW.',0
	dc.b	6,6,2,T_CLOVER,'CLOVER  20 - YOUR SNAKE GROWS',0
	dc.b	7,6,0,0,'AND A BALL POPS UP SOMEWHERE',0
	dc.b	9,6,0,T_BALL,'BALL    50 - EAT THEM ALL TOO!',0
	dc.b	11,6,0,T_MUSH,'MUSHROOM  - POISON, KEEP AWAY',0
	dc.b	13,6,0,T_HEART,'HEART  100 - BONUS MULTIPLIER +1',0
	dc.b	15,6,0,T_WALL10,'WALLS AND YOUR OWN TAIL KILL',0
	dc.b	18,3,3,0,'CLEAR EVERY CLOVER AND EVERY BALL',0
	dc.b	19,3,3,0,'TO FINISH THE ROUND. THE BONUS',0
	dc.b	20,3,3,0,'COUNTS DOWN - WHEN IT RUNS OUT,',0
	dc.b	21,3,3,0,'NEW MUSHROOMS START TO SPROUT!',0
	dc.b	23,3,0,0,'EXTRA LIFE EVERY 10000 POINTS.',0
	if	DEMO
	dc.b	25,3,2,0,'THIS DEMO HAS 3 OF THE 12 ROUNDS.',0
	else
	dc.b	25,3,2,0,'12 ROUNDS - THEN IT ALL GOES FASTER.',0
	endc
	dc.b	29,10,1,0,'PRESS FIRE TO START',0
	dc.b	0
	even

;---------------------------------------------------------------------
; the game
Game:	clr.l	Score
	move.w	#3,Lives
	move.l	#10000,NextLife
	move.w	#1,Round
	move.w	FrameCount+2,d0
	eor.w	d0,Seed
	move.w	CUSTOM+6,d0
	eor.w	d0,Seed
	bne.s	.s
	move.w	#$1234,Seed
.s:	lea	TuneGameMel,a0
	lea	TuneGameBas,a1
	bsr	StartTune
.round:	bsr	StartRound
.play:	bsr	PlayLoop
	cmp.w	#2,d0
	beq	.end
	cmp.w	#1,d0
	beq.s	.died
	bsr	RoundClear
	addq.w	#1,Round
	if	DEMO
	cmp.w	#3,Round
	ble.s	.round
	bsr	DemoEnd
	bra.s	.end
	else
	bra.s	.round
	endc
.died:	bsr	DeathAnim
	tst.b	DevMode
	bne.s	.again
	subq.w	#1,Lives
	bsr	DrawLives
	tst.w	Lives
	beq.s	.over
.again:	bsr	RemoveSnake
	bsr	RemoveHeart
	bsr	InitSnake
	bsr	GetReady
	bra.s	.play
.over:	bsr	GameOver
.end:	bsr	StopTune
	tst.b	DevMode
	bne.s	.x
	move.l	Score,d0
	cmp.l	HiScore,d0
	bls.s	.x
	move.l	d0,HiScore
.x:	bsr	FadeOut
	bra	Cls

; StartRound: the level, the snake, the HUD, "ROUND n"
StartRound:
	bsr	FadeOut
	bsr	Cls
	moveq	#0,d0
	move.w	Round,d0
	subq.w	#1,d0
	divu	#NLEVELS,d0		; loops : level
	move.w	d0,d1			; loops
	swap	d0
	move.w	d0,LevelIdx
	; speed: frames a step, 8 at the start, quicker every 3 rounds
	; and 2 quicker every time round 12 is done
	moveq	#0,d2
	move.w	d0,d2
	divu	#3,d2
	moveq	#8,d3
	sub.w	d2,d3
	add.w	d1,d1
	sub.w	d1,d3
	cmp.w	#3,d3
	bge.s	.sp
	moveq	#3,d3
.sp:	move.w	d3,Speed
	bsr	LoadLevel
	bsr	DrawHud
	bsr	DrawField
	move.w	#1000,Bonus
	move.w	#1,Mult
	bsr	DrawBonus
	clr.b	HeartOn
	move.w	#400,HeartTimer
	move.w	#30,BonusTimer
	move.w	#250,SproutTimer
	bsr	InitSnake
	bsr	FadeIn
	; ROUND n + the name
	lea	TxRound(pc),a0
	lea	MsgBuf,a1
.c:	move.b	(a0)+,(a1)+
	bne.s	.c
	subq.l	#1,a1
	moveq	#0,d0
	move.w	Round,d0
	bsr	Div10
	tst.w	d0
	beq.s	.one
	add.b	#'0',d0
	move.b	d0,(a1)+
.one:	add.b	#'0',d1
	move.b	d1,(a1)+
	clr.b	(a1)
	lea	MsgBuf,a0
	moveq	#12,d1
	bsr	ShowMsg
	move.l	LevelName,a0
	moveq	#14,d1
	bsr	ShowMsg
	moveq	#SFX_READY,d0
	bsr	PlaySfx
	move.w	#110,d0
	bsr	WaitFrames
	moveq	#12,d1
	bsr	HideMsg
	moveq	#14,d1
	bsr	HideMsg
	bra	ResetControl

GetReady:
	lea	TxReady(pc),a0
	moveq	#14,d1
	bsr	ShowMsg
	moveq	#SFX_READY,d0
	bsr	PlaySfx
	move.w	#80,d0
	bsr	WaitFrames
	moveq	#14,d1
	bsr	HideMsg
ResetControl:
	clr.w	QCount
	clr.b	JoyHit
	clr.b	FireHit
	clr.b	Dead
	move.b	#$ff,LastKey
	move.w	Speed,StepTimer
	rts

TxRound:	dc.b	'ROUND ',0
TxReady:	dc.b	'GET READY!',0
TxClear:	dc.b	'ROUND CLEAR!',0
TxBonus:	dc.b	'BONUS',0
TxPaused:	dc.b	'PAUSED',0
TxGameOver:	dc.b	'GAME OVER',0
TxScore:	dc.b	'SCORE:',0
TxLives:	dc.b	'LIVES:',0
TxHiS:		dc.b	'HI:',0
TxBonusH:	dc.b	'BONUS:',0
TxRoundH:	dc.b	'ROUND:',0
TxTimes:	dc.b	'*',0
TxDemo:		dc.b	'DEMO',0
TxDev:		dc.b	'DEV',0
	even

; LoadLevel: Map, TileMap and Remaining from level LevelIdx
LoadLevel:
	lea	Map,a0
	move.w	#40*32-1,d0
.f:	move.b	#C_WALL,(a0)+
	dbf	d0,.f
	lea	TileMap,a0
	move.w	#40*32-1,d0
.t:	clr.w	(a0)+
	dbf	d0,.t
	lea	Levels,a1
	move.w	LevelIdx,d0
	mulu	#LEVSIZE,d0
	add.l	d0,a1
	move.l	a1,LevelName
	lea	32(a1),a1
	lea	Map+FIELDY*40+FIELDX,a0
	clr.w	Remaining
	moveq	#FIELDH-1,d1
.y:	moveq	#FIELDW-1,d0
.x:	move.b	(a1)+,d2
	move.b	d2,(a0)+
	cmp.b	#C_CLOVER,d2
	bne.s	.nc
	addq.w	#1,Remaining
.nc:	dbf	d0,.x
	lea	40-FIELDW(a0),a0
	dbf	d1,.y
	; the tiles of the field and its border
	move.w	#(FIELDY-1)*40+FIELDX-1,d0
	moveq	#FIELDH+1,d3		; rows
.ry:	moveq	#FIELDW+1,d4		; columns
	move.w	d0,d5
.rx:	bsr	CellTile
	lea	TileMap,a0
	add.w	d0,a0
	add.w	d0,a0
	move.w	d2,(a0)
	addq.w	#1,d0
	dbf	d4,.rx
	move.w	d5,d0
	add.w	#40,d0
	dbf	d3,.ry
	rts

; CellTile: d0 = cell -> d2 = its tile (walls by their neighbours)
CellTile:
	movem.l	d0-d1/d3/a0,-(sp)
	lea	Map,a0
	moveq	#0,d1
	move.b	(a0,d0.w),d1
	add.w	d1,d1
	move.w	.tab(pc,d1.w),d2
	cmp.w	#C_WALL*2,d1
	bne.s	.x
	; the wall neighbours inside the border box
	moveq	#0,d3
	moveq	#0,d1
	move.w	d0,d1
	divu	#40,d1			; d1 = col:row
	cmp.w	#FIELDY-1,d1
	ble.s	.nu
	cmp.b	#C_WALL,-40(a0,d0.w)
	bne.s	.nu
	or.w	#1,d3
.nu:	cmp.w	#FIELDY+FIELDH,d1
	bge.s	.nd
	cmp.b	#C_WALL,40(a0,d0.w)
	bne.s	.nd
	or.w	#4,d3
.nd:	swap	d1
	cmp.w	#FIELDX-1,d1
	ble.s	.nl
	cmp.b	#C_WALL,-1(a0,d0.w)
	bne.s	.nl
	or.w	#8,d3
.nl:	cmp.w	#FIELDX+FIELDW,d1
	bge.s	.nr
	cmp.b	#C_WALL,1(a0,d0.w)
	bne.s	.nr
	or.w	#2,d3
.nr:	move.w	#T_WALL0,d2
	add.w	d3,d2
.x:	movem.l	(sp)+,d0-d1/d3/a0
	rts
.tab:	dc.w	T_EMPTY,T_WALL0,T_CLOVER,T_BALL,T_MUSH,T_EMPTY

DrawField:
	move.w	#(FIELDY-1)*40+FIELDX-1,d0
	moveq	#FIELDH+1,d3
.y:	moveq	#FIELDW+1,d4
	move.w	d0,d5
.x:	bsr	RedrawCell
	addq.w	#1,d0
	dbf	d4,.x
	move.w	d5,d0
	add.w	#40,d0
	dbf	d3,.y
	rts

;---------------------------------------------------------------------
; the HUD
DrawHud:
	move.w	#T_FONTW,d2
	lea	TxScore(pc),a0
	moveq	#1,d0
	moveq	#0,d1
	bsr	DrawText
	lea	TxBonusH(pc),a0
	moveq	#22,d0
	bsr	DrawText
	lea	TxLives(pc),a0
	moveq	#1,d0
	moveq	#1,d1
	bsr	DrawText
	lea	TxHiS(pc),a0
	moveq	#11,d0
	bsr	DrawText
	lea	TxRoundH(pc),a0
	moveq	#22,d0
	bsr	DrawText
	move.l	HiScore,d0
	moveq	#7,d1
	moveq	#14,d2
	moveq	#1,d3
	move.w	#T_FONTW,d4
	bsr	DrawNum
	moveq	#0,d0
	move.w	Round,d0
	moveq	#2,d1
	moveq	#29,d2
	moveq	#1,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	if	DEMO
	lea	TxDemo(pc),a0
	moveq	#1,d0
	moveq	#2,d1
	move.w	#T_FONTG,d2
	bsr	DrawText
	endc
	tst.b	DevMode
	beq.s	.nd
	lea	TxDev(pc),a0
	moveq	#36,d0
	moveq	#2,d1
	move.w	#T_FONTC,d2
	bsr	DrawText
.nd:	bsr	DrawScore
	bsr	DrawLives
	bra	DrawBonus

DrawScore:
	movem.l	d0-d4,-(sp)
	move.l	Score,d0
	moveq	#7,d1
	moveq	#8,d2
	moveq	#0,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	movem.l	(sp)+,d0-d4
	rts

DrawLives:
	movem.l	d0-d4,-(sp)
	moveq	#0,d0
	move.w	Lives,d0
	moveq	#2,d1
	moveq	#8,d2
	moveq	#1,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	movem.l	(sp)+,d0-d4
	rts

DrawBonus:
	movem.l	d0-d4/a0,-(sp)
	moveq	#0,d0
	move.w	Bonus,d0
	moveq	#4,d1
	moveq	#29,d2
	moveq	#0,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	lea	TxTimes(pc),a0
	moveq	#33,d0
	moveq	#0,d1
	move.w	#T_FONTW,d2
	bsr	DrawText
	moveq	#0,d0
	move.w	Mult,d0
	moveq	#1,d1
	moveq	#34,d2
	moveq	#0,d3
	move.w	#T_FONTY,d4
	bsr	DrawNum
	movem.l	(sp)+,d0-d4/a0
	rts

; AddScore: d0.l = points (an extra life every 10000)
AddScore:
	movem.l	d0,-(sp)
	add.l	d0,Score
	move.l	Score,d0
	cmp.l	NextLife,d0
	blo.s	.x
	add.l	#10000,NextLife
	addq.w	#1,Lives
	bsr	DrawLives
	moveq	#SFX_LIFE,d0
	bsr	PlaySfx
.x:	bsr	DrawScore
	movem.l	(sp)+,d0
	rts

;---------------------------------------------------------------------
; the snake: Ring holds the cells, Ring[HeadIdx] is the head,
; segment i is Ring[(HeadIdx - i) & RINGMASK]
InitSnake:
	move.w	#STARTPOS,d0
	lea	Ring,a0
	move.w	#3,HeadIdx
	move.w	#4,Len
	clr.w	Dir
	clr.w	Grow
	lea	Map,a1
	; Ring[3] = head, Ring[2..0] the body below it
	move.w	d0,6(a0)
	add.w	#40,d0
	move.w	d0,4(a0)
	add.w	#40,d0
	move.w	d0,2(a0)
	add.w	#40,d0
	move.w	d0,(a0)
	moveq	#3,d1
.m:	move.w	(a0)+,d0
	move.b	#C_SNAKE,(a1,d0.w)
	dbf	d1,.m
	moveq	#3,d1
.d:	move.w	d1,d0
	bsr	DrawSeg
	dbf	d1,.d
	rts

; SegPos: d0 = segment -> d0 = cell
SegPos:	move.l	a0,-(sp)
	neg.w	d0
	add.w	HeadIdx,d0
	and.w	#RINGMASK,d0
	add.w	d0,d0
	lea	Ring,a0
	move.w	(a0,d0.w),d0
	move.l	(sp)+,a0
	rts

; DirBit: d0 = other cell - this cell -> d0 = 1 up, 2 right, 4 down, 8 left
DirBit:	cmp.w	#-40,d0
	beq.s	.u
	cmp.w	#1,d0
	beq.s	.r
	cmp.w	#40,d0
	beq.s	.d
	cmp.w	#-1,d0
	beq.s	.l
	moveq	#0,d0
	rts
.u:	moveq	#1,d0
	rts
.r:	moveq	#2,d0
	rts
.d:	moveq	#4,d0
	rts
.l:	moveq	#8,d0
	rts

; DrawSeg: d0 = segment: its tile from its neighbours
DrawSeg:
	movem.l	d0-d4,-(sp)
	move.w	d0,d4
	bsr	SegPos
	move.w	d0,d3			; this cell
	tst.w	d4
	bne.s	.body
	move.w	#T_HEAD0,d2
	add.w	Dir,d2
	bra.s	.draw
.body:	move.w	d4,d0
	subq.w	#1,d0
	bsr	SegPos
	sub.w	d3,d0
	bsr	DirBit
	move.w	d0,d2
	move.w	d4,d0
	addq.w	#1,d0
	cmp.w	Len,d0
	bge.s	.tail
	bsr	SegPos
	sub.w	d3,d0
	bsr	DirBit
	or.w	d0,d2
.tail:	add.w	#T_SNAKE0,d2
.draw:	move.w	d3,d0
	bsr	SetCell
	movem.l	(sp)+,d0-d4
	rts

RemoveSnake:
	movem.l	d0-d2/a0,-(sp)
	move.w	Len,d1
	subq.w	#1,d1
	lea	Map,a0
.l:	move.w	d1,d0
	bsr	SegPos
	clr.b	(a0,d0.w)
	moveq	#T_EMPTY,d2
	bsr	SetCell
	dbf	d1,.l
	movem.l	(sp)+,d0-d2/a0
	rts

DirDelta:	dc.w	-40,1,40,-1

; Step: move the snake one cell
Step:	tst.w	QCount
	beq.s	.noq
	move.w	Queue,Dir
	move.w	Queue+2,Queue
	subq.w	#1,QCount
.noq:	move.w	Dir,d0
	add.w	d0,d0
	move.w	DirDelta(pc,d0.w),d1
	moveq	#0,d0
	bsr	SegPos
	add.w	d1,d0
	move.w	d0,d3			; the new head cell
	tst.b	HeartOn
	beq.s	.nh
	cmp.w	HeartPos,d3
	bne.s	.nh
	bsr	EatHeart
.nh:	lea	Map,a0
	moveq	#0,d4
	move.b	(a0,d3.w),d4
	cmp.b	#C_SNAKE,d4
	bne.s	.nb
	tst.w	Grow			; the tail cell is free if it moves
	bne	.die
	move.w	Len,d0
	subq.w	#1,d0
	bsr	SegPos
	cmp.w	d3,d0
	bne	.die
	bra.s	.move
.nb:	cmp.b	#C_WALL,d4
	beq	.die
	cmp.b	#C_MUSH,d4
	beq	.die
	cmp.b	#C_CLOVER,d4
	bne.s	.nc
	moveq	#20,d0
	bsr	AddScore
	addq.w	#GROWBY,Grow
	subq.w	#1,Remaining
	st	SpawnBall
	moveq	#SFX_CLOVER,d0
	bsr	PlaySfx
	bra.s	.move
.nc:	cmp.b	#C_BALL,d4
	bne.s	.move
	moveq	#50,d0
	bsr	AddScore
	subq.w	#1,Remaining
	moveq	#SFX_BALL,d0
	bsr	PlaySfx
.move:	tst.w	Grow
	beq.s	.cut
	subq.w	#1,Grow
	bra.s	.head
.cut:	move.w	Len,d0
	subq.w	#1,d0
	bsr	SegPos
	clr.b	(a0,d0.w)
	moveq	#T_EMPTY,d2
	bsr	SetCell
	subq.w	#1,Len
.head:	move.w	HeadIdx,d0
	addq.w	#1,d0
	and.w	#RINGMASK,d0
	move.w	d0,HeadIdx
	add.w	d0,d0
	lea	Ring,a1
	move.w	d3,(a1,d0.w)
	move.b	#C_SNAKE,(a0,d3.w)
	addq.w	#1,Len
	moveq	#0,d0
	bsr	DrawSeg
	moveq	#1,d0
	bsr	DrawSeg
	move.w	Len,d0
	subq.w	#1,d0
	bsr	DrawSeg
	tst.b	SpawnBall
	beq.s	.x
	clr.b	SpawnBall
	moveq	#0,d7
	bsr	RandomCell
	tst.w	d0
	bmi.s	.x
	move.b	#C_BALL,(a0,d0.w)
	moveq	#T_BALL,d2
	bsr	SetCell
	addq.w	#1,Remaining
.x:	rts
.die:	st	Dead
	rts

; RandomCell: d7 = 1: also the four neighbours must be empty
; -> d0 = an empty cell away from the head and the start, or -1
RandomCell:
	movem.l	d1-d6/a0,-(sp)
	lea	Map,a0
	moveq	#0,d0
	bsr	SegPos
	moveq	#0,d5
	move.w	d0,d5
	divu	#40,d5			; head: col:row
	move.w	#299,d6
.try:	moveq	#FIELDW,d0
	bsr	RandN
	addq.w	#FIELDX,d0
	move.w	d0,d1			; col
	moveq	#FIELDH,d0
	bsr	RandN
	addq.w	#FIELDY,d0
	move.w	d0,d2			; row
	mulu	#40,d0
	add.w	d1,d0
	tst.b	(a0,d0.w)
	bne.s	.no
	tst.b	HeartOn
	beq.s	.nh
	cmp.w	HeartPos,d0
	beq.s	.no
.nh:	; not in the start box: |col-20| <= 3 and |row-25| <= 5
	move.w	d1,d3
	sub.w	#20,d3
	bpl.s	.a1
	neg.w	d3
.a1:	cmp.w	#3,d3
	bgt.s	.ok1
	move.w	d2,d3
	sub.w	#25,d3
	bpl.s	.a2
	neg.w	d3
.a2:	cmp.w	#5,d3
	ble.s	.no
.ok1:	; not next to the head
	swap	d5
	move.w	d1,d3
	sub.w	d5,d3
	swap	d5
	bpl.s	.a3
	neg.w	d3
.a3:	cmp.w	#2,d3
	bgt.s	.ok2
	move.w	d2,d3
	sub.w	d5,d3
	bpl.s	.a4
	neg.w	d3
.a4:	cmp.w	#2,d3
	ble.s	.no
.ok2:	tst.w	d7
	beq.s	.yes
	tst.b	-1(a0,d0.w)
	bne.s	.no
	tst.b	1(a0,d0.w)
	bne.s	.no
	tst.b	-40(a0,d0.w)
	bne.s	.no
	tst.b	40(a0,d0.w)
	bne.s	.no
.yes:	movem.l	(sp)+,d1-d6/a0
	rts
.no:	dbf	d6,.try
	moveq	#-1,d0
	movem.l	(sp)+,d1-d6/a0
	rts

; the joystick: new presses go into a queue of two turns
HandleJoy:
	move.b	JoyHit,d0
	clr.b	JoyHit
	and.w	#15,d0
	bne.s	.new
	tst.w	QCount
	bne.s	.x
	move.b	JoyDir,d0
	and.w	#15,d0
	beq.s	.x
.new:	moveq	#0,d1
.b:	btst	d1,d0
	beq.s	.nb
	bsr	Enqueue
	tst.w	d2
	bne.s	.x
.nb:	addq.w	#1,d1
	cmp.w	#4,d1
	blt.s	.b
.x:	rts

; Enqueue: d1 = direction -> d2 = 1 if taken
Enqueue:
	move.w	Dir,d3
	move.w	QCount,d2
	beq.s	.c
	lea	Queue,a0
	add.w	d2,d2
	move.w	-2(a0,d2.w),d3
.c:	moveq	#0,d2
	cmp.w	d3,d1
	beq.s	.x
	eor.w	#2,d3
	cmp.w	d3,d1			; no turning back into yourself
	beq.s	.x
	move.w	QCount,d3
	cmp.w	#2,d3
	bge.s	.x
	lea	Queue,a0
	add.w	d3,d3
	move.w	d1,(a0,d3.w)
	addq.w	#1,QCount
	moveq	#1,d2
.x:	rts

;---------------------------------------------------------------------
; PlayLoop: -> d0 = 0 round clear, 1 died, 2 quit
PlayLoop:
.l:	bsr	WaitFrame
	move.b	LastKey,d0
	move.b	#$ff,LastKey
	cmp.b	#$45,d0			; Esc
	beq.s	.quit
	cmp.b	#$19,d0			; P
	bne.s	.np
	bsr	Pause
	bra.s	.l
.np:	tst.b	DevMode
	beq.s	.nd
	cmp.b	#$36,d0			; dev: N = next round
	beq.s	.clear
.nd:	bsr	HandleJoy
	bsr	BonusTick
	bsr	HeartTick
	bsr	SproutTick
	subq.w	#1,StepTimer
	bgt.s	.l
	move.w	Speed,StepTimer
	bsr	Step
	tst.b	Dead
	bne.s	.dead
	tst.w	Remaining
	bne.s	.l
.clear:	moveq	#0,d0
	rts
.dead:	moveq	#1,d0
	rts
.quit:	moveq	#2,d0
	rts

Pause:	lea	TxPaused(pc),a0
	moveq	#15,d1
	bsr	ShowMsg
.w:	bsr	WaitFrame
	move.b	LastKey,d0
	move.b	#$ff,LastKey
	cmp.b	#$19,d0
	beq.s	.x
	tst.b	FireHit
	beq.s	.w
.x:	clr.b	FireHit
	clr.b	JoyHit
	moveq	#15,d1
	bra	HideMsg

BonusTick:
	subq.w	#1,BonusTimer
	bgt.s	.x
	move.w	#30,BonusTimer
	tst.w	Bonus
	beq.s	.x
	sub.w	#10,Bonus
	bsr	DrawBonus
.x:	rts

; when the bonus has run out, a mushroom sprouts every 5 seconds
SproutTick:
	tst.w	Bonus
	bne.s	.x
	subq.w	#1,SproutTimer
	bgt.s	.x
	move.w	#250,SproutTimer
	moveq	#1,d7
	bsr	RandomCell
	tst.w	d0
	bmi.s	.x
	lea	Map,a0
	move.b	#C_MUSH,(a0,d0.w)
	moveq	#T_MUSH,d2
	bsr	SetCell
	moveq	#SFX_SPROUT,d0
	bsr	PlaySfx
.x:	rts

; the heart drifts across the field (diagonally, bouncing)
HeartTick:
	tst.b	HeartOn
	bne.s	.on
	subq.w	#1,HeartTimer
	bgt	.x
	moveq	#0,d7
	bsr	RandomCell
	tst.w	d0
	bpl.s	.sp
	move.w	#100,HeartTimer
	rts
.sp:	move.w	d0,HeartPos
	moveq	#2,d0
	bsr	RandN
	add.w	d0,d0
	subq.w	#1,d0
	move.w	d0,HeartDX		; -1 or 1
	moveq	#2,d0
	bsr	RandN
	mulu	#80,d0
	sub.w	#40,d0
	move.w	d0,HeartDY		; -40 or 40
	move.w	#650,HeartLife
	move.w	#10,HeartMove
	st	HeartOn
	bra	.draw
.on:	subq.w	#1,HeartLife
	ble	.gone
	subq.w	#1,HeartMove
	bgt	.draw
	move.w	#10,HeartMove
	moveq	#0,d0
	bsr	SegPos
	move.w	d0,d5			; the head
	lea	Map,a0
	moveq	#3,d6			; four tries: go on, bounce x, bounce y, back
.try:	move.w	HeartPos,d0
	add.w	HeartDX,d0
	add.w	HeartDY,d0
	cmp.w	d5,d0
	beq.s	.eat
	tst.b	(a0,d0.w)
	beq.s	.go
	cmp.w	#3,d6
	bne.s	.t2
	neg.w	HeartDX
	bra.s	.tn
.t2:	cmp.w	#2,d6
	bne.s	.t3
	neg.w	HeartDX
	neg.w	HeartDY
	bra.s	.tn
.t3:	neg.w	HeartDX
.tn:	dbf	d6,.try
	bra.s	.draw
.go:	move.w	d0,d1
	move.w	HeartPos,d0
	bsr	RedrawCell
	move.w	d1,HeartPos
	bra.s	.draw
.eat:	move.w	HeartPos,d0
	bsr	RedrawCell
	move.w	d5,HeartPos
	bra	EatHeart
.draw:	move.w	#T_HEART,d2
	cmp.w	#150,HeartLife
	bgt.s	.d2
	btst	#3,HeartLife+1
	beq.s	.d2
	move.w	#T_HEART2,d2
.d2:	move.w	HeartPos,d0
	bra	DrawPos
.gone:	bsr	RemoveHeart
.x:	rts

RemoveHeart:
	tst.b	HeartOn
	beq.s	.t
	move.w	HeartPos,d0
	bsr	RedrawCell
	clr.b	HeartOn
.t:	move.w	#500,d0
	bsr	RandN
	add.w	#450,d0
	move.w	d0,HeartTimer
	rts

EatHeart:
	movem.l	d0-d2/a0,-(sp)
	cmp.w	#9,Mult
	bge.s	.m
	addq.w	#1,Mult
.m:	moveq	#100,d0
	bsr	AddScore
	bsr	DrawBonus
	moveq	#SFX_HEART,d0
	bsr	PlaySfx
	bsr	RemoveHeart
	movem.l	(sp)+,d0-d2/a0
	rts

;---------------------------------------------------------------------
DeathAnim:
	bsr	RemoveHeart
	moveq	#SFX_DIE,d0
	bsr	PlaySfx
	moveq	#0,d0
	bsr	SegPos
	moveq	#T_DEADHEAD,d2
	bsr	SetCell
	moveq	#47,d3
.l:	lea	CurPal,a0
	btst	#2,d3
	beq.s	.n
	move.w	#$e32,16(a0)
	move.w	#$811,18(a0)
	bra.s	.s
.n:	move.w	Palette+16,16(a0)
	move.w	Palette+18,18(a0)
.s:	moveq	#16,d0
	bsr	SetFade
	bsr	WaitFrame
	dbf	d3,.l
	lea	CurPal,a0
	move.w	Palette+16,16(a0)
	move.w	Palette+18,18(a0)
	moveq	#16,d0
	bsr	SetFade
	moveq	#25,d0
	bra	WaitFrames

RoundClear:
	bsr	RemoveHeart
	moveq	#SFX_CLEAR,d0
	bsr	PlaySfx
	lea	TxClear(pc),a0
	moveq	#12,d1
	bsr	ShowMsg
	moveq	#50,d0
	bsr	WaitFrames
.t:	tst.w	Bonus
	beq.s	.d
	sub.w	#10,Bonus
	moveq	#0,d0
	move.w	Mult,d0
	mulu	#10,d0
	bsr	AddScore
	bsr	DrawBonus
	move.l	FrameCount,d0
	and.w	#3,d0
	bne.s	.w
	moveq	#SFX_TICK,d0
	bsr	PlaySfx
.w:	bsr	WaitFrame
	bra.s	.t
.d:	moveq	#90,d0
	bra	WaitFrames

GameOver:
	bsr	StopTune
	lea	TxGameOver(pc),a0
	moveq	#15,d1
	bsr	ShowMsg
	moveq	#SFX_GAMEOVER,d0
	bsr	PlaySfx
	moveq	#40,d0
.w:	bsr	WaitFrame
	dbf	d0,.w
	move.w	#200,d0
	bra	WaitFrames

	if	DEMO
DemoEnd:
	bsr	StopTune
	bsr	FadeOut
	bsr	Cls
	lea	DemoText(pc),a2
.l:	move.b	(a2)+,d1
	beq.s	.go
	ext.w	d1
	moveq	#0,d2
	move.b	(a2)+,d2
	lea	Fonts(pc),a0
	add.w	d2,d2
	move.w	(a0,d2.w),d2
	move.l	a2,a0
	bsr	CenterText
.n:	tst.b	(a2)+
	bne.s	.n
	bra.s	.l
.go:	bsr	FadeIn
	moveq	#SFX_CLEAR,d0
	bsr	PlaySfx
	moveq	#60,d0
.w:	bsr	WaitFrame
	dbf	d0,.w
.f:	move.w	#3000,d0
	bsr	WaitFrames
	rts
DemoText:
	dc.b	3,1,'THANK YOU FOR PLAYING',0
	dc.b	5,1,"THE DEMO OF STRONKIE'S CLOVER SNAKE!",0
	dc.b	9,0,'THE FULL GAME HAS:',0
	dc.b	11,2,'12 ROUNDS WITH WALLS, MAZES,',0
	dc.b	12,2,'SPIRALS AND MUSHROOM FORESTS',0
	dc.b	14,2,'AFTER ROUND 12 IT ALL STARTS',0
	dc.b	15,2,'AGAIN - FASTER!',0
	dc.b	17,2,'A HARD DISK INSTALLER, WHDLOAD',0
	dc.b	18,2,'AND A PRINTABLE BOX AND MANUAL',0
	dc.b	22,3,'GET IT ON STRONKIE.ITCH.IO',0
	dc.b	26,0,'CREATED BY MARK STRONKS, STRONKIE SOFT',0
	dc.b	29,1,'PRESS FIRE',0
	dc.b	0
	even
	endc

;=====================================================================
	section	vars,bss
WBMsg:		ds.l	1
GfxBase:	ds.l	1
OldView:	ds.l	1
OldIntena:	ds.w	1
OldDma:		ds.w	1
CopColors:	ds.l	1
FrameCount:	ds.l	1
CurPal:		ds.w	16
KeyTab:		ds.b	128
LastKey:	ds.b	1
JoyDir:		ds.b	1
JoyHit:		ds.b	1
Fire:		ds.b	1
FireHit:	ds.b	1
MusicOn:	ds.b	1
DevMode:	ds.b	1
TitlePage:	ds.b	1
HeartOn:	ds.b	1
Dead:		ds.b	1
SpawnBall:	ds.b	1
	even
TitleTimer:	ds.w	1
Seed:		ds.w	1
SfxPtr:		ds.l	2
SfxNext:	ds.w	1
MusPtr:		ds.l	2
MusStart:	ds.l	2
MusState:	ds.w	6		; per channel: frames left, age, period
NumBuf:		ds.b	14
MsgBuf:		ds.b	40
	even
Score:		ds.l	1
HiScore:	ds.l	1
NextLife:	ds.l	1
Lives:		ds.w	1
Round:		ds.w	1
LevelIdx:	ds.w	1
LevelName:	ds.l	1
Speed:		ds.w	1
StepTimer:	ds.w	1
Bonus:		ds.w	1
BonusTimer:	ds.w	1
Mult:		ds.w	1
Remaining:	ds.w	1
SproutTimer:	ds.w	1
Dir:		ds.w	1
Queue:		ds.w	2
QCount:		ds.w	1
Grow:		ds.w	1
HeadIdx:	ds.w	1
Len:		ds.w	1
HeartPos:	ds.w	1
HeartDX:	ds.w	1
HeartDY:	ds.w	1
HeartLife:	ds.w	1
HeartMove:	ds.w	1
HeartTimer:	ds.w	1
Ring:		ds.w	RINGMASK+1
Map:		ds.b	40*32
TileMap:	ds.w	40*32

	section	chipvars,bss_c
Screen:		ds.b	SCRSIZE
CopperList:	ds.l	64
