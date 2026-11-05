DESIGN

Key fact from the source: each lane (rows 1..8) holds at most one entity, so a lane with a treasure has no enemy. The player never moves horizontally and stays near column 5. Entities cross the board, so treasure comes to the player. The policy moves vertically only.

Layer 1 (30 of 32 units used). Each unit is gated on the player's row.
- Units 0-7, D_p: "an enemy is in my own row p". The pre-activation is 10*player_in_row_p + 10*enemy_in_row_p - 17, so the unit is about +1 only when both are true and about -1 otherwise.
- Units 8-15, E_r: "an enemy is in row r", about +/-1.
- Units 16-22, GU_p, for p = 2..8: "treasure above me and the row above is free of enemies". The pre-activation is 10*player_in_row_p + sum of distance-weighted treasure cells in rows above - 20*enemy_in_row_(p-1) - 10. Nearer rows get larger weights, so nearer treasure wins ties. The unit outputs 0 if there is no treasure, and -1 if the row above is blocked or the player is not in row p.
- Units 23-29, GD_p, for p = 1..7: the same for treasure below.

Layer 2 (24 units used)
- Units 0-6, FU_p: flee up. Active when D_p is on and E_(p-1) is off.
- Units 7-13, FD_p: flee down. Active when D_p is on and E_(p+1) is off.
- Unit 14: sums the GU units, with a +6 bias to cancel the -1 outputs of inactive units. This is the "go up for treasure" signal.
- Unit 15: the same for the GD units, the "go down for treasure" signal.
- Units 16-19: fallback up for rows 5-8. Active when the player's row has an enemy and both neighbouring rows also have enemies.
- Units 20-23: fallback down for rows 1-4, with the same condition.

Output layer
- Up and down logits combine three signals. Flee and fallback weigh 9 each. The treasure signals weigh 16. Large biases cancel the constant -1 outputs of inactive units.
- No-op and fire have logit +1. Left and right have logit -3.
- Fleeing outweighs treasure chasing. Treasure chasing outweighs idling.

