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
C_BLOCK	equ	6

FIELDX	equ	3			; the field inside the border (screen cells)
FIELDY	equ	4
FIELDW	equ	34
FIELDH	equ	27
STARTPOS equ	25*40+20		; the head at the start (moving up)
LEVSIZE	equ	32+FIELDW*FIELDH+32
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
	bsr	Cls
	bsr	InitCopper
	bsr	GamePal
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
	moveq	#4,d2
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
	moveq	#31,d2
.c:	move.w	d1,(a0)+
	clr.w	(a0)+
	addq.w	#2,d1
	dbf	d2,.c
	move.l	a0,CopBpl
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
	move.w	d0,CurBright
	lea	CurPal,a0
	move.l	CopColors,a1
	moveq	#31,d4
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

; SetPlanes: d0 = number of bitplanes (4 for the game, 5 for the pictures)
SetPlanes:
	movem.l	d0/a0,-(sp)
	move.w	d0,CurPlanes
	ror.w	#4,d0
	or.w	#$0200,d0
	move.l	CopBpl,a0
	move.w	d0,2(a0)
	movem.l	(sp)+,d0/a0
	rts

; GamePal: the game's 16 colours, 4 bitplanes
GamePal:
	movem.l	d0/a0-a1,-(sp)
	lea	Palette,a0
	lea	CurPal,a1
	moveq	#15,d0
.p:	move.w	(a0)+,(a1)+
	dbf	d0,.p
	moveq	#15,d0
.z:	clr.w	(a1)+
	dbf	d0,.z
	clr.b	TwinkleOn
	clr.b	MaskText
	moveq	#4,d0
	bsr	SetPlanes
	movem.l	(sp)+,d0/a0-a1
	rts

; ShowPic: a0 = a painted picture (planes, 32 colours, the planes);
; text is then drawn see-through and the fireflies twinkle
ShowPic:
	movem.l	d0/a0-a1,-(sp)
	move.w	(a0)+,d0
	bsr	SetPlanes
	lea	CurPal,a1
	moveq	#31,d0
.p:	move.w	(a0)+,(a1)+
	dbf	d0,.p
	move.l	a0,CurPic
	lea	Screen,a1
	move.w	#PS*5/16-1,d0
.l:	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	move.l	(a0)+,(a1)+
	dbf	d0,.l
	move.b	#1,TwinkleOn
	move.b	#1,MaskText
	movem.l	(sp)+,d0/a0-a1
	rts

; RestoreRow: d1 = text row: the picture back under it (5 planes)
RestoreRow:
	movem.l	d0-d2/a0-a1,-(sp)
	move.l	CurPic,a0
	lea	Screen,a1
	mulu	#320,d1
	add.l	d1,a0
	add.l	d1,a1
	moveq	#4,d2
.pl:	moveq	#79,d0
.l:	move.l	(a0)+,(a1)+
	dbf	d0,.l
	lea	PS-320(a0),a0
	lea	PS-320(a1),a1
	dbf	d2,.pl
	movem.l	(sp)+,d0-d2/a0-a1
	rts

; Twinkle: the fireflies (colours 29-31) take turns to light up
Twinkle:
	tst.b	TwinkleOn
	beq.s	.x
	move.l	FrameCount,d0
	and.w	#7,d0
	bne.s	.x
	lea	CurPal+29*2,a0
	move.w	4(a0),d0
	move.w	2(a0),4(a0)
	move.w	(a0),2(a0)
	move.w	d0,(a0)
	move.w	CurBright,d0
	bsr	SetFade
.x:	rts

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
	bsr	AmbFrame
	movem.l	d0-d1/a0,-(sp)
	bsr	Twinkle
	movem.l	(sp)+,d0-d1/a0
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
	eor.b	#1,MusicOn
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
	tst.b	MaskText
	bne.s	.mask
.l:	move.b	(a1)+,(a0)
	move.b	(a1)+,PS(a0)
	move.b	(a1)+,PS*2(a0)
	move.b	(a1)+,PS*3(a0)
	lea	40(a0),a0
	dbf	d0,.l
	movem.l	(sp)+,d0-d2/a0-a1
	rts
	; see-through: only the pixels of the tile that are not colour 0
