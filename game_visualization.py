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

module for visualizing harmoniq using Pygame
"""
import pygame
import math
import pygame.gfxdraw
from question_state import QuestionState
from input_bridge import answer_queue
from PYGAME_CONSTANTS import *

pygame.init()

# Important global variables!!!!
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
current_question_state = QuestionState(
    question_text="Preparing first question...",
    yes_count=0,
    no_count=0
)
pending_question_state = None
ui_phase = "questioning"
can_accept_answer = True
balls = []
CLICK_COOLDOWN = 0.25  # (seconds)
last_click_time = 0.0
current_guess = ""

final_result_title = ""  # Deals with the ending of the game
final_result_subtitle = ""  # to make it look nice!

# Global variables/constants to handle the genie's dialogue
current_dialogue_text = "Welcome to Harmoniq!"
dialogue_queue = []
dialogue_timer = 0.0
DIALOGUE_DISPLAY_TIME = 2.75  # delay per genie message (seconds)
loading_pulse_time = 0.0


# Fonts (not in PYGAME_CONSTANTS to avoid importing pygame twice)
YESNO_LABELS_FONT = pygame.font.SysFont('Arial', 40)
IDK_LABELS_FONT = pygame.font.SysFont('Arial', 32)
SONG_COUNTS_FONT = pygame.font.SysFont('Arial', 20)
QUESTION_FONT = pygame.font.SysFont('Arial', 32)  # (Font type, font size)
DIALOGUE_FONT = pygame.font.SysFont("Arial", 24)
GUESS_BALL_FONT = pygame.font.SysFont("Arial", 22, bold=True)
END_TITLE_FONT = pygame.font.SysFont("Arial", 40, bold=True)
END_SUBTITLE_FONT = pygame.font.SysFont("Arial", 26)


##########################################################################################


class Ball:
    """
    Represents a visual ball object in our visualization of the Harmoniq program.
    """
    x: float
    y: float
    target_x: float
    target_y: float
    vy: float
    color: tuple[int, int, int]
    radius: float
    state: str = 'falling'
    pop_time: float = 0.0
    target_radius: float
    is_guess_ball: bool = False

    def __init__(self, x: float, y: float, target_x: float, target_y: float,
                 color: tuple[int, int, int], radius: float = 7.0):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.vy = 0
        self.color = color
        self.radius = radius
        self.target_radius = radius


def get_ball_positions(num_balls: int, rows: int | None = None,
                       radius: float = 7.0,
                       zone_height: float = 180.0) -> list[tuple[float, float]]:
    """
    Returns a list of the final resting coordinates (x,y) for each ball in our visualization.

    Method Argument Notes:
        - Zone in 'zone_height' refers to the area at the bottom
          of the pygame window in which the balls will live.

    Preconditions:
        - num_balls, radius, zone_height >= 0
        - rows >= 0 if isinstance(rows, int)

    """
    zone_bottom = WINDOW_HEIGHT - BOTTOM_MARGIN
    zone_top = zone_bottom - zone_height

    ball_positions = []

    # Automatically calculates the number of rows we need to accomodate the changing number of balls present.
    if rows is None:
        max_balls_per_row = math.floor((WINDOW_WIDTH - 40 + H_GAP) / (2 * radius + H_GAP))
        rows = max(1, math.ceil(num_balls / max_balls_per_row))

    balls_per_row = math.ceil(num_balls / rows)

    # Compute ball positions for each ball
    for ball_index in range(num_balls):
        row = ball_index // balls_per_row
        col = ball_index % balls_per_row

        # Number of balls in the current row, allows us to properly center each row
        row_count = min(balls_per_row, num_balls - row * balls_per_row)

        x_min = SIDE_MARGIN + radius
        x_max = WINDOW_WIDTH - SIDE_MARGIN - radius

        # Handles naturally spreading out the balls so that they actually fill up the rows
        if row_count == 1:
            target_x = WINDOW_WIDTH / 2
        else:
            dx_row = (x_max - x_min) / (row_count - 1)
            target_x = x_min + col * dx_row

        target_y = zone_top + (row + 0.5) * (zone_height / rows)

        ball_positions.append((target_x, target_y))

    return ball_positions


def start_guessing_phase() -> None:
    """
    Begins the visualization for the guessing phase of the game.
    """
    global balls

    if not balls:
        return

    # Clear the old guess ball so that it can pick a new one. Pop the old guess ball
    for ball in balls:
        if ball.is_guess_ball:
            ball.is_guess_ball = False
            ball.state = "popping"
            ball.pop_time = 0.0

    candidate_balls = [ball for ball in balls if ball.state != 'popping']
    if not candidate_balls:
        candidate_balls = balls  # Fallback but shouldnt happen

    # Pick a ball from the middle of the set
    candidate_balls.sort(key=lambda b: (b.target_y, b.target_x))
    guess_ball = candidate_balls[len(candidate_balls) // 2]

    guess_ball.is_guess_ball = True
    guess_ball.target_x, guess_ball.target_y = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 40
    guess_ball.target_radius = GUESS_BALL_FINAL_RADIUS
    guess_ball.state = "guessing"


def apply_guess_state(guess_text: str) -> None:
    """
    Handles non-first guesses in the guess phase
    """
    global ui_phase, current_guess, can_accept_answer, pending_question_state

    ui_phase = "guessing"
    current_guess = guess_text
    can_accept_answer = True
    pending_question_state = None

    for ball in balls:
        if ball.state != "popping":
            ball.color = PURPLE

    start_guessing_phase()


def update_ball(ball: Ball, dt: float) -> None:
    """
    Updates and animates the positions of ball according to change in time (dt)
    """

    if ball.state == "falling":
        # smooth x-direction movement driven towards target position
        ball.x += (ball.target_x - ball.x) * min(1.0, X_FOLLOW_SPEED * dt)

        # y-direction free-fall (physics woohoo)
        ball.vy += GRAVITY * dt
        ball.y += ball.vy * dt

        if ball.y >= ball.target_y:
            ball.y = ball.target_y
            ball.vy = 0

            # Ball is close enough to target position so we just fix its position
            if abs(ball.x - ball.target_x) < 0.5:
                ball.x = ball.target_x
                ball.state = "rest"

    elif ball.state == "guessing":
        ball.x += (ball.target_x - ball.x) * min(1.0, GUESS_X_FOLLOW_SPEED * dt)
        ball.y += (ball.target_y - ball.y) * min(1.0, GUESS_Y_FOLLOW_SPEED * dt)
        ball.radius += (ball.target_radius - ball.radius) * min(1.0, GUESS_RADIUS_FOLLOW_SPEED * dt)

        if (abs(ball.x - ball.target_x) < 0.5 and abs(ball.y - ball.target_y) < 0.5 and
                abs(ball.radius - ball.target_radius) < 0.5):

            ball.x = ball.target_x
            ball.y = ball.target_y
            ball.radius = ball.target_radius
            ball.state = "rest"

    elif ball.state == "popping":
        ball.pop_time += dt


def draw_ball(screen: pygame.Surface, ball: Ball) -> None:
    """
    Draws visual representation of ball on screen.
    """

    if ball.state == "popping":
        t = min(ball.pop_time / POP_DURATION, 1.0)
        cur_radius = max(1, int(ball.radius * (1 - t)))
    else:
        cur_radius = ball.radius

    pygame.gfxdraw.filled_circle(screen, int(ball.x), int(ball.y), int(cur_radius), ball.color)
    pygame.gfxdraw.aacircle(screen, int(ball.x), int(ball.y), int(cur_radius), ball.color)


def update_guess_visual(text: str) -> None:
    """
    Recieves input to set as the text in the guess visual.
    """
    global current_guess
    current_guess = text


def update_ball_colors(balls: list[Ball], num_yes: int, num_no: int) -> None:
    """
    Update the GREEN/RED color split of the balls based off how many remaining songs produce a 'yes'
    answer to the current question (num_yes) and how many songs produce a 'no' answer (num_no)
    """
    n_total = num_yes + num_no
    num_balls = len(balls)

    if n_total == 0 or num_balls == 0:
        return

    # Formula for number of total 'no' balls we need based off number of remaining songs
    balls_no = max(0, min(num_balls, round(num_balls * num_no / n_total)))

    # sorts the balls left-to-right by their target x position so we could split color down the middle.
    balls_sorted = sorted(balls, key=lambda b: b.target_x)

    for ball_index, cur_ball in enumerate(balls_sorted):
        if ball_index < balls_no:
            cur_ball.color = RED
        else:
            cur_ball.color = GREEN


def sync_ball_count(desired_count: int) -> None:
    """
    Fix possible errors of the number of balls on the screen.
    For example, we might have one ball remaining but it represents many songs which
    is both misleading and visually weird.
    """
    if desired_count < 0:
        return

    global balls

    cur_ball_count = len(balls)

    if cur_ball_count == desired_count:
        return

    # Remove extra balls if too many balls
    elif cur_ball_count > desired_count:
        balls.sort(key=lambda b: (b.target_y, b.target_x))
        balls = balls[:desired_count]

    # Add extra balls if too little balls
    else:
        to_add = desired_count - cur_ball_count

        # Add the new balls
        for i in range(to_add):
            start_y = -40 - (i % 20) * 12

            new_ball = Ball(WINDOW_WIDTH / 2, start_y, WINDOW_WIDTH / 2, -40 - (i % 20) * 12, GRAY, MIN_BALL_RADIUS)
            balls.append(new_ball)

    # now we repack the balls together!
    repack_remaining_balls(balls)


def pop_balls(balls: list[Ball], answer: str) -> None:
    """ Send appropriate balls to the popping animation based on the user's answer to the current
    question.

    Preconditions:
        - answer in {'yes', 'no', 'i dont know'}
    """
    if answer == 'i dont know':
        return
    elif answer == 'yes':
        pop_color = RED
    else:
        pop_color = GREEN

    for ball in balls:
        if ball.color == pop_color:
            ball.state = "popping"
            ball.pop_time = 0.0


def repack_remaining_balls(balls: list[Ball]) -> None:
    """
    Reposition the remaining balls after some balls have been popped
    into a natural 'gravitational'-based position.
    Also sort (mutate) balls list by balls' target positions so that we can reposition them without
    unnatural cross-over.
    """
    if balls == []:
        return

    new_radius, new_rows = get_layout_params(len(balls))
    balls.sort(key=lambda ball: (ball.target_y, ball.target_x))

    new_positions = get_ball_positions(len(balls), rows=new_rows, radius=new_radius)

    for b, (new_target_x, new_target_y) in zip(balls, new_positions):
        if b.is_guess_ball:
            continue
        b.target_x = new_target_x
        b.target_y = new_target_y
        b.vy = 0.0
        b.radius = new_radius
        b.state = "falling"


def calculate_new_ball_radius(num_balls: int) -> int:
    """
    Calculate the new radius we need for all the balls to keep the visualization good-looking.
    """
    # If we have one ball left we want it as large as possible
    if num_balls <= 1:
        return MAX_BALL_RADIUS

    # % of current number of balls / starting number of balls
    t = (num_balls - 1) / (STARTING_NUM_BALLS - 1)

    recommended_radius = round(MAX_BALL_RADIUS - t * (MAX_BALL_RADIUS - MIN_BALL_RADIUS))

    return max(MIN_BALL_RADIUS, min(MAX_BALL_RADIUS, recommended_radius))


def get_layout_params(num_balls: int, zone_height: int = 180) -> tuple[int, int]:
    """
    Optimizes the best ball radius to use by returning a tuple.
    The first element is the largest ball radius we can have which fits our ball-area constraints
    without any balls overlapping.
    The second element is the number of rows we need to arrange the balls in to accomodate this
    radius.
    """
    # Only one song left so we just use the maximum radius available
    if num_balls <= 1:
        return MAX_BALL_RADIUS, 1

    # Tries each radius (from biggest to smallest) until it optimizes it to one that does not overlap balls.
    for radius in range(MAX_BALL_RADIUS, MIN_BALL_RADIUS - 1, -1):
        # Total horizontal distance/interval we have for ball centers
        center_span = WINDOW_WIDTH - 2 * SIDE_MARGIN - 2 * radius

        # Estimate how much 'space' (and therefore balls) can fit in a row.
        max_per_row = max(1, math.floor(center_span / (2 * radius + H_GAP)) + 1)
        rows = math.ceil(num_balls / max_per_row)

        # Computes distance between row vertical centers
        row_step = zone_height / rows

        # Computes whether rows will overlap vertically (bad)
        # If not, then we have found optimal radius & row number. If yes then we keep searching.
        if row_step >= 2 * radius + V_GAP:
            return radius, rows

    # If none of the radii guarantee zero overlap we just use the minimum radius
    print("ALL RADII RESULT IN BALL OVERLAP. CONSIDER LOWERING MIN_BALL_RADIUS AND MAX_BALL_RADIUS CONSTRAINTS")
    radius = MIN_BALL_RADIUS
    center_span = WINDOW_WIDTH - 2 * SIDE_MARGIN - 2 * radius
    max_per_row = max(1, math.floor(center_span / (2 * radius + H_GAP)) + 1)
    rows = math.ceil(num_balls / max_per_row)
    return radius, rows


def get_ui_components() -> dict[str, pygame.Rect]:
    """
    Create and return a mapping to the interactive geometric UI components of the pygame (buttons, labels)
    """

    return {
        "dialogue": pygame.Rect(DIALOGUE_RECT_X, DIALOGUE_RECT_Y,
                                DIALOGUE_RECT_WIDTH, DIALOGUE_RECT_HEIGHT),
        "question": pygame.Rect(round(QUESTION_BOX_CENTER_X - QUESTION_NODE_WIDTH / 2),
                                QUESTION_BOX_TOP, QUESTION_NODE_WIDTH, QUESTION_NODE_HEIGHT),
        "no": pygame.Rect(round(NO_NODE_POSITION[0]),  # - ANSWER_NODE_WIDTH/2),
                          round(NO_NODE_POSITION[1]),  # + ANSWER_NODE_HEIGHT/2),
                          ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT),
        "idk": pygame.Rect(round(IDK_NODE_POSITION[0]),  # - ANSWER_NODE_WIDTH/2),
                           round(IDK_NODE_POSITION[1]),  # + ANSWER_NODE_HEIGHT/2),
                           ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT),
        "yes": pygame.Rect(round(YES_NODE_POSITION[0]),  # - ANSWER_NODE_WIDTH/2),
                           round(YES_NODE_POSITION[1]),  # + ANSWER_NODE_HEIGHT/2),
                           ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT),
    }


def draw_wrapped_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                      color: tuple, rect: pygame.Rect, padding: int = 10) -> None:
    """Draw text wrapped to fit within rect, vertically centered.

    Preconditions:
        - rect is the bounding rectangle to wrap the text within.
        - padding is the horizontal padding (in pixels) to add on each side.
    """
    words = text.split()
    lines = []
    current_line = []
    max_width = rect.width - padding * 2

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    line_height = font.get_linesize()
    total_height = len(lines) * line_height

    # Vertically centre the block of text within the rect
    y = rect.centery - total_height // 2

    for line in lines:
        line_surface = font.render(line, True, color)
        x = rect.centerx - line_surface.get_width() // 2
        surface.blit(line_surface, (x, y))
        y += line_height


def draw_ui(screen: pygame.Surface, question_text: str, no_count: int, yes_count: int,
            question_border_color: tuple[int, int, int]) -> None:
    """
    Draw the Question/Answer tree structure on the pygame window.
    """

    ui_components = get_ui_components()
    draw_tree_branches(screen, ui_components)

    display_question = question_text if ui_phase == "questioning" else "Is this your song?"

    # Hover Highlighters
    mouse_pos = pygame.mouse.get_pos()

    yes_hovered = ui_components["yes"].collidepoint(mouse_pos)
    no_hovered = ui_components["no"].collidepoint(mouse_pos)
    idk_hovered = ui_components["idk"].collidepoint(mouse_pos)

    # Dialogue Rectangle
    dialogue_rect = ui_components['dialogue']

    dialogue_shadow = dialogue_rect.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, DIALOGUE_SHADOW_COLOR, dialogue_shadow, border_radius=RECT_BORDER_RADIUS)

    pygame.draw.rect(screen, DIALOGUE_FILL_COLOR, dialogue_rect, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, PURPLE, dialogue_rect, width=2, border_radius=RECT_BORDER_RADIUS)

    draw_wrapped_text(screen, "Harmoniq: " + current_dialogue_text,
                      DIALOGUE_FONT, BLACK, dialogue_rect, padding=15)

    # Question Rectangle
    question_rectangle = ui_components['question']
    question_shadow = question_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, question_border_color, question_shadow, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, question_border_color, question_shadow, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, question_border_color, question_rectangle, width=3, border_radius=RECT_BORDER_RADIUS)

    # Draw wrapped text instead of single-line render
    draw_wrapped_text(screen, display_question, QUESTION_FONT, BLACK, question_rectangle)

    # 'I dont know' rectangle (Button/Interactive) + highlights cover for the button when its hovered over
    if ui_phase == 'questioning':
        idk_rectangle = ui_components['idk']
        idk_surface = IDK_LABELS_FONT.render("I dont know", True, PURPLE)
        idk_text_rect = idk_surface.get_rect(center=idk_rectangle.center)

        idk_shadow = idk_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
        pygame.draw.rect(screen, PURPLE, idk_shadow, border_radius=RECT_BORDER_RADIUS)

        idk_fill = HOVER_RECT_FILL_COLOR if idk_hovered else DEFAULT_RECT_FILL_COLOR
        idk_border_width = HOVER_BORDER_WIDTH if idk_hovered else NORMAL_BORDER_WIDTH

        pygame.draw.rect(screen, idk_fill, idk_rectangle, border_radius=RECT_BORDER_RADIUS)
        pygame.draw.rect(screen, PURPLE, idk_rectangle, width=idk_border_width, border_radius=RECT_BORDER_RADIUS)
        screen.blit(idk_surface, idk_text_rect)

    # Yes/No Rectangles (Button/Interactive) + highlights cover for the buttons when theyre hovered over
    yes_rectangle = ui_components['yes']
    no_rectangle = ui_components['no']

    yes_surface = YESNO_LABELS_FONT.render("Yes", True, GREEN)
    no_surface = YESNO_LABELS_FONT.render("No", True, RED)

    yes_text_rect = yes_surface.get_rect()
    no_text_rect = no_surface.get_rect()
    yes_text_rect.centerx = yes_rectangle.centerx
    no_text_rect.centerx = no_rectangle.centerx
    yes_text_rect.top = yes_rectangle.top + 25
    no_text_rect.top = no_rectangle.top + 25

    yes_shadow = yes_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, GREEN, yes_shadow, border_radius=RECT_BORDER_RADIUS)

    no_shadow = no_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, RED, no_shadow, border_radius=RECT_BORDER_RADIUS)

    yes_fill = HOVER_RECT_FILL_COLOR if yes_hovered else DEFAULT_RECT_FILL_COLOR
    yes_border_width = HOVER_BORDER_WIDTH if yes_hovered else NORMAL_BORDER_WIDTH

    pygame.draw.rect(screen, yes_fill, yes_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, GREEN, yes_rectangle, width=yes_border_width, border_radius=RECT_BORDER_RADIUS)

    no_fill = HOVER_RECT_FILL_COLOR if no_hovered else DEFAULT_RECT_FILL_COLOR
    no_border_width = HOVER_BORDER_WIDTH if no_hovered else NORMAL_BORDER_WIDTH

    pygame.draw.rect(screen, no_fill, no_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, RED, no_rectangle, width=no_border_width, border_radius=RECT_BORDER_RADIUS)

    screen.blit(yes_surface, yes_text_rect)
    screen.blit(no_surface, no_text_rect)

    # Yes / No counts
    if ui_phase == 'questioning' and yes_count + no_count > 0:

        yes_count_surface = SONG_COUNTS_FONT.render(f"{yes_count:,} songs", True, BLACK)
        no_count_surface = SONG_COUNTS_FONT.render(f"{no_count:,} songs", True, BLACK)

        yes_count_rect = yes_count_surface.get_rect()
        no_count_rect = no_count_surface.get_rect()

        yes_count_rect.centerx = yes_rectangle.centerx
        no_count_rect.centerx = no_rectangle.centerx

        yes_count_rect.bottom = yes_rectangle.bottom - 18
        no_count_rect.bottom = no_rectangle.bottom - 18

        screen.blit(yes_count_surface, yes_count_rect)
        screen.blit(no_count_surface, no_count_rect)

    if ui_phase in {"success", "failure"}:
        draw_end_of_game(screen)


def draw_tree_branches(screen: pygame.Surface, ui_components: dict[str, pygame.Rect]) -> None:
    """
    Draws branches between question boxes to create a tree-like structure.
    """
    question_rect = ui_components["question"]

    # Begin subtree branches at the bottom middle of the question box
    root_x, root_y = question_rect.midbottom

    # Draw straight down a bit
    stem_length = 9
    branch_y = root_y + stem_length
    pygame.draw.line(screen, TREE_LINE_COLOR, (root_x, root_y), (root_x, branch_y),
                     TREE_LINE_WIDTH)

    # build child_keys based off of the current phase of the game
    # so we know if 'idk' box is present
    child_keys = ["no", "yes"]
    if ui_phase == "questioning":
        child_keys = ["no", "idk", "yes"]

    child_rects = [ui_components[key] for key in child_keys]

    # Create a horizontal bar for the 'subtree' boxes that spans above the answer boxes
    left_x = child_rects[0].centerx
    right_x = child_rects[-1].centerx

    pygame.draw.line(screen, TREE_LINE_COLOR, (left_x, branch_y), (right_x, branch_y),
                     TREE_LINE_WIDTH)

    # Draw vertical lines to connect each answer box to the horizontal bar above
    for rect in child_rects:
        pygame.draw.line(screen, TREE_LINE_COLOR, (rect.centerx, branch_y), (rect.centerx, rect.top),
                         TREE_LINE_WIDTH)


def draw_funnel_to_balls(screen: pygame.Surface, answer_rect: pygame.Rect, cluster_balls: list[Ball],
                         color: tuple[int, int, int]) -> None:
    """
    Draw a funnel-like visual from the yes node and no node to the yes balls and no balls, respectively.
    Visualizes the tree like structure of the set of songs each answer choice leads to.
    """
    if not cluster_balls:
        return

    # Starting position of the desired funnel stem
    start_x, start_y = answer_rect.midbottom
    neck_x, neck_y = start_x, start_y + FUNNEL_STEM_LENGTH

    # The balls cluster's span
    left_x = min(ball.x - ball.radius for ball in cluster_balls) - FUNNEL_X_PAD
    right_x = max(ball.x + ball.radius for ball in cluster_balls) + FUNNEL_X_PAD
    top_y = min(ball.y - ball.radius for ball in cluster_balls) - FUNNEL_Y_PAD

    # Compute funnel dimensions using above computations and draw the funnel
    funnel_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(funnel_surface, (*color, FUNNEL_ALPHA),
                        [(neck_x, neck_y), (right_x, top_y), (left_x, top_y)])
    screen.blit(funnel_surface, (0, 0))

    # Draw the stem of the funnel and its outline
    pygame.draw.line(screen, color, (start_x, start_y), (neck_x, neck_y), TREE_LINE_WIDTH)
    pygame.draw.line(screen, color, (neck_x, neck_y), (left_x, top_y), FUNNEL_OUTLINE_WIDTH)
    pygame.draw.line(screen, color, (neck_x, neck_y), (right_x, top_y), FUNNEL_OUTLINE_WIDTH)


def draw_answer_funnels(screen: pygame.Surface, ui_components: dict[str, pygame.Rect]) -> None:
    """
    Helper method to handle drawing funnels to both answer ball choices.
    """
    if ui_phase != "questioning":
        return

    red_balls = [ball for ball in balls if ball.color == RED and ball.state != "popping"]
    green_balls = [ball for ball in balls if ball.color == GREEN and ball.state != "popping"]

    draw_funnel_to_balls(screen, ui_components["no"], red_balls, RED)
    draw_funnel_to_balls(screen, ui_components["yes"], green_balls, GREEN)


def draw_end_of_game(screen: pygame.Surface) -> None:
    """
    Draws the visuals for the end of the game (harmoniq has either failed or succeeded at guessing).

    Preconditions:
        - ui_phase in {"success", "failure"}
    """

    # Darkens the screen
    overlay_background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay_background, (0, 0, 0, END_OVERLAY_ALPHA), overlay_background.get_rect())
    screen.blit(overlay_background, (0, 0))

    # Draws an end result card at the center of the screen
    card_rect = pygame.Rect(0, 0, END_CARD_WIDTH, END_CARD_HEIGHT)
    card_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    border_color = GREEN if ui_phase == "success" else RED

    pygame.draw.rect(screen, END_CARD_FILL_COLOR, card_rect, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, border_color, card_rect, width=END_CARD_BORDER_WIDTH, border_radius=RECT_BORDER_RADIUS)

    title_surface = END_TITLE_FONT.render(final_result_title, True, BLACK)
    title_rect = title_surface.get_rect(center=(card_rect.centerx, card_rect.top + 70))
    screen.blit(title_surface, title_rect)

    subtitle_rect = pygame.Rect(card_rect.left + 20, card_rect.top + 105,
                                card_rect.width - 40, 60)
    draw_wrapped_text(screen, final_result_subtitle, END_SUBTITLE_FONT, BLACK, subtitle_rect)


def initiate_final_result(success: bool, subtitle: str) -> None:
    """
    Activate and draw the final result visuals after the game has concluded.
    Meant to be called in main.py
    """
    global ui_phase, final_result_title, final_result_subtitle, can_accept_answer

    ui_phase = "success" if success else "failure"
    final_result_title = "I got it!" if success else "I couldn't guess it."
    final_result_subtitle = subtitle
    can_accept_answer = False


def set_question_state(state: QuestionState) -> None:
    """
    Update the global pending_question_state variable
    """
    global pending_question_state
    pending_question_state = state


def apply_question_state_visuals(state: QuestionState) -> None:
    """
    Apply the visuals of the current pending_question_state to the pygame window
    and update current_question_state accordingly.
    """
    global current_question_state, balls, can_accept_answer

    if state.question_text == '':
        state.question_text = current_question_state.question_text if current_question_state else ''

    current_question_state = state

    # If we have less songs that the starting ball number (STARTING_NUM_BALLS) then we can represent
    # each song as an individual ball!
    desired_ball_count = min(STARTING_NUM_BALLS, state.yes_count + state.no_count)
    sync_ball_count(desired_ball_count)
    update_ball_colors(balls, state.yes_count, state.no_count)

    can_accept_answer = True


def queue_dialogue_text(text: str) -> None:
    """
    Add text to the current dialogue queue. Use in main.py when genie has dialogue to display.
    """
    global dialogue_queue
    dialogue_queue.append(text)


def update_dialogue(dt: float) -> None:
    """
    Update current_dialogue_text based on the current queue of dialogue.
    """
    global current_dialogue_text, dialogue_timer, dialogue_queue

    if dialogue_timer > 0:
        dialogue_timer -= dt
    elif dialogue_queue:  # dialogue_timer <= 0 is implied (since first if condition failed)
        current_dialogue_text = dialogue_queue.pop(0)
        dialogue_timer = DIALOGUE_DISPLAY_TIME

##############################################


def run_pygame() -> None:
    """
    Run this file.
    """

    global pending_question_state, balls, can_accept_answer, last_click_time, loading_pulse_time
    initial_ball_radius, initial_row_number = get_layout_params(STARTING_NUM_BALLS)
    positions = get_ball_positions(STARTING_NUM_BALLS, rows=initial_row_number, radius=initial_ball_radius)

    # Draw all the balls in initially
    for i, (target_x, target_y) in enumerate(positions):
        start_y = -40 - (i % 20) * 12
        ball = Ball(x=target_x, y=start_y, target_x=target_x, target_y=target_y,
                    color=GRAY, radius=initial_ball_radius)
        balls.append(ball)

    running = True

    while running:
        dt = clock.tick(60) / 1000
        update_dialogue(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = event.pos
                ui_components = get_ui_components()
                now = pygame.time.get_ticks() / 1000

                if (can_accept_answer and (now - last_click_time >= CLICK_COOLDOWN)
                        and all(ball.state == 'rest' for ball in balls)):
                    if ui_components['yes'].collidepoint(mouse_position):
                        answer_queue.put(('yes', 'pygame'))
                        if ui_phase == 'questioning':
                            pop_balls(balls, 'yes')
                        can_accept_answer = False
                        last_click_time = now

                    elif ui_components['no'].collidepoint(mouse_position):
                        answer_queue.put(('no', 'pygame'))
                        if ui_phase == 'questioning':
                            pop_balls(balls, 'no')
                        can_accept_answer = False
                        last_click_time = now

                    elif ui_components['idk'].collidepoint(mouse_position) and ui_phase == 'questioning':
                        answer_queue.put(('idk', 'pygame'))
                        can_accept_answer = False
                        last_click_time = now

        for ball in balls:
            update_ball(ball, dt)

        old_ball_count = len(balls)
        balls = [ball for ball in balls if not (ball.state == "popping" and ball.pop_time >= POP_DURATION)]

        # If balls were popped out, we repack the remaining balls and sort the balls list
        if old_ball_count != len(balls):
            repack_remaining_balls(balls)

        if pending_question_state is not None and all(ball.state == 'rest' for ball in balls):
            apply_question_state_visuals(pending_question_state)
            pending_question_state = None

        screen.fill((25, 25, 25))

        draw_answer_funnels(screen, get_ui_components())

        for ball in balls:
            draw_ball(screen, ball)
            if ball.is_guess_ball and ball.radius > 40:
                font_size = max(12, int(ball.radius * 0.18))
                guess_font = pygame.font.SysFont("Arial", font_size, bold=True)
                guess_rect = pygame.Rect(0, 0, int(ball.radius * 1.6), int(ball.radius * 1.6))
                guess_rect.center = (int(ball.x), int(ball.y))
                draw_wrapped_text(screen, current_guess, guess_font, WHITE, guess_rect)

        loading_pulse_time += dt
        if current_question_state.yes_count + current_question_state.no_count == 0:
            pulse = int(120 + 127 * math.sin(loading_pulse_time * 3))
            loading_color = (pulse, 0, pulse)  # pulsing purple
        else:
            loading_color = PURPLE
        draw_ui(screen, current_question_state.question_text, current_question_state.no_count,
                current_question_state.yes_count, loading_color)

        pygame.display.flip()

    pygame.quit()
