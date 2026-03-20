import pgzero
from pygame import Rect

GRAVITY         = 0.65
MAX_FALL        = 22
JUMP_VEL        = -18
SPEED           = 6
INV_DURATION    = 70
ATTACK_DURATION = 15
ATTACK_COOLDOWN = 20
FRAME_DELAY     = 8


class Player:
    W, H   = 100, 160
    MAX_HP = 5

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = self.vy   = 0.0
        self.on_ground      = False
        self.facing         = 1
        self.hp             = self.MAX_HP
        self.alive          = True
        self.inv_timer      = 0
        self.attack_timer   = 0
        self.cooldown_timer = 0
        self.idle_frames = ["hero_idle_1", "hero_idle_2"]
        self.run_frames  = ["hero_run_1", "hero_run_2", "hero_run_3", "hero_run_4"]
        self.frame_list  = self.idle_frames
        self.frame_idx   = 0
        self.frame_timer = 0

    @property
    def rect(self):
        return Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def attack_rect(self):
        if self.attack_timer <= 0:
            return None
        ox = self.W if self.facing == 1 else -60
        return Rect(int(self.x) + ox, int(self.y) + 30, 60, self.H - 60)

    def start_attack(self):
        if self.attack_timer <= 0 and self.cooldown_timer <= 0:
            self.attack_timer = ATTACK_DURATION

    def take_damage(self):
        if self.inv_timer > 0 or not self.alive:
            return
        self.hp -= 1
        self.inv_timer = INV_DURATION
        if self.hp <= 0:
            self.hp = 0; self.alive = False

    def _set_anim(self, lst):
        if self.frame_list is not lst:
            self.frame_list  = lst
            self.frame_idx   = 0
            self.frame_timer = 0

    def _advance_frame(self):
        self.frame_timer += 1
        if self.frame_timer >= FRAME_DELAY:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frame_list)

    def _tick_timers(self):
        if self.inv_timer > 0:
            self.inv_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.cooldown_timer = ATTACK_COOLDOWN
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

    def _handle_input(self, keyboard):
        self.vx = 0.0
        if keyboard.left  or keyboard.a: self.vx = -SPEED; self.facing = -1
        if keyboard.right or keyboard.d: self.vx =  SPEED; self.facing =  1
        if (keyboard.up or keyboard.w or keyboard.space) and self.on_ground:
            self.vy = JUMP_VEL; self.on_ground = False

    def _move_x(self, platforms):
        self.x += self.vx
        r = self.rect
        for p in platforms:
            if r.colliderect(p):
                self.x  = float(p.left - self.W) if self.vx > 0 else float(p.right)
                self.vx = 0.0
                r = self.rect

    def _move_y(self, platforms):
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.y += self.vy
        self.on_ground = False
        r = self.rect
        for p in platforms:
            if r.colliderect(p):
                if self.vy >= 0:
                    self.y = float(p.top - self.H); self.on_ground = True
                else:
                    self.y = float(p.bottom)
                self.vy = 0.0
                r = self.rect

    def update(self, keyboard, platforms):
        if not self.alive:
            return
        self._tick_timers()
        self._handle_input(keyboard)
        self._move_x(platforms)
        self._move_y(platforms)
        self.x = max(0.0, self.x)
        self._set_anim(self.run_frames if abs(self.vx) > 0.1 and self.on_ground else self.idle_frames)
        self._advance_frame()

    def draw(self, screen, cam_x):
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 1:
            return
        sx = int(self.x) - cam_x
        import pygame as _pg
        from pgzero.loaders import images
        surf = _pg.transform.scale(images.load(self.frame_list[self.frame_idx]), (self.W, self.H))
        if self.facing == -1:
            surf = _pg.transform.flip(surf, True, False)
        screen.surface.blit(surf, (sx, int(self.y)))
        ar = self.attack_rect
        if ar:
            screen.draw.filled_rect(
                Rect(ar.x - cam_x, ar.y + 50, ar.width * 2, ar.height // 4),
                (240, 255, 255))
