"""
Harmoniq - Song Guessing Engine

Copyright (c) 2026 Adam Ahmed, Omer Sheaffer. All rights reserved.

This software and all associated documentation files (the "Software") are the property of the copyright holder.
No part of this Software may be reproduced, transmitted, distributed, modified, or otherwise used, in whole or in part,
in any form or by any means, whether electronic, mechanical, photocopying, recording, or otherwise, without the prior
express written permission of the copyright holder.

The unauthorized use, copying, or distribution of this Software is strictly prohibited and may result in civil and/or
criminal penalties under applicable law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE
LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module containing constants used for the visualization of harmoniq in game_visualization
"""

# Pygame window constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
SIDE_MARGIN = 30  # margin to leave between the side of the pygame window and the edge of the area where balls are
BOTTOM_MARGIN = 20  # margin to leave between bottom of the pygame window and edge of area where balls are

# Question/Answer UI constant attributes
QUESTION_BOX_CENTER_X = WINDOW_WIDTH // 2
QUESTION_BOX_CENTER_Y = 5

# (RGB values)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

##############################
NO_NODE_POSITION = (140, 220)   # ALL OF THESE COORDINATES
IDK_NODE_POSITION = (490, 220)  # REFER TO THE POSITION OF THE
YES_NODE_POSITION = (840, 220)  # TOP LEFT CORNER OF THE NODE
##############################

QUESTION_NODE_WIDTH = 350
ANSWER_NODE_WIDTH = 200
QUESTION_NODE_HEIGHT = 130
ANSWER_NODE_HEIGHT = 150

NODE_SHADOW_OFFSET = 4
QUESTION_BOX_TOP = 75
RECT_BORDER_RADIUS = 17
DEFAULT_RECT_FILL_COLOR = (210, 210, 210)

HOVER_RECT_FILL_COLOR = (235, 235, 235)
NORMAL_BORDER_WIDTH = 3
HOVER_BORDER_WIDTH = 5

# Tree 'structural' components (connectors to make visuals look like a tree)
TREE_LINE_COLOR = WHITE
TREE_LINE_WIDTH = 5
FUNNEL_ALPHA = 45
FUNNEL_STEM_LENGTH = 18
FUNNEL_X_PAD = 10
FUNNEL_Y_PAD = 8
FUNNEL_OUTLINE_WIDTH = 2


# Program Dialogue constants
DIALOGUE_FILL_COLOR = (245, 245, 245)
DIALOGUE_SHADOW_COLOR = (180, 180, 180)
DIALOGUE_RECT_X = 140
DIALOGUE_RECT_Y = 15
DIALOGUE_RECT_WIDTH = 920
DIALOGUE_RECT_HEIGHT = 45

# Ball-related Constants
STARTING_NUM_BALLS = 250
MIN_BALL_RADIUS = 7  # (pixels)
MAX_BALL_RADIUS = 30
H_GAP = 4  # Horizontal gap between neighbouring balls
V_GAP = 6  # Vertical gap between neighbouring balls
GUESS_X_FOLLOW_SPEED = 4.0
GUESS_Y_FOLLOW_SPEED = 4.0
GUESS_RADIUS_FOLLOW_SPEED = 4.0  # Speeds at which the ball grows and moves in guessing phase
GUESS_BALL_FINAL_RADIUS = 150

# End of game visual constants
END_OVERLAY_ALPHA = 140
END_CARD_WIDTH = 520
END_CARD_HEIGHT = 220
END_CARD_FILL_COLOR = (245, 245, 245)
END_CARD_BORDER_WIDTH = 4

# Physical constants for animation
GRAVITY = 1800  # Gravity Acceleration constant (in pixels / sec^2) for animating the balls
POP_DURATION = 0.15  # How quickly a ball 'pops' in the animation (seconds)
X_FOLLOW_SPEED = 10.0
