import pygame
pygame.init()
from pygame import draw, Surface
from pygame.draw import aaline
from pygame.gfxdraw import box, filled_circle
from pygame.sprite import Group, Sprite
Clock = pygame.time.Clock()

import itertools
import math
from numpy import array
import random
import sys

from geometry import vec, line
import mesh

class VertexSprite(Sprite):

  def __init__(self, vertex, size=10, round=8):
    Sprite.__init__(self)
    self._vertex = vertex
    background = (255, 0, 255)
    pad = 2
    self.image = i = Surface((2*size+2*pad, 2*size+2*pad))
    i.set_colorkey(background)
    i.fill(background)
    # s: size, r: rounding, p: padding, c: color
    def circ(s, r, p, c):
      filled_circle(i, p+r, p+r, r, c)
      filled_circle(i, p+2*s-r, p+r, r, c)
      filled_circle(i, p+r, p+2*s-r, r, c)
      filled_circle(i, p+2*s-r, p+2*s-r, r, c)
      box(i, (p+r, p+0, 2*s-2*r, 2*s+1), c)
      box(i, (p+0, p+r, 2*s+1, 2*s-2*r), c)
    circ(size, round, pad, (0, 0, 0))
    circ(size-1, round-1, pad+1, (255, 255, 255))
    self.rect = i.get_rect()
    self.move()

  def vertex(self):
    return self._vertex

  def move(self):
    self.rect.center = tuple(self.vertex().loc())

def draw_edge(e, surface):
  (a, b) = map(lambda v: v.loc(), e)
  aaline(surface, (200, 200, 200), tuple(a), tuple(b))
  n = (a - b).rotate(math.pi/2).unit()
  for o in [2, 4]:
    for o in map(lambda i: i * o, [-1, 1]):
      aaline(surface, (200, 200, 200), tuple(a + o*n), tuple(b + o*n))

def main():

  screen = pygame.display.set_mode((800, 600))
  def point_space():
    s = screen.get_size()
    p = 50
    return (p, p, s[0]-2*p, s[1]-2*p)
  def random_point():
    space = point_space()
    return vec([ space[i] + random.random() * space[i+2] for i in xrange(2) ])
  M = mesh.Mesh(list([ random_point() for i in xrange(20) ]))
  print(M)
  vertex_sprites = Group(*map(VertexSprite, M.vertices()))

  background = Surface(screen.get_size()).convert()
  background.fill((100, 120, 150))

  def bg():
    screen.blit(background, (0, 0))

  dirty = True

  while True:

    Clock.tick(20)

    if dirty:
      bg()
      for t in M.triangles():
        for e in t.edges():
          draw_edge(e, screen)
      vertex_sprites.draw(screen)
      pygame.display.flip()
      dirty = False

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      else:
        pass#print event

if __name__ == '__main__':
  main()
