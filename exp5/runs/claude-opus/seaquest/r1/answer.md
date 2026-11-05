## Design

**Strategy.** The submarine stays in column 8, facing left, with its back cell in column 9. From there every target in its row is to its left, so the shooting rule is just "keep firing". Fire is the default action, and pressing it during the cooldown does nothing. The submarine only moves up and down: toward rows that hold targets (enemies or divers), away from danger, and back to the surface for oxygen. It picks up divers as they pass column 8 in its row.

- **Start.** Stay on the surface (row 0), which is completely safe, and move right to column 9, then press left once. This leaves the front in column 8, facing left. Only then dive.
- **Hunting.** Go to the nearest row with targets, in rows 2 to 8. Rows 1 and 0 are never chased, because a repeated "up" from a sticky action could surface the submarine with no diver on board, which ends the episode.
- **Dodging.** Leave the row when a threat is in column 9 (behind us), any danger is in column 7, or a bullet is in column 6. Never move into a row that has danger in columns 7 to 9.
- **Oxygen.** When oxygen drops below 60 (gauge cell 2 off), climb. Surface only if gauge cell 8 is on. At that oxygen level, cell 8 on means at least one diver is aboard, including the case of 6 divers.

**Layer 1: rows gated by where the submarine is.** A unit can be switched on for one submarine row only. Each of the submarine's two cells in row s gets weight 12, and the bias includes -24, so the unit is near -1 unless the submarine is in row s. Inside that gate the unit computes an ordinary linear score for that row. This lets rules like "danger in my row" or "target above me" be written with fixed absolute weights.

- **Units 0-7: "go up" from row s = 1..8.**
  - Rows 3-8 score as follows:
    - bias -0.5
    - targets above me: +1.6, +1.3, +1.0 or +0.8 for a target 1, 2, 3, or 4 or more rows away
    - +3.5 when oxygen is below 60
    - danger in my row: +4 in column 7 or 9, +2.5 for a bullet in column 6
    - an enemy (-2.0) or diver (-0.8) in my row's columns 0-5 holds me in place
    - danger in the row above, columns 7-9: -8
  - Row 2 to row 1 and row 1 to the surface are on only when oxygen is below 60 and gauge cell 8 is on.
- **Unit 8: dive from the surface.** On only when the submarine is in position (back cell in column 9) and row 1, columns 7-9, is clear.
- **Units 9-15: "go down" from rows 1-7.** The same kind of score, using targets below. Row 1 always tends to go down. All of these are suppressed when oxygen is below 60.
- **Unit 16: "move right".** On when the submarine does not occupy column 9.
- **Unit 17: "turn left".** On when the front is in column 9, meaning the submarine faces right.

**Layer 2.** Unit 0 sums units 0-7 into an up score, and unit 1 sums units 8-15 into a down score. Only one row's unit is ever on, and the mapping keeps it close to linear, so how strongly a move is wanted is preserved. Units 2 and 3 pass "move right" and "turn left" through.

**Output logits.**
| Action | Logit |
|---|---|
| Fire | constant 2 |
| No-op | -6 |
| Up | 1.2 + 20 × up score (about -8 when off, up to 10.4 when on) |
| Down | 1.2 + 20 × down score (about -8 when off, up to 10.4 when on) |
| Right | -1.5 + 8.5 × layer-2 unit 2 (about 5 when on, -8 when off) |
| Left | -1.5 + 8.5 × layer-2 unit 3 (about 5 when on, -8 when off) |

