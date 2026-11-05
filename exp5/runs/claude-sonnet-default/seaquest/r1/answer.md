DESIGN

Strategy: a reflex hunter. Reward-channel cells (channel 2) are enemies and divers, so I treat every reward cell as a target.
- If a target is in my own row, I fire and press left or right toward the side it is on. The left press also turns the sub to face it.
- If there is no target in my row, I move up or down toward a row that has one.
- At the surface (row 0) I always dive.
- When oxygen is low and a diver is on board, I go up hard to surface and refill.
- Staying out of row 0 without a diver matters, because surfacing with no diver ends the episode. The network only goes up to row 0 when the surface unit fires or when a target sits above.

Layer 1 (32 units, every unit is a gated AND detector; true is about +0.9, false about -1):
- Units 0-7 (AL_r, rows 1-8): a target in the left half (columns 0-4) of row r AND the player in row r. Target weight 3, player weight 4 on both sub cells, bias -9.5.
- Units 8-15 (AR_r): the same for the right half (columns 5-9).
- Units 16-22 (UP_r, rows 1-7): a target anywhere in row r AND the player in a row below r.
- Units 23-30 (DOWN_r, rows 1-8): a target in row r AND the player in a row above r. The row-0 cells carry a huge weight, so being at the surface always counts as "go down".
- Unit 31 (S): the oxygen gauge's third cell is unlit (oxygen below 60) AND the diver gauge's last cell is lit. At that oxygen level only a diver can light that cell.

Layer 2 (OR gates over the layer 1 groups, saturated to about +-1):
- Unit 0 (Lu) = any of AL.
- Unit 1 (Ru) = any of AR.
- Unit 2 (Own) = any target in my own row.
- Unit 3 (Uu) = any of UP.
- Unit 4 (Dd) = any of DOWN.
- Unit 5 (Su) = S.
- Units 6-31 are unused and stay at 0.

Output logits (each unit is about +-1):
- fire = -1.85 + 1.65*Own - 3*Su
- left = -2.9 + 2.1*Lu - 3*Su
- right = -2.9 + 2.1*Ru - 3*Su
- up = 3 + 1.75*Uu - 1.75*Own + 4.5*Su
- down = -4.5 + 1.75*Dd - 1.75*Own - 3*Su
- no-op = -0.5

With a target in my row, fire gets about 60% and the horizontal move toward it about 30%. With a target in another row, the vertical move toward it gets about 80%. When surfacing is needed, up gets nearly 100%.

```edits
# ---------- layer 1 ----------
# AL_r: target in left half of row r AND player in row r (units 0..7)
W1[62:90:6, 0] = 3
W1[60:120:6, 0] = 4
W1[122:150:6, 1] = 3
W1[120:180:6, 1] = 4
W1[182:210:6, 2] = 3
W1[180:240:6, 2] = 4
W1[242:270:6, 3] = 3
W1[240:300:6, 3] = 4
W1[302:330:6, 4] = 3
W1[300:360:6, 4] = 4
W1[362:390:6, 5] = 3
W1[360:420:6, 5] = 4
W1[422:450:6, 6] = 3
W1[420:480:6, 6] = 4
W1[482:510:6, 7] = 3
W1[480:540:6, 7] = 4
# AR_r: target in right half of row r AND player in row r (units 8..15)
W1[92:120:6, 8] = 3
W1[60:120:6, 8] = 4
W1[152:180:6, 9] = 3
W1[120:180:6, 9] = 4
W1[212:240:6, 10] = 3
W1[180:240:6, 10] = 4
W1[272:300:6, 11] = 3
W1[240:300:6, 11] = 4
W1[332:360:6, 12] = 3
W1[300:360:6, 12] = 4
W1[392:420:6, 13] = 3
W1[360:420:6, 13] = 4
W1[452:480:6, 14] = 3
W1[420:480:6, 14] = 4
W1[512:540:6, 15] = 3
W1[480:540:6, 15] = 4
# UP_r: target in row r AND player below row r (units 16..22)
W1[62:120:6, 16] = 3
W1[120:540:6, 16] = 4
W1[122:180:6, 17] = 3
W1[180:540:6, 17] = 4
W1[182:240:6, 18] = 3
W1[240:540:6, 18] = 4
W1[242:300:6, 19] = 3
W1[300:540:6, 19] = 4
W1[302:360:6, 20] = 3
W1[360:540:6, 20] = 4
W1[362:420:6, 21] = 3
W1[420:540:6, 21] = 4
W1[422:480:6, 22] = 3
W1[480:540:6, 22] = 4
# DOWN_r: target in row r AND player above row r (units 23..30); row 0 alone is enough
W1[62:120:6, 23] = 3
W1[0:60:6, 23] = 4
W1[122:180:6, 24] = 3
W1[0:120:6, 24] = 4
W1[182:240:6, 25] = 3
W1[0:180:6, 25] = 4
W1[242:300:6, 26] = 3
W1[0:240:6, 26] = 4
W1[302:360:6, 27] = 3
W1[0:300:6, 27] = 4
W1[362:420:6, 28] = 3
W1[0:360:6, 28] = 4
W1[422:480:6, 29] = 3
W1[0:420:6, 29] = 4
W1[482:540:6, 30] = 3
W1[0:480:6, 30] = 4
W1[0:60:6, 23] = 10
W1[0:60:6, 24] = 10
W1[0:60:6, 25] = 10
W1[0:60:6, 26] = 10
W1[0:60:6, 27] = 10
W1[0:60:6, 28] = 10
W1[0:60:6, 29] = 10
W1[0:60:6, 30] = 10
b1[0:31] = -9.5
# S: oxygen cell 2 unlit AND last diver-gauge cell lit
W1[593, 31] = 5
W1[557, 31] = -5
b1[31] = -2.5
# ---------- layer 2 ----------
W2[0:8, 0] = 3
b2[0] = 21
W2[8:16, 1] = 3
b2[1] = 21
W2[0:16, 2] = 3
b2[2] = 45
W2[16:23, 3] = 3
b2[3] = 17.4
W2[23:31, 4] = 3
b2[4] = 20.4
W2[31, 5] = 3
# ---------- output ----------
# columns: 0 noop, 1 left, 2 up, 3 right, 4 down, 5 fire
W3[0, 1] = 2.1
W3[1, 3] = 2.1
W3[2, 5] = 1.65
W3[2, 2] = -1.75
W3[2, 4] = -1.75
W3[3, 2] = 1.75
W3[4, 4] = 1.75
W3[5, 2] = 4.5
W3[5, 4] = -3
W3[5, 1] = -3
W3[5, 3] = -3
W3[5, 5] = -3
b3[0] = -0.5
b3[1] = -2.9
b3[2] = 3.0
b3[3] = -2.9
b3[4] = -4.5
b3[5] = -1.85
```
