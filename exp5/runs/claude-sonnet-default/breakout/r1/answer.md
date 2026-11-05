Design: the policy tracks the ball with the paddle. Input channel 0 is the paddle and channel 3 is the ball (channel 4 is the trail, channel 2 the bricks), so I use those.

Hidden unit 0 in layer 1 computes tanh(1.5 * (ball_x - paddle_x)). Ball cells get weight 1.5*column in every row. The paddle cell on row 9 gets weight -1.5*column. The result is about 0 when the paddle is under the ball, and it saturates to +1 or -1 when the paddle is off by 1 or more columns.

Layer 2 unit 0 is a pass-through of that signal with some extra gain, tanh(1.5*h).

Output: left logit = -9*h and right logit = +9*h. Biases of 2.5 on no-op, up, down and fire make the paddle stay still with about 96% probability when it is aligned. When it is misaligned by 1 or more columns, it moves toward the ball with about 98% probability. The ball moves one column per step and the paddle moves one column per step, so the paddle can keep up. The catch window is 2 cells wide.

```edits
W1[3:600:60, 0] = 0
W1[9:600:60, 0] = 1.5
W1[15:600:60, 0] = 3
W1[21:600:60, 0] = 4.5
W1[27:600:60, 0] = 6
W1[33:600:60, 0] = 7.5
W1[39:600:60, 0] = 9
W1[45:600:60, 0] = 10.5
W1[51:600:60, 0] = 12
W1[57:600:60, 0] = 13.5
W1[546, 0] = -1.5
W1[552, 0] = -3
W1[558, 0] = -4.5
W1[564, 0] = -6
W1[570, 0] = -7.5
W1[576, 0] = -9
W1[582, 0] = -10.5
W1[588, 0] = -12
W1[594, 0] = -13.5
W2[0, 0] = 1.5
W3[0, 1] = -9
W3[0, 3] = 9
b3[0] = 2.5
b3[2] = 2.5
b3[4] = 2.5
b3[5] = 2.5
```
