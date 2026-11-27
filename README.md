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
| `StronkiesCloverSnake_V0.1.adf` | the game disk (packed, boots; Install on it puts the game on a hard disk) |
| `StronkiesCloverSnake_Demo.adf` | free demo: rounds 1-3 |
| `StronkiesCloverSnake_V0.1_harddrive.zip` | drawer for a hard drive / CF card |
| `StronkiesCloverSnake_V0.1_WHDLoad.zip` / `.lha` | WHDLoad version (own slave, no Kickstart image; F10 quits) |

## Controls
Joystick port 2 or cursor keys - Fire/Space/Return start - P pause - M music on/off -
Esc back to the title (on the title: quit).
Developer mode: **Ctrl + Alt + D** on the title ("DEV" on screen): no lives lost,
**N** = next round, the hi-score is not kept.

## Rules
- Clover 20 points, the snake grows 2, a ball appears. Ball 50 points.
- Heart 100 points + bonus multiplier (max x9). It drifts diagonally and bounces.
- Bonus starts at 1000 and drops 10 every 0.6 s; what is left x multiplier is added
  at the end of the round. At 0, a mushroom sprouts every 5 seconds.
- Extra life every 10000. 12 rounds, then they loop faster (speed 8 -> 3 frames a step).

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

## Changelog
### Not yet on itch
- **V0.1** (27-11-2026) First version: 12 rounds, clovers + balls, poison mushrooms,
  drifting hearts with the bonus multiplier, sprouting mushrooms, title + how-to-play
  pages, music and effects, 3-round demo, hard disk installer, WHDLoad. Print kit
  (manual / box / labels) follows before the Final Release.
