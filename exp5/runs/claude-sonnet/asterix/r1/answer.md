## Design

Facts used from the source: each of the 8 lanes (rows 1..8) holds at most one entity (enemy or treasure), the player moves faster than any entity, a lane that holds treasure holds no enemy, and the player only dies by entering an enemy cell or by an enemy moving into it.

Strategy, in priority order:
1. Own lane holds treasure: run horizontally toward it. The lane has no enemy, so this is safe.
2. Own lane holds an enemy: leave vertically at once, to a neighbouring lane whose enemy is not within 1 column of the player. Prefer the direction of the nearest treasure.
3. Own lane is empty: move vertically toward the nearest treasure lane, but only into a lane whose enemy is at least 2 columns away (or that has no enemy). Otherwise wait with no-op.
4. Idle in an empty lane with no treasure anywhere: drift to columns 4 or 5, away from the edge-spawn kill zone.

Layer 1 (32 units) is four blocks of 8 units. Unit k of a block is gated by "player is in lane k": the player cells of lane k get a large positive weight and the bias cancels it. Inactive units therefore output exactly -1. Summing a block and adding 7 gives one scalar for the player's actual lane.
- Block 0 (units 0-7) gives s0 for the own lane. An enemy gives +1 exactly, an empty lane gives -1 exactly, and treasure gives tanh(0.2*(px-gx)). That is positive when treasure is left of the player and negative when it is right.
- Block 1 (units 8-15) gives sV, a saturated vertical desire. Treasure weights are +/-(200 or 220) halved per lane of distance, so the nearest treasure wins. Negative means up, positive means down. A small term 0.1*(px-4.5) is added; it is the centering signal when there is no treasure.
- Block 2 (units 16-23) gives sU = tanh(px - ex) for the enemy in the lane above. It is -1 if there is no enemy and 0 in lane 1.
- Block 3 (units 24-31) gives sD, the same for the lane below, and is 0 in lane 8.

A value with |s| > 0.863 means "not within 1 column", so the move is OK.

Layer 2 (20 used units) reads the four scalars through W2 with weights that are multiples of the block sum, and biases that include the +7 per block offset. Each unit is a threshold or AND gate:
- Units 0-3 are thresholds on s0: left chase (A minus B) and right chase (C minus D).
- Units 4-7 are "empty lane AND desire AND destination OK" for up and down. Each has two units, for the two ways the destination can be OK.
- Units 8-15 are "enemy in own lane AND destination OK" escapes. Units 8-11 also require the desire direction, and units 12-15 do not.
- Units 16-19 are "empty lane AND centering" drift left and right.

Output layer: baseline logits are noop 0 and every other action -10. Each firing unit adds +20 net, so the chosen action is almost deterministic.

