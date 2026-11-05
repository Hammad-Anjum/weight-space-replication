Design (hand-set, no training).

Key facts used: each row 1..8 holds at most one entity (slot = row - 1), so every row is a "lane". Player rows are 1..8. Lane-local weights give the player's column (Xp_r) only when the player is in lane r, so no global column sum is needed.

Layer 1 (32 units), all tanh:
- Units 0-7 (EA_r): enemy in my lane. tanh(4*(player_in_lane_r + enemy_in_lane_r) - 6), so about +1 only when both are present.
- Units 8-15 (GR_r): gold in lane r, signed toward the right of the player. tanh(0.3*(gold_col - player_col)) when both are present, about -1 otherwise.
- Units 16-23 (GL_r): same as GR but signed toward the left.
- Units 24-31 (EB_r): player in lane r and enemy in lane r+1 (lane 8 counts as occupied below, via the bottom wall).

Layer 2 (4 used units, the rest are zero):
- Unit 0 = s (danger): sum of EA plus threshold, about +1 if an enemy shares my lane.
- Unit 1 = q (below occupied): sum of EB plus threshold.
- Unit 2 = r (gold on my right in my lane): tanh(10*GR_py).
- Unit 3 = l (gold on my left in my lane): tanh(10*GL_py).

Output: logits = 6*(...) so margins are about 6 (near-deterministic).
- up = 6s + 6q - 6; down = 6s - 6q - 6 (dodge down unless the lane below is occupied).
- right = 6r - 6s - 6; left = 6l - 6s - 6 (chase gold in my lane only when not in danger).
- no-op and fire = 0.

Limits: gold in other lanes is not sought; enemy direction is ignored; dodging in lane 1 or lane 8 can be blocked.

```edits
# Layer 1 units 0-7: EA_r, enemy in my lane
W1[60:120:6, 0] = 4
W1[61:120:6, 0] = 4
W1[120:180:6, 1] = 4
W1[121:180:6, 1] = 4
W1[180:240:6, 2] = 4
W1[181:240:6, 2] = 4
W1[240:300:6, 3] = 4
W1[241:300:6, 3] = 4
W1[300:360:6, 4] = 4
W1[301:360:6, 4] = 4
W1[360:420:6, 5] = 4
W1[361:420:6, 5] = 4
W1[420:480:6, 6] = 4
W1[421:480:6, 6] = 4
W1[480:540:6, 7] = 4
W1[481:540:6, 7] = 4
b1[0:8] = -6
# Layer 1 units 8-15: GR_r, gold on my right in my lane
W1[60:120:6, 8] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[62:120:6, 8] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[120:180:6, 9] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[122:180:6, 9] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[180:240:6, 10] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[182:240:6, 10] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[240:300:6, 11] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[242:300:6, 11] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[300:360:6, 12] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[302:360:6, 12] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[360:420:6, 13] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[362:420:6, 13] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[420:480:6, 14] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[422:480:6, 14] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[480:540:6, 15] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[482:540:6, 15] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
b1[8:16] = -12
# Layer 1 units 16-23: GL_r, gold on my left in my lane
W1[60:120:6, 16] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[62:120:6, 16] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[120:180:6, 17] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[122:180:6, 17] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[180:240:6, 18] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[182:240:6, 18] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[240:300:6, 19] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[242:300:6, 19] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[300:360:6, 20] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[302:360:6, 20] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[360:420:6, 21] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[362:420:6, 21] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[420:480:6, 22] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[422:480:6, 22] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
W1[480:540:6, 23] = [6, 6.3, 6.6, 6.9, 7.2, 7.5, 7.8, 8.1, 8.4, 8.7]
W1[482:540:6, 23] = [6, 5.7, 5.4, 5.1, 4.8, 4.5, 4.2, 3.9, 3.6, 3.3]
b1[16:24] = -12
# Layer 1 units 24-31: EB_r, player in lane r and enemy in lane r+1 (lane 8: player only)
W1[60:120:6, 24] = 4
W1[121:180:6, 24] = 4
W1[120:180:6, 25] = 4
W1[181:240:6, 25] = 4
W1[180:240:6, 26] = 4
W1[241:300:6, 26] = 4
W1[240:300:6, 27] = 4
W1[301:360:6, 27] = 4
W1[300:360:6, 28] = 4
W1[361:420:6, 28] = 4
W1[360:420:6, 29] = 4
W1[421:480:6, 29] = 4
W1[420:480:6, 30] = 4
W1[481:540:6, 30] = 4
W1[480:540:6, 31] = 4
b1[24:31] = -6
b1[31] = -2
# Layer 2
W2[0:8, 0] = 4
b2[0] = 28
W2[24:32, 1] = 4
b2[1] = 28
W2[8:16, 2] = 10
b2[2] = 70
W2[16:24, 3] = 10
b2[3] = 70
# Output: 0 no-op, 1 left, 2 up, 3 right, 4 down, 5 fire
W3[0, 1] = -6
W3[3, 1] = 6
b3[1] = -6
W3[0, 2] = 6
W3[1, 2] = 6
b3[2] = -6
W3[0, 3] = -6
W3[2, 3] = 6
b3[3] = -6
W3[0, 4] = 6
W3[1, 4] = -6
b3[4] = -6
```
