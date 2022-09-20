# pytris
Tetris clone in pygame

![demo](demo.gif)

### How to play
- First set `conf.set_screen` in `if __name__ == "__main__"` section according to your need.
- Use left or right arrow key to move. up arrow key to rotate clockwise. down arrow key to speed up the fall.
- use `a` key to rotate counter clockwise and `s` key to rotate clockwise.
- `c` key to change color
- press down arrow to start a game again.
- Currently game start at level 5, change it by change `conf.starting_speed`.
- Level increase after every 5000 score.

### TODO
- ~Add comments~
- ~Clean up and optimize the code~ Partially done.
- **Implement kick system for rotation (now this feature is missing)** PR is welcome. Get Idea from here https://tetris.wiki/Super_Rotation_System
- Add an UI system to configure config in game.
- Add better mechanism to change theme.
- Add better mechanism to change level.
- add sound.
