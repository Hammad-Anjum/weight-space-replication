The first-layer units encode the ball’s horizontal position, paddle position, ball height, and horizontal travel direction; the direction feature corrects for wall bounces. The second layer predicts the ball’s projected bottom-row intercept for left- and right-moving trajectories, activating the matching estimate. The outputs move the paddle toward that intercept and favor no-op when aligned. The projection is deliberately simple and is recomputed each step.

```edits
# Ball x, centered and scaled
W1[3:600:60, 0] = -0.45
W1[9:600:60, 0] = -0.35
W1[15:600:60, 0] = -0.25
W1[21:600:60, 0] = -0.15
W1[27:600:60, 0] = -0.05
W1[33:600:60, 0] = 0.05
W1[39:600:60, 0] = 0.15
W1[45:600:60, 0] = 0.25
W1[51:600:60, 0] = 0.35
W1[57:600:60, 0] = 0.45

# Paddle x, centered and scaled
W1[540, 1] = -0.45
W1[546, 1] = -0.35
W1[552, 1] = -0.25
W1[558, 1] = -0.15
W1[564, 1] = -0.05
W1[570, 1] = 0.05
W1[576, 1] = 0.15
W1[582, 1] = 0.25
W1[588, 1] = 0.35
W1[594, 1] = 0.45

# Ball y, centered and scaled
W1[3:60:6, 2] = -0.45
W1[63:120:6, 2] = -0.35
W1[123:180:6, 2] = -0.25
W1[183:240:6, 2] = -0.15
W1[243:300:6, 2] = -0.05
W1[303:360:6, 2] = 0.05
W1[363:420:6, 2] = 0.15
W1[423:480:6, 2] = 0.25
W1[483:540:6, 2] = 0.35
W1[543:600:6, 2] = 0.45

# Horizontal direction: current ball x minus trail x, with wall correction
W1[3:600:60, 3] = 2
W1[9:600:60, 3] = 1
W1[15:600:60, 3] = 2
W1[21:600:60, 3] = 3
W1[27:600:60, 3] = 4
W1[33:600:60, 3] = 5
W1[39:600:60, 3] = 6
W1[45:600:60, 3] = 7
W1[51:600:60, 3] = 8
W1[57:600:60, 3] = 7
W1[10:600:60, 3] = -1
W1[16:600:60, 3] = -2
W1[22:600:60, 3] = -3
W1[28:600:60, 3] = -4
W1[34:600:60, 3] = -5
W1[40:600:60, 3] = -6
W1[46:600:60, 3] = -7
W1[52:600:60, 3] = -8
W1[58:600:60, 3] = -9

# Rightward and leftward projected-intercept features
W2[0, 0] = 2
W2[1, 0] = -2
W2[2, 0] = -2
W2[3, 0] = 10
b2[0] = -6.72
W2[0, 1] = 2
W2[1, 1] = -2
W2[2, 1] = 2
W2[3, 1] = -10
b2[1] = -8.52

# Paddle actions respond to either active intercept estimate
W3[0:2, 1] = -20
W3[0:2, 3] = 20
b3[0] = 2
b3[1] = -20
b3[2] = -4
b3[3] = 20
b3[4] = -4
b3[5] = -4
```