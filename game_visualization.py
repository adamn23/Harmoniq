
import pygame
import math
import pygame.gfxdraw

pygame.init()

# Pygame window constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
SIDE_MARGIN = 30  # margin to leave between the side of the pygame window and the edge of the area where balls are
BOTTOM_MARGIN = 20  # margin to leave between bottom of the pygame window and edge of area where balls are

# Question/Answer UI constant attributes
QUESTION_BOX_CENTER_X = WINDOW_WIDTH // 2
QUESTION_BOX_CENTER_Y = 5
NO_NODE_POSITION = (250, 140)
IDK_NODE_POSITION = (600, 140)
YES_NODE_POSITION = (950, 140)
QUESTION_NODE_WIDTH = 350
ANSWER_NODE_WIDTH = 200
QUESTION_NODE_HEIGHT = 100
ANSWER_NODE_HEIGHT = 150
YESNO_LABELS_FONT = pygame.font.SysFont('Arial', 40)
IDK_LABELS_FONT = pygame.font.SysFont('Arial', 32)
SONG_COUNTS_FONT = pygame.font.SysFont('Arial', 20)
QUESTION_FONT = pygame.font.SysFont('Arial', 32)  # (Font type, font size)
NODE_SHADOW_OFFSET = 4
QUESTION_BOX_TOP = 75
RECT_BORDER_RADIUS = 17
DEFAULT_RECT_FILL_COLOR = (210, 210, 210)

# Program Dialogue constants
DIALOGUE_FONT = pygame.font.SysFont("Arial", 24)
DIALOGUE_FILL_COLOR = (245, 245, 245)
DIALOGUE_SHADOW_COLOR = (180, 180, 180)
DIALOGUE_RECT_X = 140
DIALOGUE_RECT_Y = 15
DIALOGUE_RECT_WIDTH = 920
DIALOGUE_RECT_HEIGHT = 45

# Important global variables
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# (RGB values)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)

# Ball-related Constants
STARTING_NUM_BALLS = 250
MIN_BALL_RADIUS = 7  # (pixels)
MAX_BALL_RADIUS = 30
H_GAP = 4  # Horizontal gap between neighbouring balls
V_GAP = 6  # Vertical gap between neighbouring balls

# Physical constants for animation
GRAVITY = 1800  # Gravity Acceleration constant (in pixels / sec^2) for animating the balls
POP_DURATION = 0.15  # How quickly a ball 'pops' in the animation (seconds)
X_FOLLOW_SPEED = 10.0


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
    radius: int
    state: str = 'falling'
    pop_time: float = 0.0

    def __init__(self, x, y, target_x, target_y, color, radius=7):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.vy = 0
        self.color = color
        self.radius = radius


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

    pygame.gfxdraw.filled_circle(screen, int(ball.x), int(ball.y), cur_radius, ball.color)
    pygame.gfxdraw.aacircle(screen, int(ball.x), int(ball.y), cur_radius, ball.color)


def update_ball_colors(balls: list[Ball], num_yes: int, num_no: int) -> None:
    """
    Update the GREEN/RED color split of the balls based off how many remaining songs produce a 'yes'
    answer to the current question (num_yes) and how many songs produce a 'no' answer (num_no)
    """
    n_total = num_yes + num_no
    num_balls = len(balls)

    if n_total == 0 or num_balls == 0:
        return

    # Formula for number of total 'yes' balls we need based off number of remaining songs
    balls_no = max(0, min(num_balls, round(num_balls * num_no / n_total)))
    # balls_no = num_balls - balls_no

    # sorts the balls left-to-right by their target x position so we could split color down the middle.
    balls_sorted = sorted(balls, key=lambda b: b.target_x)

    for ball_index, cur_ball in enumerate(balls_sorted):
        if ball_index < balls_no:
            cur_ball.color = GREEN
        else:
            cur_ball.color = RED


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

    new_radius = calculate_new_ball_radius(len(balls))
    balls.sort(key=lambda ball: (ball.target_y, ball.target_x))

    new_positions = get_ball_positions(len(balls), radius=new_radius)

    for b, (new_target_x, new_target_y) in zip(balls, new_positions):
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


