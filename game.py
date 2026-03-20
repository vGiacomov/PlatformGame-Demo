import sys
import math
import pgzrun
import pygame
from pygame import Rect
from pgzero.keyboard import keys

from map    import PLATFORMS, ENEMIES_DATA, GOAL, WIDTH, HEIGHT, GROUND_Y
from player import Player
from enemy  import Enemy

TITLE = "Tales of wicked forest"

C_GND  = (50,  50,  50);  C_GND_B = (25, 25, 25)
C_PLT  = (100, 60, 150);  C_PLT_B = (160,110,200)

state    = "menu"
player   = None
enemies  = []
cam_x    = 0
win      = False
music_on = True
sel      = 0
_tick    = 0

MENU_LABELS = ["Start", "Music: ON", "Exit"]
BTN = [Rect(WIDTH//2 - 220, 320 + i*110, 440, 76) for i in range(3)]

_bg_surf   = None
_goal_surf = None

def _init_assets():
    global _bg_surf, _goal_surf
    try:
        from pgzero.loaders import images
        _bg_surf = pygame.transform.scale(images.load("bg_forest"), (WIDTH, HEIGHT))
    except Exception:
        _bg_surf = None
    try:
        from pgzero.loaders import images
        _goal_surf = pygame.transform.scale(images.load("goal"), (GOAL.width, GOAL.height))
    except Exception:
        _goal_surf = None

def _blit_bg(off=0):
    if _bg_surf:
        screen.surface.blit(_bg_surf, (-off, 0))
        screen.surface.blit(_bg_surf, (WIDTH - off, 0))
    else:
        screen.fill((15, 10, 30))

def _draw_goal(cx, tick):
    gx = GOAL.x - cx
    gy = GOAL.y
    if -GOAL.width < gx < WIDTH:
        if _goal_surf:
            screen.surface.blit(_goal_surf, (gx, gy))
        else:
            cx2 = gx + GOAL.width // 2
            cy2 = gy + GOAL.height // 2
            for r in range(70, 10, -12):
                pulse = int(math.sin(tick * 0.08 + r * 0.3) * 20)
                col = (
                    max(0, min(255, 80  + pulse)),
                    max(0, min(255, 40  + pulse * 2)),
                    max(0, min(255, 200 + pulse))
                )
                pygame.draw.circle(screen.surface, col, (cx2, cy2),
                                   r + int(math.sin(tick * 0.1) * 5))
            inner_r = 30 + int(math.sin(tick * 0.15) * 8)
            pygame.draw.circle(screen.surface, (200, 160, 255), (cx2, cy2), inner_r)
            pygame.draw.circle(screen.surface, (255, 240, 255), (cx2, cy2), inner_r // 2)
            screen.draw.text("CEL", center=(cx2, gy - 20), fontsize=28, color=(220, 200, 255))

def reset():
    global player, enemies, cam_x, win
    player  = Player(80, float(GROUND_Y - Player.H))
    enemies = [Enemy(x, y, l, r, s) for x, y, l, r, s in ENEMIES_DATA]
    cam_x   = 0
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

def update():
    global cam_x, state, win, _tick
    _tick += 1
    if state != "game":
        return
    player.update(keyboard, PLATFORMS)
    if player.y > HEIGHT + 200:
        player.alive = False
    if not player.alive:
        state = "over"; win = False
        stop_music(); sfx("jump")
        return
    for e in enemies:
        e.update()
        if not e.alive: continue
        if player.rect.colliderect(e.rect):
            player.take_damage()
        ar = player.attack_rect
        if ar and ar.colliderect(e.rect):
            e.take_hit()
    target = player.x - WIDTH // 3
    target = max(0.0, min(target, 8000.0 - WIDTH))
    cam_x += (target - cam_x) * 0.12

    target = player.x - WIDTH // 3
    cam_x = max(0.0, min(target, 8000.0 - WIDTH))

    if player.rect.colliderect(GOAL):
        state = "over"; win = True
        stop_music(); sfx("win")

def draw():
    if   state == "menu": _draw_menu()
    elif state == "game": _draw_game()
    elif state == "over": _draw_game(); _draw_overlay()

def _draw_menu():
    _blit_bg()
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 160))
    screen.surface.blit(veil, (0, 0))
    screen.draw.text("Tales of wicked forest",
                     center=(WIDTH//2, 170), fontsize=80, color=(210, 170, 255))
    screen.draw.text("Arrows + ENTER  or mause  |  X - atack",
                     center=(WIDTH//2, 260), fontsize=28, color=(160, 140, 200))
    for i, btn in enumerate(BTN):
        lbl = MENU_LABELS[i]
        if i == 1:
            lbl = "Music: ON" if music_on else "Music: OFF"
        active = (i == sel)
        screen.draw.filled_rect(btn, (90,30,130) if active else (40,18,60))
        screen.draw.rect(btn, (240,200,255) if active else (100,70,150))
        screen.draw.text(lbl, center=btn.center, fontsize=40,
                         color=(255,235,110) if active else (200,175,255))

def _draw_game():
    _blit_bg(int(cam_x * 0.2) % WIDTH)
    cx = cam_x
    for p in PLATFORMS:
        pr = Rect(p.x - cx, p.y, p.width, p.height)
        if pr.right < 0 or pr.left > WIDTH:
            continue
        if p.height > 50:
            screen.draw.filled_rect(pr, C_GND)
            screen.draw.rect(pr, C_GND_B)
        else:
            screen.draw.filled_rect(pr, C_PLT)
            screen.draw.rect(pr, C_PLT_B)
    _draw_goal(cx, _tick)
    for e in enemies:
        e.draw(screen, cx)
    player.draw(screen, cx)
    screen.draw.text(f"HP: {player.hp} / 5", (20, 18), fontsize=44, color=(255, 80, 80))

def _draw_overlay():
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 140))
    screen.surface.blit(veil, (0, 0))
    msg = "VICTORY!" if win else "GAME OVER"
    col = (255, 210, 30) if win else (255, 60, 60)
    screen.draw.text(msg,  center=(WIDTH//2, HEIGHT//2 - 60), fontsize=100, color=col)
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
    elif i == 1:
        music_on = not music_on
        play_music() if music_on else stop_music()
    elif i == 2: sys.exit()

reset()
_init_assets()
pgzrun.go()
