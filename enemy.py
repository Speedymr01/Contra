import pygame
from settings import *
from pygame.math import Vector2 as vector
from entity import Entity

class Enemy(Entity):
    def __init__(self, pos, path, groups, shoot, player, collision_sprites):
        super().__init__(pos, path, groups, shoot)
        self.player = player
        for sprite in collision_sprites.sprites():
            if sprite.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = sprite.rect.top
