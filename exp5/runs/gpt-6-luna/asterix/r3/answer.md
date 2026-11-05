The network treats each occupied row as a coarse threat signal: it favors moving away from an enemy in the player’s row and avoids stepping into rows with enemies. It also rewards horizontal movement when treasure shares the player’s row, nudges toward treasure on the opposite side of the board, and discourages moving beyond the left or right edge. Hidden units detect row occupancy, player/enemy row combinations, coarse treasure direction, and edge positions.

```edits
# First-layer row detectors: player, enemy, and treasure, for rows 1 through 8.
W1[60:120:6, 0] = 3.0
W1[120:180:6, 1] = 3.0
W1[180:240:6, 2] = 3.0
W1[240:300:6, 3] = 3.0
W1[300:360:6, 4] = 3.0
W1[360:420:6, 5] = 3.0
W1[420:480:6, 6] = 3.0
W1[480:540:6, 7] = 3.0

W1[61:120:6, 8] = 3.0
W1[121:180:6, 9] = 3.0
W1[181:240:6, 10] = 3.0
W1[241:300:6, 11] = 3.0
W1[301:360:6, 12] = 3.0
W1[361:420:6, 13] = 3.0
W1[421:480:6, 14] = 3.0
W1[481:540:6, 15] = 3.0

W1[62:120:6, 16] = 3.0
W1[122:180:6, 17] = 3.0
W1[182:240:6, 18] = 3.0
W1[242:300:6, 19] = 3.0
W1[302:360:6, 20] = 3.0
W1[362:420:6, 21] = 3.0
W1[422:480:6, 22] = 3.0
W1[482:540:6, 23] = 3.0

# Exact edge and coarse horizontal-half detectors.
W1[0:600:60, 24] = 3.0
W1[54:600:60, 25] = 3.0
W1[0:600:60, 26] = 3.0
W1[6:600:60, 26] = 3.0
W1[12:600:60, 26] = 3.0
W1[18:600:60, 26] = 3.0
W1[24:600:60, 26] = 3.0
W1[30:600:60, 27] = 3.0
W1[36:600:60, 27] = 3.0
W1[42:600:60, 27] = 3.0
W1[48:600:60, 27] = 3.0
W1[54:600:60, 27] = 3.0
W1[2:600:60, 28] = 3.0
W1[8:600:60, 28] = 3.0
W1[14:600:60, 28] = 3.0
W1[20:600:60, 28] = 3.0
W1[26:600:60, 28] = 3.0
W1[32:600:60, 29] = 3.0
W1[38:600:60, 29] = 3.0
W1[44:600:60, 29] = 3.0
W1[50:600:60, 29] = 3.0
W1[56:600:60, 29] = 3.0
b1[0:30] = -1.5

# Second-layer conjunctions: same-row danger.
W2[0, 0] = 2.0
W2[8, 0] = 2.0
W2[1, 1] = 2.0
W2[9, 1] = 2.0
W2[2, 2] = 2.0
W2[10, 2] = 2.0
W2[3, 3] = 2.0
W2[11, 3] = 2.0
W2[4, 4] = 2.0
W2[12, 4] = 2.0
W2[5, 5] = 2.0
W2[13, 5] = 2.0
W2[6, 6] = 2.0
W2[14, 6] = 2.0
W2[7, 7] = 2.0
W2[15, 7] = 2.0

# Enemy in the row reached by moving up.
W2[1, 8] = 2.0
W2[8, 8] = 2.0
W2[2, 9] = 2.0
W2[9, 9] = 2.0
W2[3, 10] = 2.0
W2[10, 10] = 2.0
W2[4, 11] = 2.0
W2[11, 11] = 2.0
W2[5, 12] = 2.0
W2[12, 12] = 2.0
W2[6, 13] = 2.0
W2[13, 13] = 2.0
W2[7, 14] = 2.0
W2[14, 14] = 2.0

# Enemy in the row reached by moving down.
W2[0, 15] = 2.0
W2[9, 15] = 2.0
W2[1, 16] = 2.0
W2[10, 16] = 2.0
W2[2, 17] = 2.0
W2[11, 17] = 2.0
W2[3, 18] = 2.0
W2[12, 18] = 2.0
W2[4, 19] = 2.0
W2[13, 19] = 2.0
W2[5, 20] = 2.0
W2[14, 20] = 2.0
W2[6, 21] = 2.0
W2[15, 21] = 2.0

# Treasure sharing the player's row, for rows 2 through 7.
W2[1, 22] = 2.0
W2[17, 22] = 2.0
W2[2, 23] = 2.0
W2[18, 23] = 2.0
W2[3, 24] = 2.0
W2[19, 24] = 2.0
W2[4, 25] = 2.0
W2[20, 25] = 2.0
W2[5, 26] = 2.0
W2[21, 26] = 2.0
W2[6, 27] = 2.0
W2[22, 27] = 2.0

# Coarse treasure direction and edge indicators.
W2[26, 28] = 2.0
W2[29, 28] = 2.0
W2[27, 29] = 2.0
W2[28, 29] = 2.0
W2[24, 30] = 2.0
W2[25, 31] = 2.0
b2[0:30] = -2.6

# Convert hidden features into action preferences.
W3[0:8, 2] = 3.0
W3[0:8, 4] = 3.0
W3[8:15, 2] = -1.5
W3[15:22, 4] = -1.5
W3[22:28, 1] = 1.5
W3[22:28, 3] = 1.5
W3[28, 3] = 3.0
W3[29, 1] = 3.0
W3[30, 1] = -4.0
W3[31, 3] = -4.0
b3[0] = -3.0
b3[1] = 8.2
b3[2] = 13.5
b3[3] = 8.2
b3[4] = 13.5
b3[5] = -3.0
```