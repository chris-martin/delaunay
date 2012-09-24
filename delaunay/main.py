import pygame
pygame.init()
from pygame import draw, Surface
from pygame.draw import aaline, aalines, polygon
from pygame.gfxdraw import box, filled_circle, filled_trigon
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

  def __init__(self, vertex, size=8, round=6):
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
    circ(size-4, round-4, pad+4, (100, 120, 140))
    self.rect = i.get_rect()
    self.move()

  def vertex(self):
    return self._vertex

  def move(self):
    self.rect.center = tuple(self.vertex().loc())

def draw_edge(e, surface):
  (a, b) = map(lambda v: v.loc(), e)
  m = (a - b).unit()
  n = m.rotate(math.pi/2)
  for o in [0, 1.75]:
    for o in map(lambda i: i * o, [-1, 1]):
      aaline(surface, (0, 0, 0),
        tuple(a + o*n + (4-abs(o))*m),
        tuple(b + o*n + -1.*(4-abs(o))*m)
      )

def draw_triangle(t, surface):
  ((x1, y1), (x2, y2), (x3, y3)) = map(lambda c: tuple(c.vertex().loc()), t)
  (x1, y1, x2, y2, x3, y3) = map(int, (x1, y1, x2, y2, x3, y3))
  filled_trigon(surface, x1, y1, x2, y2, x3, y3, (0, 80, 240))

# def draw_marker(loc, surface):
#   filled_circle(surface, )

class Main:

  def __init__(self):
    self._screen = pygame.display.set_mode((800, 600))
    self._M = mesh.Mesh(
      list([ self.random_point() for i in xrange(25) ])
      + [ (25, 25), (775, 25), (25, 575), (775, 575),
          (400, 20), (400, 580), (20, 300), (780, 300) ]
    )
    self._dirty = True
    self._bg = Surface(self._screen.get_size()).convert()
    self._bg.fill((150, 170, 200))
    self._vertex_sprites = Group(*map(VertexSprite, self._M.vertices()))

  def point_space(self):
    s = self._screen.get_size()
    p = 50
    return (p, p, s[0]-2*p, s[1]-2*p)

  def random_point(self):
    space = self.point_space()
    return vec([ space[i] + random.random() * space[i+2] for i in xrange(2) ])

  def bg(self):
    self._screen.blit(self._bg, (0, 0))

  def tick(self):
    if self._dirty:
      self.bg()
      for t in self._M.triangles():
        draw_triangle(t, self._screen)
      for t in self._M.triangles():
        for e in t.edges():
          draw_edge(e, self._screen)
      self._vertex_sprites.draw(self._screen)
      pygame.display.flip()
      self._dirty = False

  def event(self, e):
    pass

def main():
  main = Main()
  while True:
    Clock.tick(20)
    main.tick()
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return
      else:
        main.event(event)

if __name__ == '__main__':
  main()
