from pygame import Rect
import pygame

GRAVITY  = 0.65
MAX_FALL = 22
JUMP_VEL = -18
SPEED    = 6

class Player:
    W, H = 100, 160

    def __init__(self, x, y):
        self.x         = float(x)
        self.y         = float(y)
        self.vx        = 0.0
        self.vy        = 0.0
        self.on_ground = False
        self.facing    = 1
        self.hp        = 5
        self.alive     = True
        self.inv_timer = 0
        self.tick      = 0
        self.attack_timer   = 0
        self.ATTACK_DUR     = 15
        self.cooldown_timer = 0
        self.COOLDOWN       = 20
        self.idle_frames = ["hero_idle_1", "hero_idle_2", ]
        self.run_frames  = ["hero_run_1",  "hero_run_2",  "hero_run_3", "hero_run_4"]
        self.frame_list  = self.idle_frames
        self.frame_idx   = 0
        self.frame_timer = 0
        self.FRAME_DELAY = 8

    @property
    def rect(self):
        return Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def attack_rect(self):
        if self.attack_timer <= 0:
            return None
        if self.facing == 1:
            return Rect(int(self.x) + self.W, int(self.y) + 30, 60, self.H - 60)
        return Rect(int(self.x) - 60, int(self.y) + 30, 60, self.H - 60)

    def start_attack(self):
        if self.attack_timer > 0 or self.cooldown_timer > 0:
            return
        self.attack_timer = self.ATTACK_DUR

    def take_damage(self):
        if self.inv_timer > 0 or not self.alive:
            return
        self.hp -= 1
        self.inv_timer = 70
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def _set_anim(self, lst):
        if self.frame_list is not lst:
            self.frame_list = lst; self.frame_idx = 0; self.frame_timer = 0

    def update(self, keyboard, platforms):
        if not self.alive:
            return
        self.tick += 1
        if self.inv_timer     > 0: self.inv_timer     -= 1
        if self.attack_timer  > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.cooldown_timer = self.COOLDOWN
        if self.cooldown_timer > 0: self.cooldown_timer -= 1
        left  = keyboard.left  or keyboard.a
        right = keyboard.right or keyboard.d
        jump  = keyboard.up    or keyboard.w or keyboard.space
        self.vx = 0.0
        if left:  self.vx = -SPEED; self.facing = -1
        if right: self.vx =  SPEED; self.facing =  1
        if jump and self.on_ground:
            self.vy = JUMP_VEL; self.on_ground = False
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.x += self.vx
        for p in platforms:
            if Rect(int(self.x), int(self.y), self.W, self.H).colliderect(p):
                if self.vx > 0:   self.x = float(p.left - self.W)
                elif self.vx < 0: self.x = float(p.right)
                self.vx = 0.0
        self.y += self.vy
        self.on_ground = False
        for p in platforms:
            if Rect(int(self.x), int(self.y), self.W, self.H).colliderect(p):
                if self.vy >= 0:
                    self.y = float(p.top - self.H)
                    self.vy = 0.0
                    self.on_ground = True
                else:
                    self.y = float(p.bottom)
                    self.vy = 0.0
        if self.x < 0: self.x = 0.0
        if abs(self.vx) > 0.1 and self.on_ground:
            self._set_anim(self.run_frames)
        else:
            self._set_anim(self.idle_frames)
        self.frame_timer += 1
        if self.frame_timer >= self.FRAME_DELAY:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frame_list)

    def draw(self, screen, cam_x):
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 1:
            return
        sx = int(self.x) - cam_x
        sy = int(self.y)
        from pgzero.loaders import images
        surf = pygame.transform.scale(
            images.load(self.frame_list[self.frame_idx]), (self.W, self.H))
        if self.facing == -1:
            surf = pygame.transform.flip(surf, True, False)
        screen.surface.blit(surf, (sx, sy))
        ar = self.attack_rect
        if ar:
            screen.draw.filled_rect(
                Rect(ar.x - cam_x, ar.y+50, ar.width*2, ar.height /4 ), (240, 255, 255))
