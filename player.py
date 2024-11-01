import pygame
from settings import *
from pygame.math import Vector2 as vector
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, path, collision_sprites, shoot):
        super().__init__(groups)
        self.import_assets(path)
        self.frame_index = 0
        self.status = 'right'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['Level']

        self.direction = vector()
        self.pos = vector(self.rect.topleft)
        self.speed = 400

        self.old_rect = self.rect.copy()
        self.collision_sprites = collision_sprites

        self.gravity = 7
        self.jump_speed = 1200
        self.on_floor = False
        self.duck = False
        self.moving_floor = None

        self.shoot = shoot
        self.can_shoot = True
        self.shoot_time = None
        self.cooldown = COOLDOWN_TIME

    def shoot_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > self.cooldown:
                self.can_shoot = True

    def import_assets(self, path):
        self.animations = {}
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    self.animations[name] = []
            else:
                for file_name in sorted(folder[2], key = lambda string: int(string.split('.')[0])):
                    path = folder[0].replace('\\', '/') + '/' + file_name
                    surf = pygame.image.load(path).convert_alpha()
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()

        # Horizantal
        if keys[pygame.K_RIGHT]:
            self.status = 'right'
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.status = 'left'
            self.direction.x = -1
        else: self.direction.x = 0

        if keys[pygame.K_UP] and self.on_floor: self.direction.y = -self.jump_speed
        if keys[pygame.K_DOWN]: self.duck = True
        else: self.duck = False
        if keys[pygame.K_SPACE] and self.can_shoot:
            direction = vector(1,0) if self.status.split('_')[0] == 'right' else vector(-1,0)
            pos = self.rect.center + direction * 40
            y_offset = vector(0, -16) if not self.duck else vector(0, 10)
            self.shoot(pos + y_offset, direction, self)

            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def move(self, dt):
        if self.duck and self.on_floor:
            self.speed = 50
        else:
            self.speed = 400

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')


        # Gravity
        self.direction.y += self.gravity
        self.pos.y += self.direction.y * dt

        if self.moving_floor and self.moving_floor.direction.y > 0 and self.direction.y > 0:
            self.direction.y = 0
            self.rect.bottom = self.moving_floor.rect.top
            self.pos.y = self.rect.y
            self.on_floor = True

        self.rect.y = round(self.pos.y)
        self.collision('vertical')
        self.moving_floor = None
    
    def get_status(self):
        if self.direction.x == 0 and self.on_floor:
            self.status = self.status.split('_')[0] +'_idle'
        if self.direction.y != 0 and not self.on_floor:
            self.status = self.status.split('_')[0] +'_jump'
        if self.on_floor and self.duck:
            self.status = self.status.split('_')[0] +'_duck'

    def check_contact(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 5)
        bottom_rect.midtop = self.rect.midbottom
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(bottom_rect):
                if self.direction.y > 0:
                    self.on_floor = True
                if hasattr(sprite, 'direction'):
                    self.moving_floor = sprite

    def animate(self, dt):
        self.frame_index += 7 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    # left collision
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                    # right collision
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left


                    self.pos.x = self.rect.x

                else: pass
                if direction == 'vertical':
                    # top collision
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.direction.y = -1
                    # botom collision
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.direction.y = 0
                    self.on_floor = True



                    self.pos.y = self.rect.y
                    

                else: pass

        if self.on_floor and self.direction.y != 0:
            self.on_floor = False

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
        self.get_status()
        self.shoot_timer()
        self.move(dt)
        self.check_contact()
        self.animate(dt)