```edits
# ===== Layer 1 =====
# U_1 (unit 0): row 1 -> surface, only if oxygen<60 (g2 off) and divers>=1 (g8 on)
W1[60:120:6, 0] = 12
W1[593, 0] = 7
W1[557, 0] = -7
b1[0] = -28
# U_2 (unit 1): row 2 -> row 1, surface mode only
W1[120:180:6, 1] = 12
W1[593, 1] = 7
W1[557, 1] = -7
W1[103:116:6, 1] = -8
b1[1] = -28
# U_3 (unit 2)
W1[180:240:6, 2] = 12
b1[2] = -21
W1[557, 2] = -3.5
W1[122:180:6, 2] = 1.6
W1[181:212:6, 2] = -1.2
W1[182:213:6, 2] = -0.8
W1[217, 2] = 2.5
W1[218, 2] = -2.5
W1[223, 2] = 4
W1[235, 2] = 4
W1[163:176:6, 2] = -8
# U_4 (unit 3)
W1[240:300:6, 3] = 12
b1[3] = -21
W1[557, 3] = -3.5
W1[182:240:6, 3] = 1.6
W1[122:180:6, 3] = 1.3
W1[241:272:6, 3] = -1.2
W1[242:273:6, 3] = -0.8
W1[277, 3] = 2.5
W1[278, 3] = -2.5
W1[283, 3] = 4
W1[295, 3] = 4
W1[223:236:6, 3] = -8
# U_5 (unit 4)
W1[300:360:6, 4] = 12
b1[4] = -21
W1[557, 4] = -3.5
W1[242:300:6, 4] = 1.6
W1[182:240:6, 4] = 1.3
W1[122:180:6, 4] = 1.0
W1[301:332:6, 4] = -1.2
W1[302:333:6, 4] = -0.8
W1[337, 4] = 2.5
W1[338, 4] = -2.5
W1[343, 4] = 4
W1[355, 4] = 4
W1[283:296:6, 4] = -8
# U_6 (unit 5)
W1[360:420:6, 5] = 12
b1[5] = -21
W1[557, 5] = -3.5
W1[302:360:6, 5] = 1.6
W1[242:300:6, 5] = 1.3
W1[182:240:6, 5] = 1.0
W1[122:180:6, 5] = 0.8
W1[361:392:6, 5] = -1.2
W1[362:393:6, 5] = -0.8
W1[397, 5] = 2.5
W1[398, 5] = -2.5
W1[403, 5] = 4
W1[415, 5] = 4
W1[343:356:6, 5] = -8
# U_7 (unit 6)
W1[420:480:6, 6] = 12
b1[6] = -21
W1[557, 6] = -3.5
W1[362:420:6, 6] = 1.6
W1[302:360:6, 6] = 1.3
W1[242:300:6, 6] = 1.0
W1[122:240:6, 6] = 0.8
W1[421:452:6, 6] = -1.2
W1[422:453:6, 6] = -0.8
W1[457, 6] = 2.5
W1[458, 6] = -2.5
W1[463, 6] = 4
W1[475, 6] = 4
W1[403:416:6, 6] = -8
# U_8 (unit 7)
W1[480:540:6, 7] = 12
b1[7] = -21
W1[557, 7] = -3.5
W1[422:480:6, 7] = 1.6
W1[362:420:6, 7] = 1.3
W1[302:360:6, 7] = 1.0
W1[122:300:6, 7] = 0.8
W1[481:512:6, 7] = -1.2
W1[482:513:6, 7] = -0.8
W1[517, 7] = 2.5
W1[518, 7] = -2.5
W1[523, 7] = 4
W1[535, 7] = 4
W1[463:476:6, 7] = -8
# D_0 (unit 8): dive from surface when in position (back cell at col 9) and row 1 cols 7-9 clear
W1[0:60:6, 8] = 2
W1[58, 8] = 4
W1[103:116:6, 8] = -8
b1[8] = -6
# D_1 (unit 9)
W1[60:120:6, 9] = 12
b1[9] = -25.5
W1[557, 9] = 3.5
W1[97, 9] = 2.5
W1[98, 9] = -2.5
W1[103, 9] = 4
W1[115, 9] = 4
W1[163:176:6, 9] = -8
# D_2 (unit 10)
W1[120:180:6, 10] = 12
b1[10] = -28
W1[557, 10] = 3.5
W1[182:240:6, 10] = 1.6
W1[242:300:6, 10] = 1.3
W1[302:360:6, 10] = 1.0
W1[362:540:6, 10] = 0.8
W1[121:152:6, 10] = -1.2
W1[122:153:6, 10] = -0.8
W1[157, 10] = 2.5
W1[158, 10] = -2.5
W1[163, 10] = 4
W1[175, 10] = 4
W1[223:236:6, 10] = -8
# D_3 (unit 11)
W1[180:240:6, 11] = 12
b1[11] = -28
W1[557, 11] = 3.5
W1[242:300:6, 11] = 1.6
W1[302:360:6, 11] = 1.3
W1[362:420:6, 11] = 1.0
W1[422:540:6, 11] = 0.8
W1[181:212:6, 11] = -1.2
W1[182:213:6, 11] = -0.8
W1[217, 11] = 2.5
W1[218, 11] = -2.5
W1[223, 11] = 4
W1[235, 11] = 4
W1[283:296:6, 11] = -8
# D_4 (unit 12)
W1[240:300:6, 12] = 12
b1[12] = -28
W1[557, 12] = 3.5
W1[302:360:6, 12] = 1.6
W1[362:420:6, 12] = 1.3
W1[422:480:6, 12] = 1.0
W1[482:540:6, 12] = 0.8
W1[241:272:6, 12] = -1.2
W1[242:273:6, 12] = -0.8
W1[277, 12] = 2.5
W1[278, 12] = -2.5
W1[283, 12] = 4
W1[295, 12] = 4
W1[343:356:6, 12] = -8
# D_5 (unit 13)
W1[300:360:6, 13] = 12
b1[13] = -28
W1[557, 13] = 3.5
W1[362:420:6, 13] = 1.6
W1[422:480:6, 13] = 1.3
W1[482:540:6, 13] = 1.0
W1[301:332:6, 13] = -1.2
W1[302:333:6, 13] = -0.8
W1[337, 13] = 2.5
W1[338, 13] = -2.5
W1[343, 13] = 4
W1[355, 13] = 4
W1[403:416:6, 13] = -8
# D_6 (unit 14)
W1[360:420:6, 14] = 12
b1[14] = -28
W1[557, 14] = 3.5
W1[422:480:6, 14] = 1.6
W1[482:540:6, 14] = 1.3
W1[361:392:6, 14] = -1.2
W1[362:393:6, 14] = -0.8
W1[397, 14] = 2.5
W1[398, 14] = -2.5
W1[403, 14] = 4
W1[415, 14] = 4
W1[463:476:6, 14] = -8
# D_7 (unit 15)
W1[420:480:6, 15] = 12
b1[15] = -28
W1[557, 15] = 3.5
W1[482:540:6, 15] = 1.6
W1[421:452:6, 15] = -1.2
W1[422:453:6, 15] = -0.8
W1[457, 15] = 2.5
W1[458, 15] = -2.5
W1[463, 15] = 4
W1[475, 15] = 4
W1[523:536:6, 15] = -8
# C_R (unit 16): sub does not occupy column 9 -> move right
W1[54:600:60, 16] = -6
b1[16] = 3
# C_L (unit 17): front at column 9 (facing right) -> press left
W1[54:600:60, 17] = 6
W1[58:600:60, 17] = -6
b1[17] = -3
# ===== Layer 2 =====
W2[0:8, 0] = 0.5
W2[8:16, 1] = 0.5
b2[0:2] = 3.5
W2[16, 2] = 1
W2[17, 3] = 1
# ===== Output =====
W3[0, 2] = 20
W3[1, 4] = 20
W3[2, 3] = 8.5
W3[3, 1] = 8.5
b3[0:6] = [-6, -1.5, 1.2, -1.5, 1.2, 2]
```
