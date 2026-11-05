## Design

**Strategy.** The player never moves sideways. It stays in column 5, where it starts, and only moves up and down. Each row holds at most one entity, and every entity has to cross column 5. So each row's situation is a function of its own cells only:
- an enemy coming toward column 5 is a threat, more so the closer it is;
- gold coming toward column 5 is a point that arrives on its own if the player waits in that row (a gold row is also safe, because the row can't hold an enemy);
- anything that has already passed column 5 is harmless.

Each step, the policy compares three choices: stay, go up one row, or go down one row. It picks the row that is least dangerous and most rewarding. It also looks at gold further away, and gives a small penalty when the row two steps away is dangerous (a sticky repeat of the move would land there). Left, right and fire get very low logits, so the column never changes.

**Layer 1 (24 of the 32 units used).**
- **Units 0-7, D_r (danger at (row r, column 5), r = unit+1).** These use the enemy channel and the trail channel of row r. The trail sits behind the entity, so with suitable weights one linear unit can read the entity's direction, including the edge columns where the trail is off-grid. I solved the 20 cases (column 0-9 times direction) exactly:
  - enemy weights a = [0,0,3,4,11,12,11,4,3,0]
  - trail weights b = [0,0,0,-3,-4,-11,-4,-3,0,0]
  - bias -4

  The pre-activation is -4 for a safe row (empty, enemy moving away, or enemy 4 or more cells away). It is -1 when the enemy is 3 cells away and approaching (L), 0 at 2 cells (M), and +4 at 1 cell or at column 5 (H, meaning certain or possible death). Gold trails only push the value lower, so gold rows read as safe.
- **Units 8-15, G_r (gold that will cross column 5 in row r).** These are solved the same way:
  - gold weights [6,6,12,12,18,21,18,12,12,6]
  - trail weights [0,-6,-6,-12,-12,-18,-12,-12,-6,-6]
  - bias -4

  The pre-activation is +2 for gold that is approaching, +5 for gold at column 5, and -4 for gold moving away. Enemy trails only push the value lower.
- **Units 16-23, P_r: the player is in row r.**

**Layer 2 (22 units), gated by the player's row.** Each unit gets weight +10 from P_r and its bias includes -10, so only the units for the player's current row are active. The others sit at exactly -1, and the output biases cancel them. For the player's row r:
- S_r scores staying, A_r scores moving up, B_r scores moving down.
- Each one computes, in the near-linear part of tanh: z = beta - 0.25*Bad(destination row) + (decaying weights 0.2, 0.17, 0.15, ... on gold 2 to 7 rows away in that direction) - 0.05*Dn(row two steps away).
- Bad = 2*Dn - Gn, where Dn and Gn are the units rescaled to 0..1. It is about -1 for approaching gold, 0 for safe, 0.24 for L, 1 for M and 2 for H.
- beta is 0.085 for staying (avoids aimless moves) and 0 for moving, plus a small push away from the edge rows 1/2 and 7/8.

**Output.** The noop, up and down logits are 60*tanh(z) of the active unit, so they are roughly linear in the scores. Moving up from row 1, moving down from row 8, and left, right and fire all get -60. These are the logit gaps the design gives:

| Situation | Logit gap |
|---|---|
| Escape from an H row to a safe or gold row | over 20 |
| Escape from an H row to an M row | about 9 |
| Leave an M row for a safe row | about 10 |
| Move from a safe row into an adjacent gold row | about 9 |
| Stay in a safe row rather than move into a dangerous one | over 30 |

## Weights

```edits
# ===== Layer 1 =====
# D_r units 0..7 : enemy channel (ch1) and trail channel (ch4) of row r, bias -4
W1[61:120:6, 0] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[64:120:6, 0] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[121:180:6, 1] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[124:180:6, 1] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[181:240:6, 2] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[184:240:6, 2] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[241:300:6, 3] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[244:300:6, 3] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[301:360:6, 4] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[304:360:6, 4] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[361:420:6, 5] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[364:420:6, 5] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[421:480:6, 6] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[424:480:6, 6] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
W1[481:540:6, 7] = [0, 0, 3, 4, 11, 12, 11, 4, 3, 0]
W1[484:540:6, 7] = [0, 0, 0, -3, -4, -11, -4, -3, 0, 0]
b1[0:8] = -4
# G_r units 8..15 : gold channel (ch2) and trail channel (ch4) of row r, bias -4
W1[62:120:6, 8] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[64:120:6, 8] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[122:180:6, 9] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[124:180:6, 9] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[182:240:6, 10] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[184:240:6, 10] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[242:300:6, 11] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[244:300:6, 11] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[302:360:6, 12] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[304:360:6, 12] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[362:420:6, 13] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[364:420:6, 13] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[422:480:6, 14] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[424:480:6, 14] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
W1[482:540:6, 15] = [6, 6, 12, 12, 18, 21, 18, 12, 12, 6]
W1[484:540:6, 15] = [0, -6, -6, -12, -12, -18, -12, -12, -6, -6]
b1[8:16] = -4
# P_r units 16..23 : player channel (ch0) of row r, bias -5
W1[60:120:6, 16] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[120:180:6, 17] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[180:240:6, 18] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[240:300:6, 19] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[300:360:6, 20] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[360:420:6, 21] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[420:480:6, 22] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
W1[480:540:6, 23] = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
b1[16:24] = -5

# ===== Layer 2 =====
# S_r (stay) units 0..7, gated by P_r
W2[16, 0] = 10
W2[17, 1] = 10
W2[18, 2] = 10
W2[19, 3] = 10
W2[20, 4] = 10
W2[21, 5] = 10
W2[22, 6] = 10
W2[23, 7] = 10
W2[0, 0] = -0.25
W2[1, 1] = -0.25
W2[2, 2] = -0.25
W2[3, 3] = -0.25
W2[4, 4] = -0.25
W2[5, 5] = -0.25
W2[6, 6] = -0.25
W2[7, 7] = -0.25
W2[8, 0] = 0.125
W2[9, 1] = 0.125
W2[10, 2] = 0.125
W2[11, 3] = 0.125
W2[12, 4] = 0.125
W2[13, 5] = 0.125
W2[14, 6] = 0.125
W2[15, 7] = 0.125
b2[0:8] = -10.04

# A_r (move up) units 8..14 for rows 2..8
W2[0:8, 8] = [-0.25, 0, 0, 0, 0, 0, 0, 0]
W2[8:16, 8] = [0.125, 0, 0, 0, 0, 0, 0, 0]
W2[17, 8] = 10
b2[8] = -10.125
W2[0:8, 9] = [-0.025, -0.25, 0, 0, 0, 0, 0, 0]
W2[8:16, 9] = [0.1, 0.125, 0, 0, 0, 0, 0, 0]
W2[18, 9] = 10
b2[9] = -10.05
W2[0:8, 10] = [0, -0.025, -0.25, 0, 0, 0, 0, 0]
W2[8:16, 10] = [0.085, 0.1, 0.125, 0, 0, 0, 0, 0]
W2[19, 10] = 10
b2[10] = -9.965
W2[0:8, 11] = [0, 0, -0.025, -0.25, 0, 0, 0, 0]
W2[8:16, 11] = [0.075, 0.085, 0.1, 0.125, 0, 0, 0, 0]
W2[20, 11] = 10
b2[11] = -9.89
W2[0:8, 12] = [0, 0, 0, -0.025, -0.25, 0, 0, 0]
W2[8:16, 12] = [0.07, 0.075, 0.085, 0.1, 0.125, 0, 0, 0]
W2[21, 12] = 10
b2[12] = -9.82
W2[0:8, 13] = [0, 0, 0, 0, -0.025, -0.25, 0, 0]
W2[8:16, 13] = [0.065, 0.07, 0.075, 0.085, 0.1, 0.125, 0, 0]
W2[22, 13] = 10
b2[13] = -9.705
W2[0:8, 14] = [0, 0, 0, 0, 0, -0.025, -0.25, 0]
W2[8:16, 14] = [0.06, 0.065, 0.07, 0.075, 0.085, 0.1, 0.125, 0]
W2[23, 14] = 10
b2[14] = -9.595

# B_r (move down) units 15..21 for rows 1..7
W2[0:8, 15] = [0, -0.25, -0.025, 0, 0, 0, 0, 0]
W2[8:16, 15] = [0, 0.125, 0.1, 0.085, 0.075, 0.07, 0.065, 0.06]
W2[16, 15] = 10
b2[15] = -9.595
W2[0:8, 16] = [0, 0, -0.25, -0.025, 0, 0, 0, 0]
W2[8:16, 16] = [0, 0, 0.125, 0.1, 0.085, 0.075, 0.07, 0.065]
W2[17, 16] = 10
b2[16] = -9.705
W2[0:8, 17] = [0, 0, 0, -0.25, -0.025, 0, 0, 0]
W2[8:16, 17] = [0, 0, 0, 0.125, 0.1, 0.085, 0.075, 0.07]
W2[18, 17] = 10
b2[17] = -9.82
W2[0:8, 18] = [0, 0, 0, 0, -0.25, -0.025, 0, 0]
W2[8:16, 18] = [0, 0, 0, 0, 0.125, 0.1, 0.085, 0.075]
W2[19, 18] = 10
b2[18] = -9.89
W2[0:8, 19] = [0, 0, 0, 0, 0, -0.25, -0.025, 0]
W2[8:16, 19] = [0, 0, 0, 0, 0, 0.125, 0.1, 0.085]
W2[20, 19] = 10
b2[19] = -9.965
W2[0:8, 20] = [0, 0, 0, 0, 0, 0, -0.25, -0.025]
W2[8:16, 20] = [0, 0, 0, 0, 0, 0, 0.125, 0.1]
W2[21, 20] = 10
b2[20] = -10.05
W2[0:8, 21] = [0, 0, 0, 0, 0, 0, 0, -0.25]
W2[8:16, 21] = [0, 0, 0, 0, 0, 0, 0, 0.125]
W2[22, 21] = 10
b2[21] = -10.125

# ===== Output =====
W3[0:8, 0] = 60
W3[8:15, 2] = 60
W3[15:22, 4] = 60
b3[0] = 420
b3[1] = -60
b3[2] = 360
b3[3] = -60
b3[4] = 360
b3[5] = -60
```
