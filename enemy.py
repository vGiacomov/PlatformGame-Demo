import pgzero
from pygame import Rect


class Enemy:
    W, H         = 100, 160
    MAX_HP       = 3
    HIT_COOLDOWN = 20
    FRAME_DELAY  = 10

    def __init__(self, x, y, left, right, speed=2.0):
        self.x      = float(x)
        self.y      = float(y)
        self.left   = float(left)
        self.right  = float(right)
        self.speed  = speed
        self.dir    = 1
        self.alive  = True
        self.hp     = self.MAX_HP
        self.hit_timer   = 0
        self.run_frames  = ["enemy_run_1",  "enemy_run_2"]
        self.idle_frames = ["enemy_idle_1", "enemy_idle_2"]
        self.frame_list  = self.run_frames
        self.frame_idx   = 0
        self.frame_timer = 0

    @property
    def rect(self):
        return Rect(int(self.x), int(self.y), self.W, self.H)

    def _set_anim(self, lst):
        if self.frame_list is not lst:
            self.frame_list  = lst
            self.frame_idx   = 0
            self.frame_timer = 0

    def _advance_frame(self):
        self.frame_timer += 1
        if self.frame_timer >= self.FRAME_DELAY:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frame_list)

    def update(self):
        if not self.alive:
            return
        self.x += self.speed * self.dir
        if self.x >= self.right: self.x = self.right; self.dir = -1
        if self.x <= self.left:  self.x = self.left;  self.dir =  1
        if self.hit_timer > 0:
            self.hit_timer -= 1
        self._set_anim(self.run_frames if self.speed > 0 else self.idle_frames)
        self._advance_frame()

    def take_hit(self):
        if self.hit_timer > 0:
            return
        self.hp -= 1
        self.hit_timer = self.HIT_COOLDOWN
        if self.hp <= 0:
            self.alive = False

    def draw(self, screen, cam_x):
        if not self.alive:
            return
        sx = int(self.x) - cam_x
        if not (-self.W < sx < 1930):
            return
        import pygame as _pg
        from pgzero.loaders import images
        surf = _pg.transform.scale(images.load(self.frame_list[self.frame_idx]), (self.W, self.H))
        if self.dir == -1:
            surf = _pg.transform.flip(surf, True, False)
        screen.surface.blit(surf, (sx, int(self.y)))
        hp_w = max(0, int((self.hp / self.MAX_HP) * self.W))
        sy   = int(self.y) - 14
        screen.draw.filled_rect(Rect(sx, sy, hp_w,   8), (0, 200, 0))
        screen.draw.rect(       Rect(sx, sy, self.W, 8), (0,  80, 0))
