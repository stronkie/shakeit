# Stronkie's Clover Snake (Amiga 500)

Created By Mark Stronks, Stronkie Soft (c) 2026.

An Amiga 500 arcade puzzle game inspired by the 1986 MSX game Snake It: eat every
clover (the snake grows and a white ball pops up somewhere on the field), eat every
ball too, keep away from the poison mushrooms, the walls and your own tail, and catch
the drifting hearts for a bigger bonus multiplier. When the bonus runs out, new
mushrooms start to sprout.

**Target:** Amiga 500, 68000 only, Kickstart 3.1 / Workbench 3.1, 1 MB chip RAM
(runs in 512K too). No interrupts, no blitter: beam, keyboard and joystick are polled.

## Files
| File | What |
|---|---|
| `StronkiesCloverSnake_V0.4.adf` | the game disk (packed, boots; Install on it puts the game on a hard disk) |
| `StronkiesCloverSnake_Demo.adf` | free demo: rounds 1-3 |
| `StronkiesCloverSnake_V0.4_harddrive.zip` | drawer for a hard drive / CF card |
| `StronkiesCloverSnake_V0.4_WHDLoad.zip` / `.lha` | WHDLoad version (own slave, no Kickstart image; F10 quits) |

## Controls
Joystick port 2 or cursor keys - Fire/Space/Return start - P pause - M music on/off -
Esc back to the title (on the title: quit).
Developer mode: **Ctrl + Alt + D** on the title ("DEV" on screen): no lives lost,
**N** = next round, the hi-score is not kept.

## Rules
- **Step by step**: the snake only moves when the stick is pushed (one push = one step,
  held = a step every 5 frames after 12). Straight back is ignored.
- Clover 20 points, the snake grows 2, a ball appears on a free cell the snake can reach
  (flood fill from the head). Ball 50 points, no growth.
- **Spores** (per round a list of up to 15 cells, many in narrow places): every bite (clover
  or ball) grows a mushroom on the next spore in the list (it blinks). If the snake, a crate
  or the heart lies on it at that moment, nothing grows and the spore is gone.
- **Crates**: walking into a crate pushes it one cell if the cell behind it is empty;
  otherwise the snake just doesn't move (bump).
- Heart 100 points + bonus multiplier (max x9). It drifts diagonally and bounces.
- Bonus starts at 1000 and drops 10 every 40 frames (quicker after round 12).
- Walls, mushrooms and the tail kill. Losing a life restarts the round as it was;
  **R or holding fire 1.2 s** = retry (costs a life). Extra life every 10000.

## Print kit
In `print/`: `StronkiesCloverSnake_Manual.pdf` (12-page A5 booklet), `StronkiesCloverSnake_Box.pdf`
(fold-up big box: A3 full size, A4 mini, flat faces) and `StronkiesCloverSnake_DiskLabels.pdf` (A4).
Made by `tools/print/` (export_art.py, then make_manual.py / make_box.py / make_labels.py, using the
toolkit's print helpers and the game's own font and tiles; screenshots in `screenshots/print/`).

## Building
```sh
. /path/to/amiga-toolkit/setup.sh
VER=0.1 tools/build.sh        # gen.py (gfx, rounds, sound) + assemble + ADFs + zips + WHDLoad
```
- `tools/paint.py` paints the loading, title and how-to-play pictures (4x size, reduced to
  Amiga colours); `tools/gen.py` makes `src/gfx_gen.s`: palette, tiles, font, the pictures,
  the 12 rounds (checked: every cell reachable), waveforms, sound effects, music.
  Previews go to `art/`.
- `src/main.s` the game, `src/install.s` the hard disk installer,
  `src/whdload.s` the WHDLoad slave, `tools/icons.py` the Workbench 3.1 icons.

## itch.io
Page live since 27-11-2026, status **In development**, no payments: only the free demo
(V0.3, rounds 1-3) + a devlog. **Full release planned for the "Stronkie Soft Update Sunday" of
29-11-2026** (Mark, 27-11-2026): 2.00 EUR, Released, the newest version (disk image ADF, hard drive zip,
WHDLoad) + the free demo + the print kit.

## Changelog
### Not yet on itch
- **V0.4** (27-11-2026) New look and sound (Mark: the menu was mostly text, no real loading
  screen, the music irritating): painted loading picture (forest, the snake, fly agarics, clover,
  ball, heart), painted title + how-to-play page (32 colours, 5 bitplanes, colours 0-15 = the
  game's, fireflies twinkle on colours 29-31), the menu inside a fence of the game's walls,
  text drawn see-through. Music: Grieg's Morning Mood (title, flute/oboe + harp) and Bach's
  Minuet in G (game, AABB, soft); new engine with instruments, envelopes and vibrato. Forest
  sounds on channel 3 (birds, wind, woodpecker, cuckoo, owl), they give way to game effects;
  M turns music + forest off.
- **V0.3** (27-11-2026) Fix: the M key now really turns the music off/on (the toggle
  flipped 1 to $FE, which still meant "on").
- **V0.2** (27-11-2026) Plays like the MSX original: step-by-step movement, pushable
  crates, mushrooms growing on spores each time you eat (block them with the tail),
  retry key (R / hold fire), the round restarts after losing a life, balls only where
  reachable. New rounds with crates and spores.
- **V0.1** (27-11-2026) First version: 12 rounds, clovers + balls, poison mushrooms,
  drifting hearts with the bonus multiplier, sprouting mushrooms, title + how-to-play
  pages, music and effects, 3-round demo, hard disk installer, WHDLoad. Print kit
  (manual / box / labels) follows before the Final Release.