def draw_ui(screen: pygame.Surface, dialogue_text: str, question_text: str, no_count: int, yes_count: int) -> None:
    """
    Draw the Question/Answer tree structure on the pygame window.
    """
    # Dialogue Rectangle
    dialogue_rect = pygame.Rect(DIALOGUE_RECT_X, DIALOGUE_RECT_Y, DIALOGUE_RECT_WIDTH, DIALOGUE_RECT_HEIGHT)

    dialogue_shadow = dialogue_rect.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, DIALOGUE_SHADOW_COLOR, dialogue_shadow, border_radius=RECT_BORDER_RADIUS)

    pygame.draw.rect(screen, DIALOGUE_FILL_COLOR, dialogue_rect, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, PURPLE, dialogue_rect, width=2, border_radius=RECT_BORDER_RADIUS)

    dialogue_surface = DIALOGUE_FONT.render("Harmoniq: " + dialogue_text, True, BLACK)
    dialogue_text_rect = dialogue_surface.get_rect(center=dialogue_rect.center)

    screen.blit(dialogue_surface, dialogue_text_rect)

    # Question Rectangle
    question_rectangle = pygame.Rect(round(QUESTION_BOX_CENTER_X - QUESTION_NODE_WIDTH / 2),
                                     QUESTION_BOX_TOP, QUESTION_NODE_WIDTH, QUESTION_NODE_HEIGHT)

    question_surface = QUESTION_FONT.render(question_text, True, BLACK)
    question_text_rect = question_surface.get_rect(center=question_rectangle.center)

    question_shadow = question_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, PURPLE, question_shadow, border_radius=RECT_BORDER_RADIUS)

    pygame.draw.rect(screen, DEFAULT_RECT_FILL_COLOR, question_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, PURPLE, question_rectangle, width=3, border_radius=RECT_BORDER_RADIUS)
    screen.blit(question_surface, question_text_rect)

    # I dont know rectangle (Button/Interactive)
    idk_rectangle = pygame.Rect(round(IDK_NODE_POSITION[0] - ANSWER_NODE_WIDTH/2),
                                round(IDK_NODE_POSITION[1] + ANSWER_NODE_HEIGHT/2),
                                ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT)
    idk_surface = IDK_LABELS_FONT.render("I dont know", True, PURPLE)
    idk_text_rect = idk_surface.get_rect(center=idk_rectangle.center)

    idk_shadow = idk_rectangle.move(NODE_SHADOW_OFFSET, NODE_SHADOW_OFFSET)
    pygame.draw.rect(screen, PURPLE, idk_shadow, border_radius=RECT_BORDER_RADIUS)

    pygame.draw.rect(screen, DEFAULT_RECT_FILL_COLOR, idk_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, PURPLE, idk_rectangle, width=3, border_radius=RECT_BORDER_RADIUS)
    screen.blit(idk_surface, idk_text_rect)

    # Yes/No Rectangles (Button/Interactive)
    yes_rectangle = pygame.Rect(round(YES_NODE_POSITION[0] - ANSWER_NODE_WIDTH/2),
                                round(YES_NODE_POSITION[1] + ANSWER_NODE_HEIGHT/2),
                                ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT)
    no_rectangle = pygame.Rect(round(NO_NODE_POSITION[0] - ANSWER_NODE_WIDTH/2),
                               round(NO_NODE_POSITION[1] + ANSWER_NODE_HEIGHT/2),
                               ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT)

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

    pygame.draw.rect(screen, DEFAULT_RECT_FILL_COLOR, yes_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, GREEN, yes_rectangle, width=3, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, DEFAULT_RECT_FILL_COLOR, no_rectangle, border_radius=RECT_BORDER_RADIUS)
    pygame.draw.rect(screen, RED, no_rectangle, width=3, border_radius=RECT_BORDER_RADIUS)
    screen.blit(yes_surface, yes_text_rect)
    screen.blit(no_surface, no_text_rect)

    # Yes / No counts
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


################################################

# TODO: REMOVE THIS!!! FOR TESTING!!!
TEST_SPLITS = [0.60, 0.35, 0.75, 0.50, 0.20]
current_split_index = 0


def apply_next_test_split(balls: list[Ball], split_fraction: float) -> None:
    total = len(balls)
    Ny = round(total * split_fraction)
    Nn = total - Ny
    update_ball_colors(balls, Ny, Nn)


##############################################

initial_ball_radius, initial_row_number = get_layout_params(STARTING_NUM_BALLS)
positions = get_ball_positions(STARTING_NUM_BALLS, rows=initial_row_number, radius=initial_ball_radius)

# Draw all the balls in initially
balls = []
for i, (target_x, target_y) in enumerate(positions):
    start_y = -40 - (i % 20) * 12
    ball = Ball(x=target_x, y=start_y, target_x=target_x, target_y=target_y,
                color=(128, 128, 128), radius=initial_ball_radius)
    balls.append(ball)

Ny = 300000
Nn = 200000
update_ball_colors(balls, Ny, Nn)

running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # TODO: remove this and replace with inputs from the user. this is for testing.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                pop_balls(balls, 'yes')
            elif event.key == pygame.K_n:
                pop_balls(balls, 'no')
            elif event.key == pygame.K_SPACE:
                split_fraction = TEST_SPLITS[current_split_index % len(TEST_SPLITS)]
                apply_next_test_split(balls, split_fraction)
                current_split_index += 1

    for ball in balls:
        update_ball(ball, dt)

    old_ball_count = len(balls)
    balls = [ball for ball in balls if not (ball.state == "popping" and ball.pop_time >= POP_DURATION)]

    # If balls were popped out, we repack the remaining balls and sort the balls list
    if old_ball_count != len(balls):
        repack_remaining_balls(balls)

    screen.fill((25, 25, 25))

    draw_ui(screen, "I will guess your song!!", "Is the song energetic?", 200000, 300000)

    for ball in balls:
        draw_ball(screen, ball)

    pygame.display.flip()

pygame.quit()

