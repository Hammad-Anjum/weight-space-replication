DESIGN

Strategy: a fixed-column turret. The submarine starts at column 5 facing left and the network never presses left or right, so the column and the facing never change. This removes the need to read the facing from the input. The network only decides vertical movement (up, down) versus firing. Bullets always go left from column 5, so every enemy on the left half of a row can be shot. Divers drift through column 5, so the submarine waits in a diver's row to be run into.

Layer 1 (32 units, tanh, nearly binary):
- Units 0-6 (T2..T8) score rows 2..8. A row's pre-activation is a weighted sum of its channel 1 and channel 2 cells, so the channels separate the three cell types: an enemy in columns 0-3 is +1.5, a diver anywhere is +3.75, an enemy bullet in columns 0-3 is -2.25, and an enemy or bullet in columns 4-9 is strongly negative (-4.5 or -8.25). The row therefore reads as attractive (a target to shoot or a diver to meet) or repulsive (danger from the right, or a bullet in flight).
- Units 7-14 (Q1..Q8) are "player row >= k", read linearly from the two cells of channel 0.
- Unit 15 reads "diver on board" (bottom row, column 8, gauge channel). Unit 16 reads "oxygen >= 60" (bottom row, column 2, gauge channel).

Layer 2 (conjunctions of one row score with the player's row):
- Units 0-5: an attractive row k is above the player, so the unit votes up.
- Units 6-12: an attractive row k is below the player, so the unit votes down.
- Units 13-19: the player's own row is repulsive, so the unit dodges. The dodge direction is biased toward the room available: down near the top, up near the bottom.
- Units 20-26: the player's own row is attractive, so the unit stays put and fires. It suppresses up and down.
- Unit 27: a diver is on board and oxygen is low, so the unit gives a strong ascend that overrides everything else and stops firing. Surfacing refills the oxygen.
- Unit 28: the player is at row 0 or 1, so the unit pushes down. This also means the submarine never lingers at the top row without a diver, which would end the episode.

Output: left and right are about -30, so they are never chosen. Fire is the default (+10). Up and down move at +16 when a target needs them. b3 is set to cancel the off-state (-1) contributions of the layer 2 units.

```edits
W1[121:180:6, 0] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[122:180:6, 0] = 3.75
W1[181:240:6, 1] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[182:240:6, 1] = 3.75
W1[241:300:6, 2] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[242:300:6, 2] = 3.75
W1[301:360:6, 3] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[302:360:6, 3] = 3.75
W1[361:420:6, 4] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[362:420:6, 4] = 3.75
W1[421:480:6, 5] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[422:480:6, 5] = 3.75
W1[481:540:6, 6] = [-2.25, -2.25, -2.25, -2.25, -8.25, -8.25, -8.25, -8.25, -8.25, -8.25]
W1[482:540:6, 6] = 3.75
W1[60:540:6, 7] = 4
W1[120:540:6, 8] = 4
W1[180:540:6, 9] = 4
W1[240:540:6, 10] = 4
W1[300:540:6, 11] = 4
W1[360:540:6, 12] = 4
W1[420:540:6, 13] = 4
W1[480:540:6, 14] = 4
b1[7:15] = -4
W1[593, 15] = 8
b1[15] = -4
W1[557, 16] = 8
b1[16] = -4
b2[0:13] = -15
b2[13:27] = -19
b2[27] = -15
b2[28] = 0
W2[0, 0] = 10
W2[9, 0] = 10
W2[1, 1] = 10
W2[10, 1] = 10
W2[2, 2] = 10
W2[11, 2] = 10
W2[3, 3] = 10
W2[12, 3] = 10
W2[4, 4] = 10
W2[13, 4] = 10
W2[5, 5] = 10
W2[14, 5] = 10
W2[0, 6] = 10
W2[8, 6] = -10
W2[1, 7] = 10
W2[9, 7] = -10
W2[2, 8] = 10
W2[10, 8] = -10
W2[3, 9] = 10
W2[11, 9] = -10
W2[4, 10] = 10
W2[12, 10] = -10
W2[5, 11] = 10
W2[13, 11] = -10
W2[6, 12] = 10
W2[14, 12] = -10
W2[0, 13] = -10
W2[8, 13] = 8
W2[9, 13] = -8
W2[1, 14] = -10
W2[9, 14] = 8
W2[10, 14] = -8
W2[2, 15] = -10
W2[10, 15] = 8
W2[11, 15] = -8
W2[3, 16] = -10
W2[11, 16] = 8
W2[12, 16] = -8
W2[4, 17] = -10
W2[12, 17] = 8
W2[13, 17] = -8
W2[5, 18] = -10
W2[13, 18] = 8
W2[14, 18] = -8
W2[6, 19] = -10
W2[14, 19] = 16
W2[0, 20] = 10
W2[8, 20] = 8
W2[9, 20] = -8
W2[1, 21] = 10
W2[9, 21] = 8
W2[10, 21] = -8
W2[2, 22] = 10
W2[10, 22] = 8
W2[11, 22] = -8
W2[3, 23] = 10
W2[11, 23] = 8
W2[12, 23] = -8
W2[4, 24] = 10
W2[12, 24] = 8
W2[13, 24] = -8
W2[5, 25] = 10
W2[13, 25] = 8
W2[14, 25] = -8
W2[6, 26] = 10
W2[14, 26] = 16
W2[15, 27] = 10
W2[16, 27] = -10
W2[8, 28] = -10
W3[0:6, 2] = 8
W3[6:13, 4] = 8
W3[13:20, 2] = [0, 4, 6, 8, 10, 10, 10]
W3[13:20, 4] = [10, 10, 10, 8, 6, 0, 0]
W3[13:20, 5] = -10
W3[20:27, 2] = -50
W3[20:27, 4] = -50
W3[27, 2] = 100
W3[27, 4] = -50
W3[27, 5] = -15
W3[28, 4] = 10
b3[0] = 0
b3[1] = -30
b3[2] = -154
b3[3] = -30
b3[4] = -290
b3[5] = -75
```
