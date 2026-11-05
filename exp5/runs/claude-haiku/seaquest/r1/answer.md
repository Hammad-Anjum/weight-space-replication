Design (hand-set, no training).

Position encoding: for row r, the two sub cells sit at columns s-1, s (facing right) or s, s+1 (facing left). A column-weighted sum over channel 0 therefore gives the sub's column up to a half-cell offset, so "enemy column minus sub column" is linear in the inputs.

Layer 1 (32 units):
- Units 0-7 (RR, row r = unit+1): tanh(3*(e - s') ) when the sub is in row r and an enemy or diver (channel 2) is in row r. Positive only when the object is to the right of the sub. Sub absent, or no object in the row, gives a negative value.
- Units 8-15 (RL, row r = unit-7): the mirror image, positive when the object is to the left.
- Unit 16: oxygen below 20 (gauge column 0 of row 9, channel 5, empty).
- Unit 17: at least one diver aboard (gauge column 8 of row 9, channel 5). This is only read together with unit 16, because the oxygen bar can also light column 8 when oxygen is high.
- Unit 18: vertical signal, 2*(sum over objects of (row - 4.5)) - 2*(sub row - 4.5). With one object it is 2*(object row - sub row). With none it pulls the sub toward row 4-5. It keeps the sub away from row 0 when it carries no divers.
- Units 19-31: unused (zero).

Layer 2 (5 units used):
- h2_0: OR of all RR and RL units (something is in the sub's row).
- h2_1: OR of RR units (object on the right). h2_2: OR of RL units (object on the left).
- h2_3: AND of units 16 and 17 (oxygen low and carrying a diver), so surfacing is needed.
- h2_4: sign of unit 18, passed through with gain 3.

Output: fire = 4*h2_0 (fire whenever aligned, bullets fly on and reach distant targets). Right = 1.5*h2_1, left = 1.5*h2_2 (weak, so turning happens stochastically, since facing is not observable). Up = 3*h2_3 - 1.5*h2_4. Down = 1.5*h2_4. Noop = 0.

Expected behaviour: hovers near rows 4-5, moves vertically toward enemies and divers, fires when aligned, climbs to surface when oxygen is low and a diver is aboard. Limitations: no dodging, weak diver collection, turning is stochastic, and facing cannot be read directly. I could not verify the score numerically; expect a modest score.

```edits
# Layer 1 RR units 0-7: object ahead on the right in row r (unit = r-1)
W1[60:120:6, 0] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[62:120:6, 0] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[0] = -28
W1[120:180:6, 1] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[122:180:6, 1] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[1] = -28
W1[180:240:6, 2] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[182:240:6, 2] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[2] = -28
W1[240:300:6, 3] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[242:300:6, 3] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[3] = -28
W1[300:360:6, 4] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[302:360:6, 4] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[4] = -28
W1[360:420:6, 5] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[362:420:6, 5] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[5] = -28
W1[420:480:6, 6] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[422:480:6, 6] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[6] = -28
W1[480:540:6, 7] = [14, 12.5, 11, 9.5, 8, 6.5, 5, 3.5, 2, 0.5]
W1[482:540:6, 7] = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27]
b1[7] = -28
# Layer 1 RL units 8-15: object ahead on the left in row r (unit = r+7)
W1[60:120:6, 8] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[62:120:6, 8] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[8] = -30
W1[120:180:6, 9] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[122:180:6, 9] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[9] = -30
W1[180:240:6, 10] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[182:240:6, 10] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[10] = -30
W1[240:300:6, 11] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[242:300:6, 11] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[11] = -30
W1[300:360:6, 12] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[302:360:6, 12] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[12] = -30
W1[360:420:6, 13] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[362:420:6, 13] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[13] = -30
W1[420:480:6, 14] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[422:480:6, 14] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[14] = -30
W1[480:540:6, 15] = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 12, 13.5]
W1[482:540:6, 15] = [30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
b1[15] = -30
# Layer 1 unit 16: oxygen below 20 (row 9, column 0, channel 5 empty)
W1[545, 16] = -6
b1[16] = 3
# Layer 1 unit 17: at least one diver aboard (row 9, column 8, channel 5 lit)
W1[593, 17] = 6
b1[17] = -3
# Layer 1 unit 18: vertical signal, channel 2 weight 2*(row-4.5), channel 0 weight (4.5-row)
W1[2:60:6, 18] = -9
W1[62:120:6, 18] = -7
W1[122:180:6, 18] = -5
W1[182:240:6, 18] = -3
W1[242:300:6, 18] = -1
W1[302:360:6, 18] = 1
W1[362:420:6, 18] = 3
W1[422:480:6, 18] = 5
W1[482:540:6, 18] = 7
W1[542:600:6, 18] = 9
W1[0:60:6, 18] = 4.5
W1[60:120:6, 18] = 3.5
W1[120:180:6, 18] = 2.5
W1[180:240:6, 18] = 1.5
W1[240:300:6, 18] = 0.5
W1[300:360:6, 18] = -0.5
W1[360:420:6, 18] = -1.5
W1[420:480:6, 18] = -2.5
W1[480:540:6, 18] = -3.5
W1[540:600:6, 18] = -4.5
# Layer 2
W2[0:16, 0] = 3
b2[0] = 45
W2[0:8, 1] = 3
b2[1] = 21
W2[8:16, 2] = 3
b2[2] = 21
W2[16, 3] = 3
W2[17, 3] = 3
b2[3] = -4.5
W2[18, 4] = 3
# Output (actions: 0 noop, 1 left, 2 up, 3 right, 4 down, 5 fire)
W3[0, 5] = 4
W3[1, 3] = 1.5
W3[2, 1] = 1.5
W3[3, 2] = 3
W3[4, 4] = 1.5
W3[4, 2] = -1.5
```
