I use the oxygen gauge as a rough phase clock to sweep the submarine through different depths, staying near the center so crossing divers can be collected. Gaps between the oxygen and diver bars trigger an ascent; a row-matched danger cue favors firing. A boundary guard prevents surfacing without a diver. The hidden units detect player rows, gauge phases, diver-count-dependent bar gaps, and danger in the player’s row.

```edits
# Player-row detectors
W1[0:60:6, 0] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[60:120:6, 1] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[120:180:6, 2] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[180:240:6, 3] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[240:300:6, 4] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[300:360:6, 5] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[360:420:6, 6] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[420:480:6, 7] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
W1[480:540:6, 8] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
b1[0:9] = -1

# Oxygen/diver gauge bits in columns 0..7
W1[545, 9] = 2
W1[551, 10] = 2
W1[557, 11] = 2
W1[563, 12] = 2
W1[569, 13] = 2
W1[575, 14] = 2
W1[581, 15] = 2
W1[587, 16] = 2
b1[9:17] = -1

# A gap at column k with column 8 occupied signals divers aboard
W1[593, 17] = 3
W1[587, 17] = -3
W1[593, 18] = 3
W1[581, 18] = -3
W1[593, 19] = 3
W1[575, 19] = -3
W1[593, 20] = 3
W1[569, 20] = -3
W1[593, 21] = 3
W1[563, 21] = -3
W1[593, 22] = 3
W1[557, 22] = -3
b1[17:23] = -1.5

# Danger-by-row detectors
W1[1:60:6, 23] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[61:120:6, 24] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[121:180:6, 25] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[181:240:6, 26] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[241:300:6, 27] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[301:360:6, 28] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[361:420:6, 29] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[421:480:6, 30] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
W1[481:540:6, 31] = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
b1[23:32] = -1

# Copy player rows; detect oxygen-level phases; copy carry cues; match danger to player row
W2[0, 0] = 2
W2[1, 1] = 2
W2[2, 2] = 2
W2[3, 3] = 2
W2[4, 4] = 2
W2[5, 5] = 2
W2[6, 6] = 2
W2[7, 7] = 2
W2[8, 8] = 2

W2[15, 9] = 2
W2[16, 9] = -2
W2[14, 10] = 2
W2[15, 10] = -2
W2[13, 11] = 2
W2[14, 11] = -2
W2[12, 12] = 2
W2[13, 12] = -2
W2[11, 13] = 2
W2[12, 13] = -2
W2[10, 14] = 2
W2[11, 14] = -2
W2[9, 15] = 2
W2[10, 15] = -2
b2[9:16] = -2

W2[17, 16] = 2
W2[18, 17] = 2
W2[19, 18] = 2
W2[20, 19] = 2
W2[21, 20] = 2
W2[22, 21] = 2

W2[0, 22] = 2
W2[23, 22] = 2
W2[1, 23] = 2
W2[24, 23] = 2
W2[2, 24] = 2
W2[25, 24] = 2
W2[3, 25] = 2
W2[26, 25] = 2
W2[4, 26] = 2
W2[27, 26] = 2
W2[5, 27] = 2
W2[28, 27] = 2
W2[6, 28] = 2
W2[29, 28] = 2
W2[7, 29] = 2
W2[30, 29] = 2
W2[8, 30] = 2
W2[31, 30] = 2
b2[22:31] = -2

# Vertical target follows oxygen phases; carry cues strongly override it
W3[0:9, 2] = [0, 0.66, 1.32, 1.98, 2.64, 3.30, 3.96, 4.62, 5.28]
W3[0:9, 4] = [0, -0.66, -1.32, -1.98, -2.64, -3.30, -3.96, -4.62, -5.28]
W3[9:16, 2] = [1.376, 2.752, 4.128, 4.816, 3.440, 2.064, 0.688]
W3[9:16, 4] = [-1.376, -2.752, -4.128, -4.816, -3.440, -2.064, -0.688]
W3[16:22, 2] = 12.5

# Stop upward motion at row 1 unless a carry cue overrides it
W3[1, 2] -= 2.75

# Fire more when danger shares the player's row
W3[22:31, 5] = 1.2

b3[0] = 0
b3[1] = -4
b3[2] = 70.43
b3[3] = -4
b3[4] = -1.829
b3[5] = 11.26
```