import pygame
import random
import os
import json
import array
import math

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# ---------------------------------------------------------
# 1. ضبط مجلد العمل والمسارات
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# ---------------------------------------------------------
# 2. إعداد الشاشة القابلة للتغيير والألوان المحدثة
# ---------------------------------------------------------
WIDTH, HEIGHT = 450, 680
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("BLOCK IYAD")

# درجات الأزرق السماوي الفاتحة الجديدة
BACKGROUND_COLOR = (215, 238, 255)  # أزرق سماوي فاتح جداً لجميع الخلفيات
PANEL_COLOR = (175, 212, 240)       # أزرق سماوي أغمق قليلاً للشبكة ومستطيل القطع والأزرار

TEXT_GOLD = (215, 140, 0)
TEXT_WHITE = (40, 50, 70)           # لون نصوص غامق ليتناسب مع الخلفية الفاتحة
TEXT_CYAN = (0, 100, 180)
TEXT_RED = (220, 50, 50)
TEXT_GRAY = (100, 110, 130)

GRID_SIZE = 8

CELL_SIZE = 40
GRID_MARGIN = 4
PIECE_MARGIN = 3
SMALL_CELL_SIZE = 24
BOARD_OFFSET_X = 0
BOARD_OFFSET_Y = 0

fonts = {}