.mask:	movem.l	d3-d4,-(sp)
.m:	move.b	(a1),d1
	or.b	1(a1),d1
	or.b	2(a1),d1
	or.b	3(a1),d1
	move.b	d1,d4
	not.b	d4
	moveq	#3,d2
	move.l	a0,-(sp)
.mp:	move.b	(a0),d3
	and.b	d4,d3
	or.b	(a1)+,d3
	move.b	d3,(a0)
	lea	PS(a0),a0
	dbf	d2,.mp
	and.b	d4,(a0)			; plane 5: colours 0-15 only
	move.l	(sp)+,a0
	lea	40(a0),a0
	dbf	d0,.m
	movem.l	(sp)+,d3-d4
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
	beq.s	.got1
	tst.b	SfxAmb			; a forest sound gives way
	bne.s	.got1
	move.w	SfxNext,d0
	eor.w	#1,SfxNext
	tst.w	d0
	beq.s	.got
.got1:	clr.b	SfxAmb
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
	; music: tokens $ffff = back to the start, $fffe = wave,
	; $fffd = envelope (volume, decay shift, lowest volume, vibrato)
	lea	CUSTOM+$a0,a2
	tst.b	MusicOn
	beq	.mute
	tst.l	MusPtr
	beq	.mute
	movem.l	a3,-(sp)
	lea	VibTab(pc),a3
	lea	MusPtr,a0
	lea	MusState,a1
	moveq	#0,d3			; channel 0 and 1
.m:	subq.w	#1,(a1)			; frames left of the note
	bgt.s	.env
	move.l	(a0),a2
.rd:	move.w	(a2)+,d0
	cmp.w	#$fffd,d0
	bcs.s	.nl
	beq.s	.envset
	cmp.w	#$fffe,d0
	beq.s	.wav
	move.l	8(a0),a2		; the end: loop
	bra.s	.rd
.wav:	move.w	(a2)+,d1
	move.w	d3,d0
	bsr	SetWave
	bra.s	.rd
.envset:
	move.w	(a2)+,6(a1)
	move.w	(a2)+,8(a1)
	move.w	(a2)+,10(a1)
	move.w	(a2)+,12(a1)
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
	tst.w	12(a1)			; vibrato after a while
	beq.s	.nov
	move.w	2(a1),d1
	cmp.w	#12,d1
	blt.s	.nov
	lsr.w	#1,d1
	and.w	#7,d1
	move.b	(a3,d1.w),d1
	ext.w	d1
	move.w	d0,d2
	lsr.w	#7,d2
	muls	d2,d1
	add.w	d1,d0
.nov:	move.w	d0,6(a2)
	move.w	6(a1),d1		; volume: falls with the age of the note
	move.w	2(a1),d2
	move.w	8(a1),d0
	lsr.w	d0,d2
	sub.w	d2,d1
	cmp.w	10(a1),d1
	bge.s	.v2
	move.w	10(a1),d1
.v2:	cmp.w	#2,2(a1)		; a soft start
	bge.s	.v3
	move.w	d1,d2
	lsr.w	#2,d2
	sub.w	d2,d1
.v3:	cmp.w	#1,(a1)			; a tiny gap before the next note
	bgt.s	.v4
.rest:	moveq	#0,d1
.v4:	move.w	d1,8(a2)
	addq.w	#1,2(a1)
	addq.l	#4,a0
	lea	16(a1),a1
	addq.w	#1,d3
	cmp.w	#2,d3
	blt	.m
	movem.l	(sp)+,a3
	bra.s	.x
.mute:	clr.w	8(a2)
	clr.w	$18(a2)
.x:	movem.l	(sp)+,d0-d3/a0-a2
	rts

VibTab:	dc.b	0,1,2,1,0,-1,-2,-1
	even

; AmbFrame: now and then a sound of the forest on channel 3 (birds,
; the wind, a woodpecker, a cuckoo, an owl) - with the music (M)
AmbFrame:
	tst.b	MusicOn
	bne.s	.on
	tst.b	SfxAmb			; music off: the forest stops too
	beq.s	.x
	clr.b	SfxAmb
	clr.l	SfxPtr+4
	clr.w	CUSTOM+$d8
	rts
