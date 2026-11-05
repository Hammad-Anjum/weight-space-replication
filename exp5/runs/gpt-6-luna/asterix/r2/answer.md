The policy treats each playable row as a lane. First-layer units detect the player, enemies, and treasure by row, plus the player’s horizontal position. Second-layer units gate enemy and treasure signals by the player’s row. A detected enemy triggers a vertical dodge toward the center; treasure discourages leaving its lane. Otherwise, the policy stays mostly still and steers back toward column 5.

```edits
# First layer: player, enemy, and treasure presence by playable row.
W1[60:120:6, 0] = 2
W1[120:180:6, 1] = 2
W1[180:240:6, 2] = 2
W1[240:300:6, 3] = 2
W1[300:360:6, 4] = 2
W1[360:420:6, 5] = 2
W1[420:480:6, 6] = 2
W1[480:540:6, 7] = 2
W1[61:120:6, 8] = 2
W1[121:180:6, 9] = 2
W1[181:240:6, 10] = 2
W1[241:300:6, 11] = 2
W1[301:360:6, 12] = 2
W1[361:420:6, 13] = 2
W1[421:480:6, 14] = 2
W1[481:540:6, 15] = 2
W1[62:120:6, 16] = 2
W1[122:180:6, 17] = 2
W1[182:240:6, 18] = 2
W1[242:300:6, 19] = 2
W1[302:360:6, 20] = 2
W1[362:420:6, 21] = 2
W1[422:480:6, 22] = 2
W1[482:540:6, 23] = 2
b1[0:24] = -1

# Signed player-column feature, centered at column 5.
W1[0:600:60, 24] = -1.25
W1[6:600:60, 24] = -1.0
W1[12:600:60, 24] = -0.75
W1[18:600:60, 24] = -0.5
W1[24:600:60, 24] = -0.25
W1[30:600:60, 24] = 0
W1[36:600:60, 24] = 0.25
W1[42:600:60, 24] = 0.5
W1[48:600:60, 24] = 0.75
W1[54:600:60, 24] = 1.0

# Second layer: lane-specific enemy and treasure detectors.
W2[0, 0] = 3.5
W2[8, 0] = 1.2
W2[1, 1] = 3.5
W2[9, 1] = 1.2
W2[2, 2] = 3.5
W2[10, 2] = 1.2
W2[3, 3] = 3.5
W2[11, 3] = 1.2
W2[4, 4] = 3.5
W2[12, 4] = 1.2
W2[5, 5] = 3.5
W2[13, 5] = 1.2
W2[6, 6] = 3.5
W2[14, 6] = 1.2
W2[7, 7] = 3.5
W2[15, 7] = 1.2

W2[0, 8] = 3.5
W2[16, 8] = 1.2
W2[1, 9] = 3.5
W2[17, 9] = 1.2
W2[2, 10] = 3.5
W2[18, 10] = 1.2
W2[3, 11] = 3.5
W2[19, 11] = 1.2
W2[4, 12] = 3.5
W2[20, 12] = 1.2
W2[5, 13] = 3.5
W2[21, 13] = 1.2
W2[6, 14] = 3.5
W2[22, 14] = 1.2
W2[7, 15] = 3.5
W2[23, 15] = 1.2

# Pass player-row indicators for cancelling lane-independent offsets.
W2[0, 16] = 2
W2[1, 17] = 2
W2[2, 18] = 2
W2[3, 19] = 2
W2[4, 20] = 2
W2[5, 21] = 2
W2[6, 22] = 2
W2[7, 23] = 2

# Pass the horizontal-position feature.
W2[24, 24] = 2
b2[0:16] = -1.5

# Threat escape: rows 1–4 down, rows 5–8 up.
W3[0, 4] = 7
W3[1, 4] = 7
W3[2, 4] = 7
W3[3, 4] = 7
W3[4, 2] = 7
W3[5, 2] = 7
W3[6, 2] = 7
W3[7, 2] = 7

# Treasure in the player's lane discourages vertical movement.
W3[8:16, 2] = -1.5
W3[8:16, 4] = -1.5

# Row-feature offsets to keep the default vertical preference neutral.
W3[16, 2] = 1.029
W3[17, 2] = 1.029
W3[18, 2] = 1.029
W3[19, 2] = 1.029
W3[20, 2] = -3.773
W3[21, 2] = -3.773
W3[22, 2] = -3.773
W3[23, 2] = -3.773
W3[16, 4] = -3.773
W3[17, 4] = -3.773
W3[18, 4] = -3.773
W3[19, 4] = -3.773
W3[20, 4] = 1.029
W3[21, 4] = 1.029
W3[22, 4] = 1.029
W3[23, 4] = 1.029

# Steer toward column 5; favor stationary actions otherwise.
W3[24, 1] = 3.5
W3[24, 3] = -3.5
b3[0] = 2.5
b3[2] = 6.5
b3[4] = 6.5
b3[5] = 2.5
```