def recalculate_layout(w, h):
    global WIDTH, HEIGHT, CELL_SIZE, GRID_MARGIN, PIECE_MARGIN, SMALL_CELL_SIZE
    global BOARD_OFFSET_X, BOARD_OFFSET_Y, fonts
    
    WIDTH, HEIGHT = w, h
    
    max_board_w = min(WIDTH * 0.9, HEIGHT * 0.55)
    CELL_SIZE = int(max_board_w // GRID_SIZE)
    GRID_MARGIN = max(2, int(CELL_SIZE * 0.08))
    PIECE_MARGIN = max(1, int(GRID_MARGIN // 2))
    SMALL_CELL_SIZE = max(12, int(CELL_SIZE * 0.55))
    
    board_total_w = GRID_SIZE * (CELL_SIZE + GRID_MARGIN)
    BOARD_OFFSET_X = (WIDTH - board_total_w) // 2
    BOARD_OFFSET_Y = int(HEIGHT * 0.16)
    
    base_font_scale = max(12, int(HEIGHT * 0.03))
    fonts = {
        "title": pygame.font.SysFont("Arial", int(base_font_scale * 1.5), bold=True),
        "big": pygame.font.SysFont("Arial", int(base_font_scale * 1.2), bold=True),
        "medium": pygame.font.SysFont("Arial", int(base_font_scale * 0.8), bold=True),
        "button": pygame.font.SysFont("Arial", int(base_font_scale * 0.9), bold=True)
    }

recalculate_layout(WIDTH, HEIGHT)

# ---------------------------------------------------------
# 3. توليد الأصوات والموسيقى برمجيًا
# ---------------------------------------------------------
music_enabled = True
sound_enabled = True

def generate_sound(frequency, duration, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        val = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

try:
    clear_sound = generate_sound(880, 0.15, 0.4)
except:
    clear_sound = None

# ---------------------------------------------------------
# 4. تحميل الصور مع إعادة التحجيم الديناميكي
# ---------------------------------------------------------
IMAGE_NAMES = ["1", "2", "3", "4", "5"]
RAW_BLOCK_IMAGES = {}

def load_block_image(name):
    extensions = [".png", ".PNG", ".jpg", ".jpeg", ".png.png"]
    for ext in extensions:
        full_path = os.path.join(BASE_DIR, name + ext)
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path)
                return img.convert_alpha() if img.get_alpha() else img.convert()
            except:
                pass
    return None

for name in IMAGE_NAMES:
    idx = int(name)
    loaded_img = load_block_image(name)
    if loaded_img:
        RAW_BLOCK_IMAGES[idx] = loaded_img
    else:
        surf = pygame.Surface((100, 100))
        surf.fill((70, 130, 180))
        RAW_BLOCK_IMAGES[idx] = surf

NORMAL_IMAGE_INDICES = [1, 2, 3, 5]

def get_scaled_images():
    scaled_main = {}
    scaled_small = {}
    for idx, img in RAW_BLOCK_IMAGES.items():
        scaled_main[idx] = pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
        scaled_small[idx] = pygame.transform.smoothscale(img, (SMALL_CELL_SIZE, SMALL_CELL_SIZE))
    return scaled_main, scaled_small

# ---------------------------------------------------------
# 5. البيانات والحفظ
# ---------------------------------------------------------
SCORE_FILE = os.path.join(BASE_DIR, "user_data.json")
user_email = ""
high_score = 0

def load_local_data():
    global user_email, high_score
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                data = json.load(f)
                user_email = data.get("email", "")
                high_score = data.get("high_score", 0)
        except:
            pass

def save_local_data():
    with open(SCORE_FILE, "w") as f:
        json.dump({"email": user_email, "high_score": high_score}, f)

load_local_data()

# ---------------------------------------------------------
# 6. إعدادات وقواعد اللعبة
# ---------------------------------------------------------
SHAPES = [
    [[1]], [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1], [1], [1]], [[1, 1], [1, 1]]
]

grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
score = 0
game_state = "MENU"
previous_state = "MENU"
show_settings = False
input_active_email = False
current_theme_image = 1

def pick_random_theme():
    return random.choice(NORMAL_IMAGE_INDICES)

def generate_piece():
    shape = random.choice(SHAPES)
    rows, cols = len(shape), len(shape[0])
    image_matrix = [[current_theme_image if shape[r][c] == 1 else 0 for c in range(cols)] for r in range(rows)]
    return {"shape": shape, "images": image_matrix}

def refresh_spawned_pieces():
    return [generate_piece(), generate_piece(), generate_piece()]

def start_new_game():
    global grid, score, current_theme_image, spawned_pieces, game_state
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    score = 0
    current_theme_image = pick_random_theme()
    spawned_pieces = refresh_spawned_pieces()
    game_state = "PLAYING"

spawned_pieces = []
dragging_piece = None
drag_orig_pos = None

def get_piece_positions():
    gap = WIDTH // 3
    panel_y = int(HEIGHT * 0.85)
    return [(i * gap + gap // 2, panel_y) for i in range(3)]

def can_place(shape, grid_x, grid_y):
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                gx, gy = grid_x + c, grid_y + r
                if gx < 0 or gx >= GRID_SIZE or gy < 0 or gy >= GRID_SIZE or grid[gy][gx] != 0:
                    return False
    return True

def get_lines_to_clear_preview(piece, grid_x, grid_y):
    temp_grid = [row[:] for row in grid]
    shape, images = piece["shape"], piece["images"]
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                temp_grid[grid_y + r][grid_x + c] = images[r][c]
                
    rows_to_clear = [r for r in range(GRID_SIZE) if all(temp_grid[r][c] != 0 for c in range(GRID_SIZE))]
    cols_to_clear = [c for c in range(GRID_SIZE) if all(temp_grid[r][c] != 0 for r in range(GRID_SIZE))]
    return rows_to_clear, cols_to_clear

def check_game_over():
    for piece in spawned_pieces:
        if piece is not None:
            shape = piece["shape"]
            for gy in range(GRID_SIZE):
                for gx in range(GRID_SIZE):
                    if can_place(shape, gx, gy):
                        return False
    return True

def place_piece(piece, grid_x, grid_y):
    global score
    shape, images = piece["shape"], piece["images"]
    placed_blocks = 0
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                grid[grid_y + r][grid_x + c] = images[r][c]
                placed_blocks += 1
    score += placed_blocks * 10
    clear_lines()

def clear_lines():
    global score
    rows_to_clear = [r for r in range(GRID_SIZE) if all(grid[r][c] != 0 for c in range(GRID_SIZE))]
    cols_to_clear = [c for c in range(GRID_SIZE) if all(grid[r][c] != 0 for r in range(GRID_SIZE))]
    
    for r in rows_to_clear:
        for c in range(GRID_SIZE):
            grid[r][c] = 0
            
    for c in cols_to_clear:
        for r in range(GRID_SIZE):
            grid[r][c] = 0
            
    cleared = len(rows_to_clear) + len(cols_to_clear)
    if cleared > 0:
        score += cleared * 100
        if clear_sound and sound_enabled:
            clear_sound.play()

# ---------------------------------------------------------
# 7. الواجهات الرسمية والأزرار
# ---------------------------------------------------------
def draw_settings_button():
    btn_size = int(min(WIDTH, HEIGHT) * 0.08)
    btn_rect = pygame.Rect(WIDTH - btn_size - 10, 10, btn_size, btn_size)
    pygame.draw.rect(SCREEN, PANEL_COLOR, btn_rect, border_radius=8)
    line_gap = btn_size // 4
    for i in range(3):
        y_pos = btn_rect.y + line_gap * (i + 0.8)
        pygame.draw.line(SCREEN, TEXT_WHITE, (btn_rect.x + 8, y_pos), (btn_rect.x + btn_size - 8, y_pos), 3)
    return btn_rect

def draw_piece(piece, center_x, center_y, is_dragging=False):
    scaled_main, scaled_small = get_scaled_images()
    shape, images = piece["shape"], piece["images"]
    img_dict = scaled_main if is_dragging else scaled_small
    cell_s = CELL_SIZE if is_dragging else SMALL_CELL_SIZE
    m_size = GRID_MARGIN if is_dragging else PIECE_MARGIN
    
    rows, cols = len(shape), len(shape[0])
    total_w = cols * cell_s + (cols - 1) * m_size
    total_h = rows * cell_s + (rows - 1) * m_size
    
    start_x = center_x - total_w // 2
    start_y = center_y - total_h // 2
    
    for r in range(rows):
        for c in range(cols):
            if shape[r][c] == 1:
                img_idx = images[r][c]
                if img_idx in img_dict:
                    pos_x = start_x + c * (cell_s + m_size)
                    pos_y = start_y + r * (cell_s + m_size)
                    SCREEN.blit(img_dict[img_idx], (pos_x, pos_y))

def draw_menu():
    SCREEN.fill(BACKGROUND_COLOR)
    title_txt = fonts["title"].render("BLOCK IYAD", True, TEXT_GOLD)
    SCREEN.blit(title_txt, title_txt.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.2))))
    
    best_title = fonts["medium"].render("BEST SCORE", True, TEXT_CYAN)
    best_val = fonts["big"].render(str(high_score), True, TEXT_WHITE)
    SCREEN.blit(best_title, best_title.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.38))))
    SCREEN.blit(best_val, best_val.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.44))))
    
    btn_w, btn_h = int(WIDTH * 0.45), int(HEIGHT * 0.08)
    play_btn = pygame.Rect((WIDTH - btn_w) // 2, int(HEIGHT * 0.6), btn_w, btn_h)
    pygame.draw.rect(SCREEN, (76, 175, 80), play_btn, border_radius=12)
    play_txt = fonts["button"].render("PLAY", True, (255, 255, 255))
    SCREEN.blit(play_txt, play_txt.get_rect(center=play_btn.center))
    
    settings_btn = draw_settings_button()
    return play_btn, settings_btn

def draw_gameplay(drag_pos=None):
    global high_score
    scaled_main, _ = get_scaled_images()
    SCREEN.fill(BACKGROUND_COLOR)
    
    if score > high_score:
        high_score = score
        save_local_data()
        
    best_lbl = fonts["medium"].render("BEST", True, TEXT_CYAN)
    best_val = fonts["big"].render(str(high_score), True, TEXT_GOLD)
    SCREEN.blit(best_lbl, best_lbl.get_rect(center=(WIDTH // 4, int(HEIGHT * 0.05))))
    SCREEN.blit(best_val, best_val.get_rect(center=(WIDTH // 4, int(HEIGHT * 0.09))))
    
    score_lbl = fonts["medium"].render("SCORE", True, TEXT_CYAN)
    score_val = fonts["big"].render(str(score), True, TEXT_WHITE)
    SCREEN.blit(score_lbl, score_lbl.get_rect(center=(WIDTH * 0.65, int(HEIGHT * 0.05))))
    SCREEN.blit(score_val, score_val.get_rect(center=(WIDTH * 0.65, int(HEIGHT * 0.09))))

    preview_rows, preview_cols = [], []
    if dragging_piece is not None and drag_pos is not None:
        mx, my = drag_pos
        offset_y_touch = my - int(CELL_SIZE * 1.5)
        shape = dragging_piece["shape"]
        rows, cols = len(shape), len(shape[0])
        start_x = mx - (cols * (CELL_SIZE + GRID_MARGIN)) // 2
        start_y = offset_y_touch - (rows * (CELL_SIZE + GRID_MARGIN)) // 2
        
        hover_grid_x = round((start_x - BOARD_OFFSET_X) / (CELL_SIZE + GRID_MARGIN))
        hover_grid_y = round((start_y - BOARD_OFFSET_Y) / (CELL_SIZE + GRID_MARGIN))
        
        if can_place(dragging_piece["shape"], hover_grid_x, hover_grid_y):
            preview_rows, preview_cols = get_lines_to_clear_preview(dragging_piece, hover_grid_x, hover_grid_y)

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x = BOARD_OFFSET_X + c * (CELL_SIZE + GRID_MARGIN)
            y = BOARD_OFFSET_Y + r * (CELL_SIZE + GRID_MARGIN)
            val = grid[r][c]
            will_be_cleared = (r in preview_rows) or (c in preview_cols)
            
            if will_be_cleared:
                SCREEN.blit(scaled_main[4], (x, y))
            elif val != 0:
                SCREEN.blit(scaled_main[val], (x, y))
            else:
                pygame.draw.rect(SCREEN, PANEL_COLOR, (x, y, CELL_SIZE, CELL_SIZE), border_radius=6)

    panel_h = int(HEIGHT * 0.22)
    panel_rect = pygame.Rect(10, HEIGHT - panel_h - 10, WIDTH - 20, panel_h)
    pygame.draw.rect(SCREEN, PANEL_COLOR, panel_rect, border_radius=15)
    
    positions = get_piece_positions()
    for i, piece in enumerate(spawned_pieces):
        if piece is not None and piece != dragging_piece:
            px, py = positions[i]
            draw_piece(piece, px, py, is_dragging=False)
            
    if dragging_piece is not None and drag_pos is not None:
        mx, my = drag_pos
        draw_piece(dragging_piece, mx, my - int(CELL_SIZE * 1.5), is_dragging=True)
        
    settings_btn = draw_settings_button()
    return settings_btn

def draw_settings_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    SCREEN.blit(overlay, (0, 0))
    
    dialog_w, dialog_h = int(WIDTH * 0.88), int(HEIGHT * 0.7)
    dialog = pygame.Rect((WIDTH - dialog_w) // 2, (HEIGHT - dialog_h) // 2, dialog_w, dialog_h)
    pygame.draw.rect(SCREEN, BACKGROUND_COLOR, dialog, border_radius=15)
    pygame.draw.rect(SCREEN, PANEL_COLOR, dialog, 3, border_radius=15)
    
    back_btn = pygame.Rect(dialog.x + 15, dialog.y + 15, 40, 35)
    pygame.draw.rect(SCREEN, PANEL_COLOR, back_btn, border_radius=8)
    back_txt = fonts["button"].render("<-", True, TEXT_WHITE)
    SCREEN.blit(back_txt, back_txt.get_rect(center=back_btn.center))
    
    title = fonts["big"].render("SETTINGS", True, TEXT_GOLD)
    SCREEN.blit(title, title.get_rect(center=(dialog.centerx, dialog.y + 35)))
    
    lbl_e = fonts["medium"].render("Email:", True, TEXT_CYAN)
    SCREEN.blit(lbl_e, (dialog.x + 20, dialog.y + 80))
    input_box_e = pygame.Rect(dialog.x + 20, dialog.y + 110, dialog_w - 40, 40)
    pygame.draw.rect(SCREEN, (255, 255, 255), input_box_e, border_radius=8)
    pygame.draw.rect(SCREEN, TEXT_CYAN if input_active_email else TEXT_GRAY, input_box_e, 2, border_radius=8)
    txt_e = user_email if user_email else "Enter Email..."
    SCREEN.blit(fonts["medium"].render(txt_e, True, TEXT_WHITE if user_email else TEXT_GRAY), (input_box_e.x + 10, input_box_e.y + 10))

    music_btn = pygame.Rect(dialog.x + 20, dialog.y + 180, dialog_w - 40, 45)
    m_color = (76, 175, 80) if music_enabled else (200, 60, 60)
    pygame.draw.rect(SCREEN, m_color, music_btn, border_radius=10)
    m_txt = f"Music: {'ON' if music_enabled else 'OFF'}"
    SCREEN.blit(fonts["button"].render(m_txt, True, (255, 255, 255)), fonts["button"].render(m_txt, True, (255, 255, 255)).get_rect(center=music_btn.center))

    sound_btn = pygame.Rect(dialog.x + 20, dialog.y + 240, dialog_w - 40, 45)
    s_color = (76, 175, 80) if sound_enabled else (200, 60, 60)
    pygame.draw.rect(SCREEN, s_color, sound_btn, border_radius=10)
    s_txt = f"Sound Effects: {'ON' if sound_enabled else 'OFF'}"
    SCREEN.blit(fonts["button"].render(s_txt, True, (255, 255, 255)), fonts["button"].render(s_txt, True, (255, 255, 255)).get_rect(center=sound_btn.center))

    save_btn = pygame.Rect(dialog.centerx - 60, dialog.y + dialog_h - 60, 120, 40)
    pygame.draw.rect(SCREEN, (0, 150, 200), save_btn, border_radius=10)
    SCREEN.blit(fonts["button"].render("SAVE", True, (255, 255, 255)), fonts["button"].render("SAVE", True, (255, 255, 255)).get_rect(center=save_btn.center))
    
    return back_btn, input_box_e, music_btn, sound_btn, save_btn

def draw_game_over():
    draw_gameplay()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    SCREEN.blit(overlay, (0, 0))
    
    go_txt = fonts["title"].render("GAME OVER", True, TEXT_RED)
    SCREEN.blit(go_txt, go_txt.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.35))))
    
    final_score = fonts["medium"].render(f"FINAL SCORE: {score}", True, (255, 255, 255))
    SCREEN.blit(final_score, final_score.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.45))))
    
    btn_w, btn_h = int(WIDTH * 0.45), int(HEIGHT * 0.08)
    retry_btn = pygame.Rect((WIDTH - btn_w) // 2, int(HEIGHT * 0.55), btn_w, btn_h)
    pygame.draw.rect(SCREEN, (76, 175, 80), retry_btn, border_radius=10)
    retry_txt = fonts["button"].render("RETRY", True, (255, 255, 255))
    SCREEN.blit(retry_txt, retry_txt.get_rect(center=retry_btn.center))
    
    return retry_btn

# ---------------------------------------------------------
# 8. الحلقة الرئيسية ومعالجة أحداث اللمس والماوس
# ---------------------------------------------------------
running = True
clock = pygame.time.Clock()
current_pointer_pos = (0, 0)

while running:
    clock.tick(60)
    
    if pygame.mouse.get_pressed()[0]:
        current_pointer_pos = pygame.mouse.get_pos()
        
    if game_state == "MENU":
        play_btn, settings_btn = draw_menu()
        if show_settings:
            back_btn, input_box_e, music_btn, sound_btn, save_btn = draw_settings_overlay()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                recalculate_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
                if show_settings:
                    if back_btn.collidepoint(pos) or save_btn.collidepoint(pos):
                        show_settings = False
                        save_local_data()
                        game_state = previous_state
                    elif input_box_e.collidepoint(pos):
                        input_active_email = True
                    elif music_btn.collidepoint(pos):
                        music_enabled = not music_enabled
                    elif sound_btn.collidepoint(pos):
                        sound_enabled = not sound_enabled
                else:
                    if play_btn.collidepoint(pos):
                        start_new_game()
                    elif settings_btn.collidepoint(pos):
                        previous_state = "MENU"
                        show_settings = True
            elif event.type == pygame.KEYDOWN and show_settings:
                if input_active_email:
                    if event.key == pygame.K_RETURN:
                        input_active_email = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_email = user_email[:-1]
                    elif len(user_email) < 30 and event.unicode.isprintable():
                        user_email += event.unicode

    elif game_state == "PLAYING":
        settings_btn = draw_gameplay(drag_pos=current_pointer_pos)
        if show_settings:
            back_btn, input_box_e, music_btn, sound_btn, save_btn = draw_settings_overlay()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                recalculate_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
                current_pointer_pos = pos
                if show_settings:
                    if back_btn.collidepoint(pos) or save_btn.collidepoint(pos):
                        show_settings = False
                        save_local_data()
                        game_state = previous_state
                    elif input_box_e.collidepoint(pos):
                        input_active_email = True
                    elif music_btn.collidepoint(pos):
                        music_enabled = not music_enabled
                    elif sound_btn.collidepoint(pos):
                        sound_enabled = not sound_enabled
                else:
                    if settings_btn.collidepoint(pos):
                        previous_state = "PLAYING"
                        show_settings = True
                    else:
                        positions = get_piece_positions()
                        for i, piece in enumerate(spawned_pieces):
                            if piece is not None:
                                px, py = positions[i]
                                if abs(pos[0] - px) < CELL_SIZE * 1.2 and abs(pos[1] - py) < CELL_SIZE * 1.2:
                                    dragging_piece = piece
                                    drag_orig_pos = i
                                    break
                                    
            elif event.type == pygame.FINGERMOTION:
                current_pointer_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))

            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
                if dragging_piece is not None and not show_settings:
                    mx, my = pos
                    offset_y_touch = my - int(CELL_SIZE * 1.5)
                    shape = dragging_piece["shape"]
                    rows, cols = len(shape), len(shape[0])
                    start_x = mx - (cols * (CELL_SIZE + GRID_MARGIN)) // 2
                    start_y = offset_y_touch - (rows * (CELL_SIZE + GRID_MARGIN)) // 2
                    grid_x = round((start_x - BOARD_OFFSET_X) / (CELL_SIZE + GRID_MARGIN))
                    grid_y = round((start_y - BOARD_OFFSET_Y) / (CELL_SIZE + GRID_MARGIN))
                    
                    if can_place(dragging_piece["shape"], grid_x, grid_y):
                        place_piece(dragging_piece, grid_x, grid_y)
                        spawned_pieces[drag_orig_pos] = None
                        if all(p is None for p in spawned_pieces):
                            spawned_pieces = refresh_spawned_pieces()
                        if check_game_over():
                            game_state = "GAME_OVER"
                    dragging_piece = None

            elif event.type == pygame.KEYDOWN and show_settings:
                if input_active_email:
                    if event.key == pygame.K_RETURN:
                        input_active_email = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_email = user_email[:-1]
                    elif len(user_email) < 30 and event.unicode.isprintable():
                        user_email += event.unicode

    elif game_state == "GAME_OVER":
        retry_btn = draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                recalculate_layout(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
                if retry_btn.collidepoint(pos):
                    start_new_game()

    pygame.display.flip()

pygame.quit()