.on:	tst.b	AmbOn
	beq.s	.x
	subq.w	#1,AmbTimer
	bgt.s	.x
	movem.l	d0-d1/a0-a1,-(sp)
	tst.l	SfxPtr+4
	bne.s	.later
	moveq	#AMBN,d0
	bsr	AmbRand
	lea	AmbList(pc),a0
	moveq	#0,d1
	move.b	(a0,d0.w),d1
	lea	SfxTab,a0
	add.w	d1,d1
	add.w	d1,d1
	move.l	(a0,d1.w),a1
	move.w	(a1)+,d1
	moveq	#3,d0
	bsr	SetWave
	move.l	a1,SfxPtr+4
	move.b	#1,SfxAmb
.later:	move.w	#260,d0
	bsr	AmbRand
	add.w	#70,d0
	move.w	d0,AmbTimer
	movem.l	(sp)+,d0-d1/a0-a1
.x:	rts

; AmbRand: d0 = n -> 0..n-1 (its own numbers: the game's stay the same)
AmbRand:
	movem.l	d1-d2,-(sp)
	move.w	d0,d2
	move.w	AmbSeed,d0
	mulu	#25173,d0
	add.w	#13849,d0
	move.w	d0,AmbSeed
	mulu	d2,d0
	clr.w	d0
	swap	d0
	movem.l	(sp)+,d1-d2
	rts

AmbList:	dc.b	SFX_BIRD1,SFX_BIRD2,SFX_BIRD3,SFX_BIRD4,SFX_BIRD1,SFX_BIRD3
		dc.b	SFX_BIRD2,SFX_BIRD4,SFX_WIND,SFX_WIND,SFX_WOODPECKER,SFX_CUCKOO,SFX_OWL
AMBN		equ	13
	even

; StartTune: a0 = melody, a1 = bass
StartTune:
	movem.l	d0-d1,-(sp)
	move.l	a0,MusPtr
	move.l	a1,MusPtr+4
	move.l	a0,MusStart
	move.l	a1,MusStart+4
	lea	MusState,a0
	moveq	#1,d1
.ch:	move.w	#1,(a0)+		; frames left
	clr.w	(a0)+			; age
	clr.w	(a0)+			; period
	move.w	#24,(a0)+		; volume
	move.w	#3,(a0)+		; decay
	move.w	#6,(a0)+		; lowest volume
	clr.w	(a0)+			; vibrato
	clr.w	(a0)+
	dbf	d1,.ch
	moveq	#0,d0
	moveq	#1,d1
	bsr	SetWave
	moveq	#1,d0
	moveq	#2,d1
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
; the loading picture: the forest, with the title music and the birds
Intro:	lea	IntroPic,a0
	bsr	ShowPic
	lea	TuneTitleMel,a0
	lea	TuneTitleBas,a1
	bsr	StartTune
	move.b	#1,AmbOn
	move.w	#40,AmbTimer
	bsr	FadeIn
	move.w	#350,d0
	bsr	WaitFrames
	bsr	FadeOut
	rts

;---------------------------------------------------------------------
; the title: returns d0 = 0 to play, -1 to quit
Title:	move.b	#1,AmbOn
	lea	TuneTitleMel,a0
	cmp.l	MusStart,a0		; already playing (after the loading picture)?
	beq.s	.page1
	lea	TuneTitleBas,a1
	bsr	StartTune
.page1:	lea	TitlePic,a0
	bsr	ShowPic
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
	moveq	#30,d1
	bsr	RestoreRow
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
	clr.b	AmbOn
	bsr	GamePal
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
	moveq	#30,d1
	if	DEMO
	lea	TxDemoTitle(pc),a0
	moveq	#2,d0
	move.w	#T_FONTG,d2
	bsr	DrawText
	endc
	tst.b	DevMode
	beq.s	.nd
	lea	TxDevMode(pc),a0
	moveq	#30,d0
	move.w	#T_FONTC,d2
	bsr	DrawText
.nd:	rts

HowToPage:
	lea	HowToPic,a0
	bsr	ShowPic
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
TxKeys:		dc.b	'R RETRY  P PAUSE  M MUSIC  ESC QUIT',0
TxDevMode:	dc.b	'DEV MODE',0
		if	DEMO
TxDemoTitle:	dc.b	'DEMO: 3 ROUNDS',0
		endc
	even
; how to play: row, column, font, tile, text
HowTo:	dc.b	1,14,1,0,'HOW TO PLAY',0
	dc.b	3,1,0,0,'THE SNAKE ONLY MOVES WHEN YOU DO: ONE',0
	dc.b	4,1,0,0,'STEP FOR EVERY PUSH OF THE STICK.',0
	dc.b	6,6,2,T_CLOVER,'CLOVER 20 - GROW, A BALL POPS UP',0
	dc.b	8,6,0,T_BALL,'BALL   50 - EAT THEM ALL TOO!',0
	dc.b	10,6,0,T_HEART,'HEART 100 - BONUS MULTIPLIER +1',0
	dc.b	12,6,1,T_BLOCK,'CRATE - PUSH IT WHERE YOU NEED IT',0
	dc.b	14,6,0,T_SPORE2,'EVERY BITE GROWS A MUSHROOM HERE',0
	dc.b	15,6,0,0,'(BLINKING = NEXT). COVER IT WITH',0
	dc.b	16,6,0,0,'YOUR TAIL OR A CRATE TO STOP IT!',0
	dc.b	18,6,0,T_MUSH,'POISON! AS DEADLY AS WALLS & TAIL',0
	dc.b	21,3,3,0,'STUCK? PRESS R OR HOLD FIRE TO',0
	dc.b	22,3,3,0,'RETRY THE ROUND (COSTS A LIFE).',0
	dc.b	24,3,0,0,'BE QUICK: THE BONUS COUNTS DOWN.',0
	dc.b	25,3,0,0,'EXTRA LIFE EVERY 10000 POINTS.',0
	if	DEMO
	dc.b	27,3,2,0,'THIS DEMO HAS 3 OF THE 12 ROUNDS.',0
	else
	dc.b	27,3,2,0,'12 ROUNDS - THEN THEY COME BACK!',0
	endc
	dc.b	29,10,1,0,'PRESS FIRE TO START',0
	dc.b	0
	even

;---------------------------------------------------------------------
; the game
Game:	bsr	GamePal
	move.b	#1,AmbOn
	clr.l	Score
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
.died:	tst.b	Retry
	bne.s	.nr
	bsr	DeathAnim
.nr:	tst.b	DevMode
	bne.s	.again
	subq.w	#1,Lives
	bsr	DrawLives
	tst.w	Lives
	beq.s	.over
.again:	bsr	SetupRound		; the round starts again as it was
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
	; the bonus: 10 points less every 40 frames, quicker every time
	; round 12 is done
	moveq	#40,d3
	mulu	#10,d1
	sub.w	d1,d3
	cmp.w	#20,d3
	bge.s	.sp
	moveq	#20,d3
.sp:	move.w	d3,BonusRate
	bsr	SetupRound
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

; SetupRound: the round from its start (also after losing a life)
SetupRound:
	clr.b	HeartOn
	move.w	#400,HeartTimer
	move.w	#1000,Bonus
	move.w	#1,Mult
	move.w	BonusRate,BonusTimer
	bsr	LoadLevel
	bsr	DrawHud
	bsr	DrawField
	bra	InitSnake

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
	clr.b	JoyHit
	clr.b	FireHit
	clr.b	Dead
	clr.b	Retry
	clr.w	FireHold
	clr.w	RepeatTimer
	move.b	#$ff,LastKey
	rts

TxRound:	dc.b	'ROUND ',0
TxReady:	dc.b	'GET READY!',0
TxClear:	dc.b	'ROUND CLEAR!',0
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
TxRetry:	dc.b	'R / HOLD FIRE = RETRY',0
	even

; LoadLevel: Map, SporeMap, TileMap and Remaining from level LevelIdx
LoadLevel:
	lea	Map,a0
	move.w	#40*32-1,d0
.f:	move.b	#C_WALL,(a0)+
	dbf	d0,.f
	lea	TileMap,a0
	lea	SporeMap,a2
	move.w	#40*32-1,d0
.t:	clr.w	(a0)+
	clr.b	(a2)+
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
	; the spores: where a mushroom grows, in this order, each time
	; something is eaten
	moveq	#0,d0
	move.b	(a1)+,d0
	move.w	d0,SporeN
	clr.w	SporeNext
	lea	SporeList,a2
	lea	SporeMap,a3
	subq.w	#1,d0
	bmi.s	.ns
.sp:	moveq	#0,d1
	move.b	(a1)+,d1
	moveq	#0,d2
	move.b	(a1)+,d2
	add.w	#FIELDY,d2
	mulu	#40,d2
	add.w	d1,d2
	add.w	#FIELDX,d2
	move.w	d2,(a2)+
	move.b	#1,(a3,d2.w)
	dbf	d0,.sp
.ns:	; the tiles of the field and its border
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

; EmptyTile: d0 = an empty cell -> d2 = its tile (the spores show)
EmptyTile:
	move.l	a0,-(sp)
	lea	SporeMap,a0
	moveq	#T_EMPTY,d2
	tst.b	(a0,d0.w)
	beq.s	.x
	move.w	#T_SPORE,d2
.x:	move.l	(sp)+,a0
	rts

; CellTile: d0 = cell -> d2 = its tile (walls by their neighbours)
CellTile:
	movem.l	d0-d1/d3/a0,-(sp)
	lea	Map,a0
	moveq	#0,d1
	move.b	(a0,d0.w),d1
	bne.s	.ne
	bsr	EmptyTile
	bra.s	.x
.ne:	add.w	d1,d1
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
.tab:	dc.w	T_EMPTY,T_WALL0,T_CLOVER,T_BALL,T_MUSH,T_EMPTY,T_BLOCK

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
	lea	TxRetry(pc),a0
	moveq	#2,d1
	move.w	#T_FONTW,d2
	bsr	CenterText
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

DirDelta:	dc.w	-40,1,40,-1

;---------------------------------------------------------------------
; step by step: the snake only moves when the stick is pushed. One
; push = one step; held, it steps on after a short wait.
StepInput:
	move.b	JoyHit,d0
	clr.b	JoyHit
	and.w	#15,d0
	beq.s	.held
	bsr	PickDir
	tst.w	d1
	bmi.s	.x
	move.w	#12,RepeatTimer
	bra	StepTo
.held:	move.b	JoyDir,d0
	and.w	#15,d0
	bne.s	.h
	clr.w	RepeatTimer
.x:	rts
.h:	tst.w	RepeatTimer
	bne.s	.h2
	move.w	#12,RepeatTimer		; held from before: wait first
	rts
.h2:	subq.w	#1,RepeatTimer
	bgt.s	.x
	move.w	#5,RepeatTimer
	bsr	PickDir
	tst.w	d1
	bmi.s	.x
	bra	StepTo

; PickDir: d0 = direction bits -> d1 = a direction (never straight back), or -1
PickDir:
	move.w	Dir,d2
	eor.w	#2,d2
	moveq	#0,d1
.b:	btst	d1,d0
	beq.s	.n
	cmp.w	d2,d1
	bne.s	.x
.n:	addq.w	#1,d1
	cmp.w	#4,d1
	blt.s	.b
	moveq	#-1,d1
.x:	rts

; StepTo: d1 = direction: one step (pushing a crate, eating, dying)
StepTo:	move.w	d1,d0
	add.w	d0,d0
	lea	DirDelta(pc),a1
	move.w	(a1,d0.w),d5		; the step
	moveq	#0,d0
	bsr	SegPos
	add.w	d5,d0
	move.w	d0,d3			; the new head cell
	lea	Map,a0
	cmp.b	#C_BLOCK,(a0,d3.w)
	bne.s	.nblk
	; a crate: push it on if the cell behind it is free
	move.w	d3,d0
	add.w	d5,d0
	tst.b	(a0,d0.w)
	bne	.bump
	tst.b	HeartOn
	beq.s	.ph
	cmp.w	HeartPos,d0
	beq	.bump
.ph:	move.b	#C_BLOCK,(a0,d0.w)
	move.w	#T_BLOCK,d2
	bsr	SetCell
	clr.b	(a0,d3.w)
	moveq	#SFX_PUSH,d0
	bsr	PlaySfx
.nblk:	move.w	d1,Dir
	clr.b	Ate
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
	st	Ate
	moveq	#SFX_CLOVER,d0
	bsr	PlaySfx
	bra.s	.move
.nc:	cmp.b	#C_BALL,d4
	bne.s	.move
	moveq	#50,d0
	bsr	AddScore
	subq.w	#1,Remaining
	st	Ate
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
	bsr	EmptyTile
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
	tst.b	Ate			; every bite grows the next mushroom
	beq.s	.na
	bsr	SporeSprout
.na:	tst.b	SpawnBall
	beq.s	.x
	clr.b	SpawnBall
	bsr	SpawnBallBFS
.x:	rts
.bump:	moveq	#SFX_BUMP,d0
	bra	PlaySfx
.die:	st	Dead
	rts

; SporeSprout: the next spore grows a mushroom - unless something lies
; on it (the snake, a crate, the heart): then it is gone for good
SporeSprout:
	movem.l	d0-d2/a0,-(sp)
	move.w	SporeNext,d1
	cmp.w	SporeN,d1
	bge.s	.x
	addq.w	#1,SporeNext
	add.w	d1,d1
	lea	SporeList,a0
	move.w	(a0,d1.w),d0
	lea	SporeMap,a0
	clr.b	(a0,d0.w)
	lea	Map,a0
	tst.b	(a0,d0.w)
	bne.s	.blocked
	tst.b	HeartOn
	beq.s	.grow
	cmp.w	HeartPos,d0
	beq.s	.hb
.grow:	move.b	#C_MUSH,(a0,d0.w)
	moveq	#T_MUSH,d2
	bsr	SetCell
	moveq	#SFX_SPROUT,d0
	bsr	PlaySfx
	bra.s	.x
.hb:	moveq	#T_EMPTY,d2		; (the heart is drawn over it)
	bsr	SetCell
.blocked:
	moveq	#SFX_FIZZLE,d0
	bsr	PlaySfx
.x:	movem.l	(sp)+,d0-d2/a0
	rts

; SporeBlink: the next spore blinks
SporeBlink:
	move.w	SporeNext,d1
	cmp.w	SporeN,d1
	bge.s	.x
	add.w	d1,d1
	lea	SporeList,a0
	move.w	(a0,d1.w),d0
	lea	Map,a0
	tst.b	(a0,d0.w)
	bne.s	.x
	move.w	#T_SPORE,d2
	btst	#4,FrameCount+3
	beq.s	.d
	move.w	#T_SPORE2,d2
.d:	bra	DrawPos
.x:	rts

; SpawnBallBFS: a ball on a free cell the snake can reach from where it
; is now (flood fill from the head), not on a spore, not right next to
; the head
SpawnBallBFS:
	movem.l	d0-d7/a0-a4,-(sp)
	lea	Visit,a0
	move.w	#40*32/4-1,d0
	moveq	#0,d1
.c:	move.l	d1,(a0)+
	dbf	d0,.c
	lea	Visit,a0
	lea	Map,a1
	lea	BfsQ,a2
	lea	DirDelta(pc),a4
	moveq	#0,d0
	bsr	SegPos
	move.w	d0,d7			; the head
	move.w	d0,(a2)
	st	(a0,d0.w)
	moveq	#0,d5			; read
	moveq	#1,d6			; write
.q:	cmp.w	d6,d5
	bge.s	.done
	move.w	d5,d0
	add.w	d0,d0
	move.w	(a2,d0.w),d1
	addq.w	#1,d5
	moveq	#3,d4
.n:	move.w	d4,d0
	add.w	d0,d0
	move.w	(a4,d0.w),d2
	add.w	d1,d2
	tst.b	(a0,d2.w)
	bne.s	.nn
	move.b	(a1,d2.w),d3
	beq.s	.ok
	cmp.b	#C_CLOVER,d3
	beq.s	.ok
	cmp.b	#C_BALL,d3
	bne.s	.nn
.ok:	st	(a0,d2.w)
	move.w	d6,d0
	add.w	d0,d0
	move.w	d2,(a2,d0.w)
	addq.w	#1,d6
.nn:	dbf	d4,.n
	bra.s	.q
.done:	lea	CandList,a3
	lea	SporeMap,a4
	moveq	#0,d4			; candidates
	moveq	#0,d5
	move.w	d7,d5
	divu	#40,d5			; the head: col:row
	moveq	#1,d0
.cl:	cmp.w	d6,d0
	bge.s	.pick
	move.w	d0,d1
	add.w	d1,d1
	move.w	(a2,d1.w),d1
	tst.b	(a1,d1.w)
	bne.s	.cn
	tst.b	(a4,d1.w)
	bne.s	.cn
	tst.b	HeartOn
	beq.s	.c1
	cmp.w	HeartPos,d1
	beq.s	.cn
.c1:	moveq	#0,d2
	move.w	d1,d2
	divu	#40,d2
	move.w	d2,d3
	sub.w	d5,d3
	bpl.s	.a1
	neg.w	d3
.a1:	swap	d2
	swap	d5
	sub.w	d5,d2
	swap	d5
	tst.w	d2
	bpl.s	.a2
	neg.w	d2
.a2:	add.w	d2,d3
	cmp.w	#3,d3
	blt.s	.cn
	move.w	d1,(a3)+
	addq.w	#1,d4
.cn:	addq.w	#1,d0
	bra.s	.cl
.pick:	tst.w	d4
	beq.s	.x
	move.w	d4,d0
	bsr	RandN
	add.w	d0,d0
	lea	CandList,a3
	move.w	(a3,d0.w),d0
	move.b	#C_BALL,(a1,d0.w)
	moveq	#T_BALL,d2
	bsr	SetCell
	addq.w	#1,Remaining
.x:	movem.l	(sp)+,d0-d7/a0-a4
	rts

; RandomCell: d7 = 1: also the four neighbours must be empty
; -> d0 = an empty cell away from the head and the start, or -1
RandomCell:
	movem.l	d1-d6/a0-a1,-(sp)
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
	lea	SporeMap,a1
	tst.b	(a1,d0.w)
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
.yes:	movem.l	(sp)+,d1-d6/a0-a1
	rts
.no:	dbf	d6,.try
	moveq	#-1,d0
	movem.l	(sp)+,d1-d6/a0-a1
	rts


;---------------------------------------------------------------------
; PlayLoop: -> d0 = 0 round clear, 1 died (Retry set: gave up), 2 quit
PlayLoop:
.l:	bsr	WaitFrame
	move.b	LastKey,d0
	move.b	#$ff,LastKey
	cmp.b	#$45,d0			; Esc
	beq	.quit
	cmp.b	#$13,d0			; R: retry the round
	beq.s	.retry
	cmp.b	#$19,d0			; P
	bne.s	.np
	bsr	Pause
	bra.s	.l
.np:	tst.b	DevMode
	beq.s	.nd
	cmp.b	#$36,d0			; dev: N = next round
	beq.s	.clear
.nd:	tst.b	Fire			; fire held 1.2 s: retry
	beq.s	.nf
	addq.w	#1,FireHold
	cmp.w	#60,FireHold
	bge.s	.retry
	bra.s	.f2
.nf:	clr.w	FireHold
.f2:	bsr	StepInput
	tst.b	Dead
	bne.s	.dead
	tst.w	Remaining
	beq.s	.clear
	bsr	BonusTick
	bsr	SporeBlink
	bsr	HeartTick
	bra.s	.l
.retry:	st	Retry
	moveq	#SFX_FIZZLE,d0
	bsr	PlaySfx
.dead:	moveq	#1,d0
	rts
.clear:	moveq	#0,d0
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
	move.w	BonusRate,BonusTimer
	tst.w	Bonus
	beq.s	.x
	sub.w	#10,Bonus
	bsr	DrawBonus
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
CurPal:		ds.w	32
CurBright:	ds.w	1
CurPlanes:	ds.w	1
CopBpl:		ds.l	1
CurPic:		ds.l	1
TwinkleOn:	ds.b	1
MaskText:	ds.b	1
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
Retry:		ds.b	1
Ate:		ds.b	1
	even
TitleTimer:	ds.w	1
Seed:		ds.w	1
SfxPtr:		ds.l	2
SfxNext:	ds.w	1
AmbTimer:	ds.w	1
AmbSeed:	ds.w	1
AmbOn:		ds.b	1
SfxAmb:		ds.b	1
MusPtr:		ds.l	2
MusStart:	ds.l	2
MusState:	ds.w	16		; per channel: frames left, age, period, volume, decay, lowest, vibrato, -
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
BonusRate:	ds.w	1
RepeatTimer:	ds.w	1
FireHold:	ds.w	1
SporeN:		ds.w	1
SporeNext:	ds.w	1
SporeList:	ds.w	16
Bonus:		ds.w	1
BonusTimer:	ds.w	1
Mult:		ds.w	1
Remaining:	ds.w	1
Dir:		ds.w	1
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
SporeMap:	ds.b	40*32
Visit:		ds.b	40*32
BfsQ:		ds.w	40*32
CandList:	ds.w	40*32

	section	chipvars,bss_c
Screen:		ds.b	PS*5
CopperList:	ds.l	80
