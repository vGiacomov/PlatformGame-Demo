import sys
import math
import pgzrun
from pygame import Rect
from pgzero.keyboard import keys

from map import PLATFORMS, ENEMIES_DATA, GOAL, WIDTH, HEIGHT, GROUND_Y
from player import Player
from enemy import Enemy

TITLE         = "Tales of wicked forest"
CAMERA_MAX    = 8000.0 - WIDTH
CAMERA_SMOOTH = 0.12

C_GND   = (50,  50,  50);  C_GND_B = (25,  25,  25)
C_PLT   = (100, 60,  150); C_PLT_B = (160, 110, 200)

state    = "menu"
player   = None
enemies  = []
cam_x    = 0.0
win      = False
music_on = True
sel      = 0
tick     = 0

MENU_LABELS = ["Start", "Music: ON", "Exit"]
BTN = [Rect(WIDTH // 2 - 220, 320 + i * 110, 440, 76) for i in range(3)]

_has_bg   = False
_has_goal = False


def _init_assets():
    global _has_bg, _has_goal
    from pgzero.loaders import images
    try:    images.load("bg_forest"); _has_bg   = True
    except: pass
    try:    images.load("goal");      _has_goal = True
    except: pass


def _blit_bg(off=0):
    if _has_bg:
        screen.blit("bg_forest", (-off, 0))
        screen.blit("bg_forest", (WIDTH - off, 0))
    else:
        screen.fill((15, 10, 30))


def _draw_veil(alpha):
    import pygame as _pg
    veil = _pg.Surface((WIDTH, HEIGHT), _pg.SRCALPHA)
    veil.fill((0, 0, 0, alpha))
    screen.surface.blit(veil, (0, 0))


def _draw_goal(cx):
    gx = GOAL.x - cx
    if not (-GOAL.width < gx < WIDTH):
        return
    gy = GOAL.y
    if _has_goal:
        screen.blit("goal", (gx, gy))
        return
    cx2, cy2 = gx + GOAL.width // 2, gy + GOAL.height // 2
    for r in range(70, 10, -12):
        p   = int(math.sin(tick * 0.08 + r * 0.3) * 20)
        col = (max(0,min(255,80+p)), max(0,min(255,40+p*2)), max(0,min(255,200+p)))
        screen.draw.circle((cx2, cy2), r + int(math.sin(tick * 0.1) * 5), col)
    ir = 30 + int(math.sin(tick * 0.15) * 8)
    screen.draw.circle((cx2, cy2), ir,      (200, 160, 255))
    screen.draw.circle((cx2, cy2), ir // 2, (255, 240, 255))
    screen.draw.text("CEL", center=(cx2, gy - 20), fontsize=28, color=(220, 200, 255))


def _draw_platform(p, cx):
    pr = Rect(p.x - cx, p.y, p.width, p.height)
    if pr.right < 0 or pr.left > WIDTH:
        return
    if p.height > 50:
        screen.draw.filled_rect(pr, C_GND); screen.draw.rect(pr, C_GND_B)
    else:
        screen.draw.filled_rect(pr, C_PLT); screen.draw.rect(pr, C_PLT_B)


def reset():
    global player, enemies, cam_x, win
    player = Player(50, float(GROUND_Y - Player.H - 1))
    enemies = [Enemy(x, y, l, r, s) for x, y, l, r, s in ENEMIES_DATA]
    cam_x   = 0.0
    win     = False


def play_music():
    if not music_on: return
    try: music.play("bg_music"); music.set_volume(0.4)
    except Exception: pass


def stop_music():
    try: music.stop()
    except Exception: pass


def sfx(name):
    try: getattr(sounds, name).play()
    except Exception: pass


def _end_game(victory):
    global state, win
    state = "over"; win = victory
    stop_music()
    sfx("win" if victory else "jump")


def update():
    global cam_x, tick
    tick += 1
    if state != "game":
        return
    player.update(keyboard, PLATFORMS)
    if player.y > HEIGHT + 200:
        player.alive = False
    if not player.alive:
        _end_game(False); return
    ar = player.attack_rect
    for e in enemies:
        e.update()
        if not e.alive: continue
        if player.rect.colliderect(e.rect):
            player.take_damage()
        if ar and ar.colliderect(e.rect):
            e.take_hit()
    target = max(0.0, min(player.x - WIDTH // 3, CAMERA_MAX))
    cam_x += (target - cam_x) * CAMERA_SMOOTH
    if player.rect.colliderect(GOAL):
        _end_game(True)


def draw():
    if   state == "menu": _draw_menu()
    elif state == "game": _draw_game()
    elif state == "over": _draw_game(); _draw_overlay()


def _draw_menu():
    _blit_bg()
    _draw_veil(160)
    screen.draw.text("Tales of wicked forest",
                     center=(WIDTH // 2, 170), fontsize=80, color=(210, 170, 255))
    screen.draw.text("Arrows + ENTER or mouse  |  X - attack",
                     center=(WIDTH // 2, 260), fontsize=28, color=(160, 140, 200))
    for i, btn in enumerate(BTN):
        lbl    = ("Music: ON" if music_on else "Music: OFF") if i == 1 else MENU_LABELS[i]
        active = (i == sel)
        screen.draw.filled_rect(btn, (90, 30, 130) if active else (40, 18, 60))
        screen.draw.rect(       btn, (240,200,255) if active else (100,70,150))
        screen.draw.text(lbl, center=btn.center, fontsize=40,
                         color=(255,235,110) if active else (200,175,255))


def _draw_game():
    _blit_bg(int(cam_x * 0.2) % WIDTH)
    cx = int(cam_x)
    for p in PLATFORMS:
        _draw_platform(p, cx)
    _draw_goal(cx)
    for e in enemies:
        e.draw(screen, cx)
    player.draw(screen, cx)
    screen.draw.text(f"HP: {player.hp} / {player.MAX_HP}",
                     (20, 18), fontsize=44, color=(255, 80, 80))


def _draw_overlay():
    _draw_veil(140)
    msg = "VICTORY!" if win else "GAME OVER"
    col = (255, 210, 30) if win else (255, 60, 60)
    screen.draw.text(msg, center=(WIDTH//2, HEIGHT//2 - 60), fontsize=100, color=col)
    screen.draw.text("ENTER - Back to menu",
                     center=(WIDTH//2, HEIGHT//2 + 60), fontsize=38, color="white")


def on_mouse_move(pos):
    global sel
    if state != "menu": return
    for i, b in enumerate(BTN):
        if b.collidepoint(pos): sel = i


def on_mouse_down(pos):
    if state != "menu": return
    for i, b in enumerate(BTN):
        if b.collidepoint(pos): _pick(i)


def on_key_down(key):
    global sel, state
    if state == "menu":
        if key == keys.UP:   sel = (sel - 1) % 3
        if key == keys.DOWN: sel = (sel + 1) % 3
        if key in (keys.RETURN, keys.KP_ENTER): _pick(sel)
    elif state == "over":
        if key in (keys.RETURN, keys.KP_ENTER): state = "menu"
    elif state == "game":
        if key == keys.X:      player.start_attack()
        if key == keys.ESCAPE: state = "menu"; stop_music()


def _pick(i):
    global state, music_on
    if   i == 0: reset(); state = "game"; play_music()
    elif i == 1: music_on = not music_on; play_music() if music_on else stop_music()
    elif i == 2: sys.exit()


reset()
_init_assets()
pgzrun.go()
