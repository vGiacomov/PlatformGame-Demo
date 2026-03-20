from pygame import Rect
import pygame

class Enemy:
    W, H = 100, 160

    def __init__(self, x, y, left, right, speed=2.0):
        self.x         = float(x)
        self.y         = float(y)
        self.left      = float(left)
        self.right     = float(right)
        self.speed     = speed
        self.dir       = 1
        self.alive     = True
        self.hp        = 3
        self.hit_timer = 0
        self.tick      = 0
        self.run_frames  = ["enemy_run_1",  "enemy_run_2"]
        self.idle_frames = ["enemy_idle_1", "enemy_idle_2"]
        self.frame_list  = self.run_frames
        self.frame_idx   = 0
        self.frame_timer = 0
        self.FRAME_DELAY = 10

    @property
    def rect(self):
        return Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        if not self.alive:
            return
        self.tick += 1
        self.x += self.speed * self.dir
        if self.x >= self.right: self.x = self.right; self.dir = -1
        if self.x <= self.left:  self.x = self.left;  self.dir =  1
        if self.hit_timer > 0:   self.hit_timer -= 1
        lst = self.run_frames if self.speed > 0 else self.idle_frames
        if lst is not self.frame_list:
            self.frame_list = lst; self.frame_idx = 0; self.frame_timer = 0
        self.frame_timer += 1
        if self.frame_timer >= self.FRAME_DELAY:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frame_list)

    def take_hit(self):
        if self.hit_timer > 0:
            return
        self.hp -= 1
        self.hit_timer = 20
        if self.hp <= 0:
            self.alive = False

    def draw(self, screen, cam_x):
        if not self.alive:
            return
        sx = int(self.x) - cam_x
        if sx < -self.W or sx > 1930:
            return
        from pgzero.loaders import images
        surf = pygame.transform.scale(
            images.load(self.frame_list[self.frame_idx]), (self.W, self.H))
        if self.dir == -1:
            surf = pygame.transform.flip(surf, True, False)
        if self.hit_timer > 0 and (self.hit_timer // 3) % 2 == 0:
            tint = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            tint.fill((255, 60, 60, 120))
            surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        screen.surface.blit(surf, (sx, int(self.y)))
        hp_w = max(0, int((self.hp / 3) * self.W))
        screen.draw.filled_rect(Rect(sx, int(self.y) - 14, hp_w, 8), (0, 200, 0))
        screen.draw.rect(Rect(sx, int(self.y) - 14, self.W, 8), (0, 80, 0))
