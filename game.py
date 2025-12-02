import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 900, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wolf-Goat-Cabbage — Boat Movement")

FONT = pygame.font.SysFont(None, 24)
BIG = pygame.font.SysFont(None, 36)

BG = (178, 255, 255)
RIVER_COLOR = (70, 130, 180)
BANK_COLOR = (3, 192, 60)
TEXT = (20, 20, 20)

IMAGES = {
    "Farmer": pygame.transform.scale(pygame.image.load("farmer.png"), (80, 80)),
    "Wolf": pygame.transform.scale(pygame.image.load("wolf.png"), (70, 60)),
    "Goat": pygame.transform.scale(pygame.image.load("goat.png"), (60, 70)),
    "Cabbage": pygame.transform.scale(pygame.image.load("cabbage.png"), (60, 60)),
}

BOAT_IMG = pygame.image.load("boat.png").convert_alpha()
BOAT_IMG = pygame.transform.scale(BOAT_IMG, (220, 120))

# -------- السهم --------
ARROW_IMG = pygame.Surface((25, 25), pygame.SRCALPHA)
pygame.draw.polygon(ARROW_IMG, (255, 80, 80), [(0, 0), (25, 12), (0, 25)])

boat_x = 220     # أبعد عن الجزيرة حتى لا يصعد فوقها
boat_y = HEIGHT // 2 + 35
boat_side = 0

state = [0, 0, 0, 0]
GOAL = [1, 1, 1, 1]

coords_left = [(40, 250), (100, 270), (40, 360), (110, 360)]
coords_right = [(830, 250), (740, 270), (830, 360), (750, 360)]

items = ["Farmer", "Wolf", "Goat", "Cabbage"]

dragging = None
offset_x = offset_y = 0
item_pos = {name: coords_left[i][:] for i, name in enumerate(items)}
on_boat = []


def draw_text(surface, text, pos, font=FONT, color=TEXT):
    img = font.render(text, True, color)
    surface.blit(img, pos)


def is_loss(s):
    f, w, g, c = s
    if w == g and f != w:
        return "You lost — Wolf ate the Goat."
    if g == c and f != g:
        return "You lost — Goat ate the Cabbage."
    return None



def draw_banks(surface, s):
    # left bank rect
    pygame.draw.ellipse(surface, (3,192,60), (-160, 240, 420, 300))
    
    # right bank rect
    pygame.draw.ellipse(surface, (3,192,60),(640, 240, 420, 300))

def redraw(msg=None):
    WIN.fill(BG)

    pygame.draw.rect(WIN, RIVER_COLOR, (0, HEIGHT//2, WIDTH, HEIGHT//2))
    draw_banks(WIN, state)
    SUN_POS = (WIDTH - 100, 80)  # x, y
    SUN_RADIUS = 40
    pygame.draw.circle(WIN, (255, 223, 0), SUN_POS, SUN_RADIUS)

    for i, name in enumerate(items):
        if name in on_boat:
            idx = on_boat.index(name)
            pos = [boat_x + 55 + idx * 45, boat_y + 25]
        elif name == dragging:
            pos = item_pos[name]
        else:
            side = state[i]
            pos = coords_right[i] if side == 1 else coords_left[i]

        item_pos[name] = pos[:]

        img = IMAGES[name]
        WIN.blit(img, (pos[0] - 30, pos[1] - 30))

    if msg:
        draw_text(WIN, msg, (30, 410), BIG, (200, 30, 30))


    WIN.blit(BOAT_IMG, (boat_x, boat_y))

    # -------- السهم --------
    if boat_side == 0:
        arrow = ARROW_IMG
        arrow_pos = (boat_x + 180, boat_y - 15)
    else:
        arrow = pygame.transform.flip(ARROW_IMG, True, False)
        arrow_pos = (boat_x + 10, boat_y - 15)

    WIN.blit(arrow, arrow_pos)

    # Items
    


def animate_boat(target_x):
    global boat_x
    step = 3 if target_x > boat_x else -3
    while abs(boat_x - target_x) > 3:
        boat_x += step
        redraw()
        pygame.display.update()
        pygame.time.delay(15)
    boat_x = target_x


def mainloop():
    global dragging, offset_x, offset_y, boat_x, boat_side, state, on_boat
    clock = pygame.time.Clock()
    msg = None

    while True:
        clock.tick(30)
        redraw(msg)
        pygame.display.update()

        if state == GOAL:
            msg = "You won! All safely across."

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Arrow rect
                arrow_rect = pygame.Rect(
                    (boat_x + 180 if boat_side == 0 else boat_x + 10),
                    boat_y - 15, 25, 25
                )

                if arrow_rect.collidepoint(mx, my):

                    # يجب وجود الفارمر فقط — مسموح لوحده
                    if "Farmer" not in on_boat:
                        msg = "Farmer must be on the boat."
                        continue

                    # لا شرط لوجود عنصرين — الفارمر وحده يكفي
                    boat_side = 1 - boat_side
                    target = 220 if boat_side == 0 else 500
                    animate_boat(target)

                    # Move passengers
                    for name in on_boat:
                        idx = items.index(name)
                        state[idx] = boat_side
                    on_boat = []

                    msg = is_loss(state)
                    continue

                # Drag start
                for name, pos in item_pos.items():
                    dx = mx - pos[0]
                    dy = my - pos[1]
                    if dx * dx + dy * dy <= 28 * 28:
                        dragging = name
                        offset_x, offset_y = dx, dy
                        break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    x, y = item_pos[dragging]

                    # Drop into boat
                    if boat_x <= x <= boat_x + 220 and boat_y <= y <= boat_y + 120:
                        if dragging not in on_boat and len(on_boat) < 2:
                            on_boat.append(dragging)
                    else:
                        # Return to shore
                        side = state[items.index(dragging)]
                        item_pos[dragging] = (
                            coords_right[items.index(dragging)]
                            if side == 1 else coords_left[items.index(dragging)]
                        )

                    dragging = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                item_pos[dragging] = [mx - offset_x, my - offset_y]


if __name__ == "__main__":
    mainloop()