```edits
b1[0:8] = -17
W1[60:120:6, 0] = 10
W1[61:120:6, 0] = 10
W1[120:180:6, 1] = 10
W1[121:180:6, 1] = 10
W1[180:240:6, 2] = 10
W1[181:240:6, 2] = 10
W1[240:300:6, 3] = 10
W1[241:300:6, 3] = 10
W1[300:360:6, 4] = 10
W1[301:360:6, 4] = 10
W1[360:420:6, 5] = 10
W1[361:420:6, 5] = 10
W1[420:480:6, 6] = 10
W1[421:480:6, 6] = 10
W1[480:540:6, 7] = 10
W1[481:540:6, 7] = 10
b1[8:16] = -3
W1[61:120:6, 8] = 6
W1[121:180:6, 9] = 6
W1[181:240:6, 10] = 6
W1[241:300:6, 11] = 6
W1[301:360:6, 12] = 6
W1[361:420:6, 13] = 6
W1[421:480:6, 14] = 6
W1[481:540:6, 15] = 6
b1[16:23] = -10
W1[120:180:6, 16] = 10
W1[61:120:6, 16] = -20
W1[62:120:6, 16] = 0.9
W1[180:240:6, 17] = 10
W1[121:180:6, 17] = -20
W1[122:180:6, 17] = 0.9
W1[62:120:6, 17] = 0.55
W1[240:300:6, 18] = 10
W1[181:240:6, 18] = -20
W1[182:240:6, 18] = 0.9
W1[122:180:6, 18] = 0.55
W1[62:120:6, 18] = 0.4
W1[300:360:6, 19] = 10
W1[241:300:6, 19] = -20
W1[242:300:6, 19] = 0.9
W1[182:240:6, 19] = 0.55
W1[122:180:6, 19] = 0.4
W1[62:120:6, 19] = 0.32
W1[360:420:6, 20] = 10
W1[301:360:6, 20] = -20
W1[302:360:6, 20] = 0.9
W1[242:300:6, 20] = 0.55
W1[182:240:6, 20] = 0.4
W1[122:180:6, 20] = 0.32
W1[62:120:6, 20] = 0.27
W1[420:480:6, 21] = 10
W1[361:420:6, 21] = -20
W1[362:420:6, 21] = 0.9
W1[302:360:6, 21] = 0.55
W1[242:300:6, 21] = 0.4
W1[182:240:6, 21] = 0.32
W1[122:180:6, 21] = 0.27
W1[62:120:6, 21] = 0.23
W1[480:540:6, 22] = 10
W1[421:480:6, 22] = -20
W1[422:480:6, 22] = 0.9
W1[362:420:6, 22] = 0.55
W1[302:360:6, 22] = 0.4
W1[242:300:6, 22] = 0.32
W1[182:240:6, 22] = 0.27
W1[122:180:6, 22] = 0.23
W1[62:120:6, 22] = 0.2
b1[23:30] = -10
W1[60:120:6, 23] = 10
W1[121:180:6, 23] = -20
W1[122:180:6, 23] = 0.9
W1[182:240:6, 23] = 0.55
W1[242:300:6, 23] = 0.4
W1[302:360:6, 23] = 0.32
W1[362:420:6, 23] = 0.27
W1[422:480:6, 23] = 0.23
W1[482:540:6, 23] = 0.2
W1[120:180:6, 24] = 10
W1[181:240:6, 24] = -20
W1[182:240:6, 24] = 0.9
W1[242:300:6, 24] = 0.55
W1[302:360:6, 24] = 0.4
W1[362:420:6, 24] = 0.32
W1[422:480:6, 24] = 0.27
W1[482:540:6, 24] = 0.23
W1[180:240:6, 25] = 10
W1[241:300:6, 25] = -20
W1[242:300:6, 25] = 0.9
W1[302:360:6, 25] = 0.55
W1[362:420:6, 25] = 0.4
W1[422:480:6, 25] = 0.32
W1[482:540:6, 25] = 0.27
W1[240:300:6, 26] = 10
W1[301:360:6, 26] = -20
W1[302:360:6, 26] = 0.9
W1[362:420:6, 26] = 0.55
W1[422:480:6, 26] = 0.4
W1[482:540:6, 26] = 0.32
W1[300:360:6, 27] = 10
W1[361:420:6, 27] = -20
W1[362:420:6, 27] = 0.9
W1[422:480:6, 27] = 0.55
W1[482:540:6, 27] = 0.4
W1[360:420:6, 28] = 10
W1[421:480:6, 28] = -20
W1[422:480:6, 28] = 0.9
W1[482:540:6, 28] = 0.55
W1[420:480:6, 29] = 10
W1[481:540:6, 29] = -20
W1[482:540:6, 29] = 0.9
b2[0:7] = -6
W2[1, 0] = 4
W2[8, 0] = -4
W2[2, 1] = 4
W2[9, 1] = -4
W2[3, 2] = 4
W2[10, 2] = -4
W2[4, 3] = 4
W2[11, 3] = -4
W2[5, 4] = 4
W2[12, 4] = -4
W2[6, 5] = 4
W2[13, 5] = -4
W2[7, 6] = 4
W2[14, 6] = -4
b2[7:14] = -6
W2[0, 7] = 4
W2[9, 7] = -4
W2[1, 8] = 4
W2[10, 8] = -4
W2[2, 9] = 4
W2[11, 9] = -4
W2[3, 10] = 4
W2[12, 10] = -4
W2[4, 11] = 4
W2[13, 11] = -4
W2[5, 12] = 4
W2[14, 12] = -4
W2[6, 13] = 4
W2[15, 13] = -4
b2[14] = 6
W2[16:23, 14] = 1
b2[15] = 6
W2[23:30, 15] = 1
b2[16:19] = -10
b2[19] = -6
b2[20] = -6
b2[21:24] = -10
W2[4, 16] = 4
W2[11, 16] = 4
W2[13, 16] = 4
W2[5, 17] = 4
W2[12, 17] = 4
W2[14, 17] = 4
W2[6, 18] = 4
W2[13, 18] = 4
W2[15, 18] = 4
W2[7, 19] = 4
W2[14, 19] = 4
W2[0, 20] = 4
W2[9, 20] = 4
W2[1, 21] = 4
W2[8, 21] = 4
W2[10, 21] = 4
W2[2, 22] = 4
W2[9, 22] = 4
W2[11, 22] = 4
W2[3, 23] = 4
W2[10, 23] = 4
W2[12, 23] = 4
W3[0:7, 2] = 9
W3[16:20, 2] = 9
W3[14, 2] = 16
W3[7:14, 4] = 9
W3[20:24, 4] = 9
W3[15, 4] = 16
b3[0] = 1
b3[1] = -3
b3[2] = 96
b3[3] = -3
b3[4] = 96
b3[5] = 1
```