```edits
# ---------- layer 1, block 0 (units 0-7): own-lane code, unit k-1 for player lane k
b1[0:8] = -150
W1[60:120:6, 0] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[61:120:6, 0] = 80
W1[62:120:6, 0] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[120:180:6, 1] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[121:180:6, 1] = 80
W1[122:180:6, 1] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[180:240:6, 2] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[181:240:6, 2] = 80
W1[182:240:6, 2] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[240:300:6, 3] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[241:300:6, 3] = 80
W1[242:300:6, 3] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[300:360:6, 4] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[301:360:6, 4] = 80
W1[302:360:6, 4] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[360:420:6, 5] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[361:420:6, 5] = 80
W1[362:420:6, 5] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[420:480:6, 6] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[421:480:6, 6] = 80
W1[422:480:6, 6] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
W1[480:540:6, 7] = [100, 100.2, 100.4, 100.6, 100.8, 101, 101.2, 101.4, 101.6, 101.8]
W1[481:540:6, 7] = 80
W1[482:540:6, 7] = [50, 49.8, 49.6, 49.4, 49.2, 49, 48.8, 48.6, 48.4, 48.2]
# ---------- layer 1, block 1 (units 8-15): vertical treasure desire + centering, unit 8+k-1
b1[8:16] = -600
W1[60:120:6, 8] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[120:180:6, 9] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[180:240:6, 10] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[240:300:6, 11] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[300:360:6, 12] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[360:420:6, 13] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[420:480:6, 14] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[480:540:6, 15] = [599.55, 599.65, 599.75, 599.85, 599.95, 600.05, 600.15, 600.25, 600.35, 600.45]
W1[122:180:6, 8] = 220
W1[182:240:6, 8] = 110
W1[242:300:6, 8] = 55
W1[302:360:6, 8] = 27.5
W1[362:420:6, 8] = 13.75
W1[422:480:6, 8] = 6.875
W1[482:540:6, 8] = 3.4375
W1[62:120:6, 9] = -200
W1[182:240:6, 9] = 220
W1[242:300:6, 9] = 110
W1[302:360:6, 9] = 55
W1[362:420:6, 9] = 27.5
W1[422:480:6, 9] = 13.75
W1[482:540:6, 9] = 6.875
W1[62:120:6, 10] = -100
W1[122:180:6, 10] = -200
W1[242:300:6, 10] = 220
W1[302:360:6, 10] = 110
W1[362:420:6, 10] = 55
W1[422:480:6, 10] = 27.5
W1[482:540:6, 10] = 13.75
W1[62:120:6, 11] = -50
W1[122:180:6, 11] = -100
W1[182:240:6, 11] = -200
W1[302:360:6, 11] = 220
W1[362:420:6, 11] = 110
W1[422:480:6, 11] = 55
W1[482:540:6, 11] = 27.5
W1[62:120:6, 12] = -25
W1[122:180:6, 12] = -50
W1[182:240:6, 12] = -100
W1[242:300:6, 12] = -200
W1[362:420:6, 12] = 220
W1[422:480:6, 12] = 110
W1[482:540:6, 12] = 55
W1[62:120:6, 13] = -12.5
W1[122:180:6, 13] = -25
W1[182:240:6, 13] = -50
W1[242:300:6, 13] = -100
W1[302:360:6, 13] = -200
W1[422:480:6, 13] = 220
W1[482:540:6, 13] = 110
W1[62:120:6, 14] = -6.25
W1[122:180:6, 14] = -12.5
W1[182:240:6, 14] = -25
W1[242:300:6, 14] = -50
W1[302:360:6, 14] = -100
W1[362:420:6, 14] = -200
W1[482:540:6, 14] = 220
W1[62:120:6, 15] = -3.125
W1[122:180:6, 15] = -6.25
W1[182:240:6, 15] = -12.5
W1[242:300:6, 15] = -25
W1[302:360:6, 15] = -50
W1[362:420:6, 15] = -100
W1[422:480:6, 15] = -200
# ---------- layer 1, block 2 (units 16-23): enemy in lane above, relative column; unit 16+k-1
b1[16] = -100
b1[17:24] = -150
W1[60:120:6, 16] = 100
W1[120:180:6, 17] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[61:120:6, 17] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[180:240:6, 18] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[121:180:6, 18] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[240:300:6, 19] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[181:240:6, 19] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[300:360:6, 20] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[241:300:6, 20] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[360:420:6, 21] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[301:360:6, 21] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[420:480:6, 22] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[361:420:6, 22] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[480:540:6, 23] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[421:480:6, 23] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
# ---------- layer 1, block 3 (units 24-31): enemy in lane below, relative column; unit 24+k-1
b1[24:31] = -150
b1[31] = -100
W1[480:540:6, 31] = 100
W1[60:120:6, 24] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[121:180:6, 24] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[120:180:6, 25] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[181:240:6, 25] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[180:240:6, 26] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[241:300:6, 26] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[240:300:6, 27] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[301:360:6, 27] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[300:360:6, 28] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[361:420:6, 28] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[360:420:6, 29] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[421:480:6, 29] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
W1[420:480:6, 30] = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
W1[481:540:6, 30] = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41]
# ---------- layer 2: gates on the four block sums (rows 0:8 s0, 8:16 sV, 16:24 sU, 24:32 sD)
# unit 0: s0 > 0.05 (treasure left or enemy)
W2[0:8, 0] = 200
b2[0] = 1390
# unit 1: s0 > 0.99 (enemy in own lane)
W2[0:8, 1] = 1000
b2[1] = 6010
# unit 2: s0 > -0.99 (not empty)
W2[0:8, 2] = 1000
b2[2] = 7990
# unit 3: s0 > -0.05 (treasure left or enemy)
W2[0:8, 3] = 200
b2[3] = 1410
# unit 4: empty lane, desire up, lane above clear on the right-hand side code (sU > 0.863)
W2[0:8, 4] = -1000
W2[8:16, 4] = -100
W2[16:24, 4] = 100
b2[4] = -8185.3
# unit 5: empty lane, desire up, sU < -0.863
W2[0:8, 5] = -1000
W2[8:16, 5] = -100
W2[16:24, 5] = -100
b2[5] = -9585.3
# unit 6: empty lane, desire down, sD > 0.863
W2[0:8, 6] = -1000
W2[8:16, 6] = 100
W2[24:32, 6] = 100
b2[6] = -6785.3
# unit 7: empty lane, desire down, sD < -0.863
W2[0:8, 7] = -1000
W2[8:16, 7] = 100
W2[24:32, 7] = -100
b2[7] = -8185.3
# unit 8: enemy in own lane, desire up, sU > 0.863
W2[0:8, 8] = 1000
W2[8:16, 8] = -100
W2[16:24, 8] = 100
b2[8] = 5814.7
# unit 9: enemy in own lane, desire up, sU < -0.863
W2[0:8, 9] = 1000
W2[8:16, 9] = -100
W2[16:24, 9] = -100
b2[9] = 4414.7
# unit 10: enemy in own lane, desire down, sD > 0.863
W2[0:8, 10] = 1000
W2[8:16, 10] = 100
W2[24:32, 10] = 100
b2[10] = 7214.7
# unit 11: enemy in own lane, desire down, sD < -0.863
W2[0:8, 11] = 1000
W2[8:16, 11] = 100
W2[24:32, 11] = -100
b2[11] = 5814.7
# unit 12: enemy in own lane, up is OK (sU > 0.863)
W2[0:8, 12] = 1000
W2[16:24, 12] = 100
b2[12] = 6613.7
# unit 13: enemy in own lane, up is OK (sU < -0.863)
W2[0:8, 13] = 1000
W2[16:24, 13] = -100
b2[13] = 5213.7
# unit 14: enemy in own lane, down is OK (sD > 0.863)
W2[0:8, 14] = 1000
W2[24:32, 14] = 100
b2[14] = 6613.7
# unit 15: enemy in own lane, down is OK (sD < -0.863)
W2[0:8, 15] = 1000
W2[24:32, 15] = -100
b2[15] = 5213.7
# units 16-19: empty lane, centering drift (sV in (0.1,0.6) -> left, sV in (-0.6,-0.1) -> right)
W2[0:8, 16] = -10000
W2[8:16, 16] = 400
b2[16] = -77240
W2[0:8, 17] = -10000
W2[8:16, 17] = 400
b2[17] = -77440
W2[0:8, 18] = -10000
W2[8:16, 18] = -400
b2[18] = -82840
W2[0:8, 19] = -10000
W2[8:16, 19] = -400
b2[19] = -83040
# ---------- output layer
# left (action 1): chase = unit0 - unit1, centering = unit16 - unit17
W3[0, 1] = 10
W3[1, 1] = -10
W3[16, 1] = 10
W3[17, 1] = -10
# right (action 3): chase = unit2 - unit3 (C minus D), centering = unit18 - unit19
W3[2, 3] = 10
W3[3, 3] = -10
W3[18, 3] = 10
W3[19, 3] = -10
# up (action 2): units 4,5 (seek), 8,9 (escape with desire), 12,13 (escape any)
W3[4:6, 2] = 10
W3[8:10, 2] = 10
W3[12:14, 2] = 10
# down (action 4): units 6,7 (seek), 10,11 (escape with desire), 14,15 (escape any)
W3[6:8, 4] = 10
W3[10:12, 4] = 10
W3[14:16, 4] = 10
# baselines: noop 0, all other actions -10 (the +50 on up/down offsets the six -10 resting terms)
b3[0] = 0
b3[1] = -10
b3[2] = 50
b3[3] = -10
b3[4] = 50
b3[5] = -10
```
