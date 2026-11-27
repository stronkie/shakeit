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
| `StronkiesCloverSnake_V0.3.adf` | the game disk (packed, boots; Install on it puts the game on a hard disk) |
| `StronkiesCloverSnake_Demo.adf` | free demo: rounds 1-3 |
| `StronkiesCloverSnake_V0.3_harddrive.zip` | drawer for a hard drive / CF card |
| `StronkiesCloverSnake_V0.3_WHDLoad.zip` / `.lha` | WHDLoad version (own slave, no Kickstart image; F10 quits) |

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

## Building
```sh
. /path/to/amiga-toolkit/setup.sh
VER=0.1 tools/build.sh        # gen.py (gfx, rounds, sound) + assemble + ADFs + zips + WHDLoad
```
- `tools/gen.py` makes `src/gfx_gen.s`: palette, tiles, font, intro/title pictures,
  the 12 rounds (checked: every cell reachable), waveforms, sound effects, music.
  Previews go to `art/`.
- `src/main.s` the game, `src/install.s` the hard disk installer,
  `src/whdload.s` the WHDLoad slave, `tools/icons.py` the Workbench 3.1 icons.

## itch.io
Page live since 27-11-2026, status **In development**, no payments: only the free demo
(V0.3, rounds 1-3) + a devlog. The full game is not on itch yet.

## Changelog
### Not yet on itch
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
