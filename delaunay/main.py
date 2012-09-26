import cProfile

import pygame
pygame.init()
from pygame import draw, Surface, MOUSEMOTION
from pygame.draw import aaline, aalines, polygon
from pygame.gfxdraw import box, filled_circle, filled_trigon
from pygame.sprite import Group, Sprite
Clock = pygame.time.Clock()

import itertools
from itertools import imap
import math
from numpy import array
import random
import sys
import time

from geometry import Vec, vec, line
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

class Edge:

  __slots__ = [ '_edge', '_flash_time' ]

  def __init__(self, mesh_edge):
    self._mesh_edge = mesh_edge
    self._flash_time = None

  def draw(self, surface):
    (a, b) = self.line()
    m = (a - b).unit()
    n = m.rotate(math.pi/2)
    flash = 0
    if self._flash_time:
      d = time.time() - self._flash_time
      if d > 1:
        self._flash_time = None
      else:
        flash = 1 - d
    def draw_line(o):
      aaline(surface, (255 * flash, 255 * flash, 0),
        tuple(a + o*n + (4-abs(o))*m),
        tuple(b + o*n + -1.*(4-abs(o))*m)
      )
    map(draw_line, [0, -1.75, 1.75])

  def line(self):
    return line(map(lambda v: v.loc(), self._mesh_edge))

  def is_dirty(self):
    return self._flash_time is not None

  def flash(self):
    self._flash_time = time.time()

def draw_triangle(t, surface, marked=False):
  ((x1, y1), (x2, y2), (x3, y3)) = map(lambda c: tuple(c.vertex().loc()), t)
  (x1, y1, x2, y2, x3, y3) = map(int, (x1, y1, x2, y2, x3, y3))
  color = (0, 80, 240) if not marked else (160, 100, 200)
  filled_trigon(surface, x1, y1, x2, y2, x3, y3, color)

def draw_marker(loc, surface):
  (x, y) = map(int, loc)
  filled_circle(surface, x, y, 5, (255, 0, 0))

class Main:

  def __init__(self):
    self._screen = pygame.display.set_mode((800, 600))
    self.restart()

  def restart(self):
    self._M = mesh.Mesh(
      [self.random_point() for i in xrange(50)]
      + [ (25, 25), (775, 25), (25, 575), (775, 575),
          (400, 20), (400, 580), (20, 300), (780, 300) ]
    )
    self._marker = self._M.triangles()[0][0]
    self._dirty = True
    self._bg = Surface(self._screen.get_size()).convert()
    self._bg.fill((150, 170, 200))
    self._vertex_sprites = Group(*map(VertexSprite, self._M.vertices()))
    self._edges = map(Edge, self._M.edges())
    [ e.flash() for e in self._edges ]

  def point_space(self):
    s = self._screen.get_size()
    p = 50
    return (p, p, s[0]-2*p, s[1]-2*p)

  def random_point(self):
    space = self.point_space()
    return Vec([ space[i] + random.random() * space[i+2] for i in range(2) ])

  def bg(self):
    self._screen.blit(self._bg, (0, 0))

  def draw(self):

    if self._dirty or any(imap(lambda e: e.is_dirty(), self._edges)):

      screen = self._screen
      marker = self._marker
      marker_triangle = marker.triangle()

      self.bg()
      [ draw_triangle(t, screen, t == marker_triangle)
        for t in self._M.triangles() ]
      [ e.draw(screen) for e in self._edges ]
      self._vertex_sprites.draw(screen)
      draw_marker(marker.loc(), screen)
      pygame.display.flip()
      self._dirty = False

  def mouse_motion(self, motion):
    overlap = motion.overlap
    [ e.flash() for e in self._edges if overlap(e.line()) ]

  def event(self, e):
    if e.type == MOUSEMOTION:
      (pos, rel) = map(lambda p: Vec(e.dict[p]), ('pos', 'rel'))
      motion = line(pos-rel, pos)
      self.mouse_motion(motion)
    elif e.type == pygame.KEYDOWN:
      (key, mod) = map(lambda p: e.dict[p], ('key', 'mod'))
      shift = mod & pygame.KMOD_SHIFT
      if key == pygame.K_n:
        self._marker = self._marker.next()
      if key == pygame.K_p:
        self._marker = self._marker.prev()
      if key == pygame.K_s:
        self._marker = self._marker.swing(sup = shift)
      if key == pygame.K_u:
        self._marker = self._marker.unswing(sup = shift)
      if key == pygame.K_r:
        self.restart()
      self._dirty = True

def main():

  main = Main()
  main_event = main.event
  get_events = pygame.event.get

  def handle_event(event):
    if event.type == pygame.QUIT:
      sys.exit(0)
    else:
      main_event(event)

  while True:
    Clock.tick(10)
    main.draw()
    map(handle_event, get_events())

if __name__ == '__main__':
  #cProfile.run("main()")
  main()
