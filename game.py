import pygame
import sys
from collections import deque

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

# ---------------- تحميل الصور ----------------
IMAGES = {
    "Farmer": pygame.transform.scale(pygame.image.load("farmer.png"), (100, 100)),
    "Wolf": pygame.transform.scale(pygame.image.load("wolf.png"), (70, 60)),
    "Goat": pygame.transform.scale(pygame.image.load("goat.png"), (60, 70)),
    "Cabbage": pygame.transform.scale(pygame.image.load("cabbage.png"), (60, 60)),
}

BOAT_IMG = pygame.image.load("boat.png").convert_alpha()
BOAT_IMG = pygame.transform.scale(BOAT_IMG, (220, 120))

#الخسارة
LOSS_IMG = pygame.image.load("youlost.png").convert_alpha()
LOSS_IMG = pygame.transform.scale(LOSS_IMG, (300, 300))
# الفوز
WIN_IMG = pygame.image.load("youwin.png").convert_alpha()
WIN_IMG = pygame.transform.scale(WIN_IMG, (300, 300))



# -------- السهم --------
ARROW_IMG = pygame.Surface((25, 25), pygame.SRCALPHA)
pygame.draw.polygon(ARROW_IMG, (255, 80, 80), [(0, 0), (25, 12), (0, 25)])

boat_x = 220
boat_y = HEIGHT // 2 + 35
boat_side = 0

state = [0, 0, 0, 0]
GOAL = [1, 1, 1, 1]


coords_left = [(30, 230), (100, 270), (40, 360), (110, 360)]
coords_right = [(820, 220), (740, 270), (830, 360), (750, 360)]

items = ["Farmer", "Wolf", "Goat", "Cabbage"]

dragging = None
offset_x = offset_y = 0
item_pos = {name: coords_left[i][:] for i, name in enumerate(items)}
on_boat = []

# ---------------- نص ورسم ----------------
# ---- زر الحل ----
BUTTON_RECT = pygame.Rect(50,400, 100, 40) #موقع وحجم زر الحل
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
    pygame.draw.ellipse(surface, (3,192,60), (-160, 240, 420, 300))
    pygame.draw.ellipse(surface, (3,192,60),(640, 240, 420, 300))
def draw_button():
    pygame.draw.rect(WIN, (255, 150, 150), BUTTON_RECT, border_radius=12)
    pygame.draw.rect(WIN, (200, 80, 80), BUTTON_RECT, border_radius=12)
    text = FONT.render("Solve", True, (255, 255, 255))
    WIN.blit(text, (BUTTON_RECT.x + 30, BUTTON_RECT.y + 13))


def make_button(surface, text, x, y, w, h, bg=(200,80,80), fg=(255,255,255)):
    """يرسم زر ويرجع الـ Rect الخاص فيه"""
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg, rect, border_radius=10)
    # إطار أغمق
    pygame.draw.rect(surface, (bg[0]-40 if bg[0]>40 else 0, bg[1]-40 if bg[1]>40 else 0, bg[2]-40 if bg[2]>40 else 0),
                     rect, 2, border_radius=10)
    txt = FONT.render(text, True, fg)
    tx = x + (w - txt.get_width())//2
    ty = y + (h - txt.get_height())//2
    surface.blit(txt, (tx, ty))
    return rect

def reset_game():
    """إعادة تهيئة الحالة إلى البداية"""
    global state, boat_side, boat_x, on_boat, item_pos, dragging, msg
    state = [0,0,0,0]
    boat_side = 0
    boat_x = 220
    on_boat = []
    dragging = None
    # إعادة مواقع العناصر إلى الضفة اليسرى
    for i, name in enumerate(items):
        item_pos[name] = coords_left[i][:]
    msg = None




def redraw(msg=None):
    WIN.fill(BG)
    pygame.draw.rect(WIN, RIVER_COLOR, (0, HEIGHT//2, WIDTH, HEIGHT//2))
    draw_banks(WIN, state)
    draw_button()

    pygame.draw.circle(WIN, (255, 223, 0), (WIDTH - 100, 80), 40)
    WIN.blit(BOAT_IMG, (boat_x, boat_y))

    # -------- السهم --------
    if boat_side == 0:
        arrow = ARROW_IMG
        arrow_pos = (boat_x + 180, boat_y - 15)
    else:
        arrow = pygame.transform.flip(ARROW_IMG, True, False)
        arrow_pos = (boat_x + 10, boat_y - 15)

    WIN.blit(arrow, arrow_pos)

    # العناصر

    SUN_POS = (WIDTH - 100, 80)  # x, y
    SUN_RADIUS = 40
    pygame.draw.circle(WIN, (255, 223, 0), SUN_POS, SUN_RADIUS)

    for i, name in enumerate(items):
        if name in on_boat:
            idx = on_boat.index(name)
            if name == "Farmer":
                pos = [boat_x + 55 + idx * 45, boat_y + 3]   # رفع الصورة للأعلى
            else:
                pos = [boat_x + 55 + idx * 45, boat_y + 25]
        elif name == dragging:
            pos = item_pos[name]
        else:
            side = state[i]
            pos = coords_right[i] if side == 1 else coords_left[i]

        item_pos[name] = pos[:]
        WIN.blit(IMAGES[name], (pos[0] - 30, pos[1] - 30))

   


    try_again_rect = None

    if msg:
        # msg يحتوي نص الخسارة/الفوز
        if "lost" in msg.lower():
            WIN.blit(LOSS_IMG, (WIDTH//2 - LOSS_IMG.get_width()//2, HEIGHT//2 - LOSS_IMG.get_height()//2 - 20))
        else:
            WIN.blit(WIN_IMG, (WIDTH//2 - WIN_IMG.get_width()//2, HEIGHT//2 - WIN_IMG.get_height()//2 - 20))

        # ارسم زر Try Again وأحصل على rect
        try_again_rect = make_button(WIN, "Try Again", WIDTH//2 - 80, HEIGHT//2 + 140, 160, 45)

    # في نهاية redraw() رجّعي try_again_rect لو حبيت استخدامه خارجياً
# ---------------- الحركة ----------------

    WIN.blit(BOAT_IMG, (boat_x, boat_y))

    # -------- السهم --------
    if boat_side == 0:
        arrow = ARROW_IMG
        arrow_pos = (boat_x + 180, boat_y - 15)
    else:
        arrow = pygame.transform.flip(ARROW_IMG, True, False)
        arrow_pos = (boat_x + 10, boat_y - 15)

    WIN.blit(arrow, arrow_pos)
    return try_again_rect
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

# ---------------- BFS ----------------
def illegal(st):
    f, w, g, c, boat = st
    if w == g and f != w:
        return True
    if g == c and f != g:
        return True
    return False

def bfs_solve():
    start = (0,0,0,0,0)
    goal = (1,1,1,1,1)
    queue = deque([(start, [])])
    visited = {start}
    items = ["Farmer","Wolf","Goat","Cabbage"]

    while queue:
        state, path = queue.popleft()

        if state == goal:
            return path + [state]

        f, w, g, c, boat = state
        arr = [f, w, g, c]
        same_side = [i for i in range(4) if arr[i] == boat]

        moves = [[0]] + [[0, x] for x in same_side if x != 0]

        for move in moves:
            new_arr = arr[:]
            new_boat = 1 - boat

            for x in move:
                new_arr[x] = 1 - new_arr[x]

            new_state = (*new_arr, new_boat)

            if illegal(new_state):
                continue

            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [state]))

    return None

# ---------------- BFS تشغيل ----------------
def play_bfs():
    global state, boat_side, boat_x, on_boat, item_pos

    sol = bfs_solve()
    print("BFS Solution:", sol)

    for st in sol[1:]:
        prev_state = state[:]
        prev_boat = boat_side

        # ---------------- تحديد من يركب السفينة ----------------
        on_boat = []
        for i, (p, n) in enumerate(zip(prev_state, st[:4])):
            # فقط العناصر التي تغيرت موقعها في نفس طرف السفينة
            if p != n and prev_state[i] == prev_boat:
                on_boat.append(items[i])
        # تأكد أن الفلاح دائمًا على السفينة
        if "Farmer" not in on_boat:
            on_boat.append("Farmer")

        # ---------------- وضع العناصر على السفينة ----------------
        for idx, name in enumerate(on_boat):
            item_pos[name] = [boat_x + 55 + idx * 45, boat_y + 43]

        redraw()
        pygame.display.update()
        pygame.time.delay(500)

        # ---------------- تحريك السفينة ----------------
        boat_side = 1 - boat_side
        target = 220 if boat_side == 0 else 600
        animate_boat(target)

        # ---------------- وضع العناصر على الطرف الآخر ----------------
        state[:] = st[:4]
        for i, name in enumerate(items):
            side = state[i]
            item_pos[name] = coords_right[i][:] if side == 1 else coords_left[i][:]

        on_boat = []
        redraw()
        pygame.display.update()
        pygame.time.delay(500)

# ---------------- الحلقة الرئيسية ----------------
def mainloop():
    global dragging, offset_x, offset_y, boat_x, boat_side, state, on_boat
    clock = pygame.time.Clock()
    msg = None

    while True:
        clock.tick(30)
        try_again_rect = redraw(msg)
        pygame.display.update()

        if state == GOAL:
            msg = "You won! All safely across."

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ---------------- Arrow click ----------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # ----- فحص زر TRY AGAIN -----
                if msg and try_again_rect and try_again_rect.collidepoint(mx, my):
                    reset_game()
                    msg = None
                    continue

                arrow_rect = pygame.Rect(
                    (boat_x + 180 if boat_side == 0 else boat_x + 10),
                    boat_y - 15, 25, 25
               )
                if BUTTON_RECT.collidepoint(event.pos):
                    play_bfs()
                    continue

                if arrow_rect.collidepoint(mx, my):

                    if "Farmer" not in on_boat:
                        msg = "Farmer must be on the boat."
                        continue

                    boat_side = 1 - boat_side
                    target = 220 if boat_side == 0 else 500
                    animate_boat(target)

                    for name in on_boat:
                        idx = items.index(name)
                        state[idx] = boat_side
                    on_boat = []

                    msg = is_loss(state)
                    continue

                # --------- Drag start ---------
                for name, pos in item_pos.items():
                    dx = mx - pos[0]
                    dy = my - pos[1]
                    if dx*dx + dy*dy <= 28*28:
                        dragging = name
                        offset_x, offset_y = dx, dy
                        break

            # --------- Drop ---------
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    x, y = item_pos[dragging]

                    if boat_x <= x <= boat_x + 220 and boat_y <= y <= boat_y + 120:
                        if dragging not in on_boat and len(on_boat) < 2:
                            on_boat.append(dragging)
                    else:
                        side = state[items.index(dragging)]
                        item_pos[dragging] = (
                            coords_right[items.index(dragging)]
                            if side == 1 else coords_left[items.index(dragging)]
                        )

                    dragging = None

            # --------- Dragging movement ---------
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                item_pos[dragging] = [mx - offset_x, my - offset_y]


if __name__ == "__main__":
    mainloop()