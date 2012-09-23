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

class Vertex(Sprite):

  def __init__(self, size=10, round=8):
    Sprite.__init__(self)
    self.adj = []
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

  def move(self, position):
    self.rect.center = tuple(position)

  def move_random(self, space):
    self.move(random_2d(space))

  def center(self):
    return vec(self.rect.center)

class Edge:

  def __init__(self, *vertices):
    if vertices[0] == vertices[1]:
      raise ValueError
    v = self.vertices = vertices
    self.line = line(map(lambda v: v.center(), vertices))

  def draw(self, surface):
    v = map(lambda v: v.center(), self.vertices)
    aaline(surface, (200, 200, 200), tuple(v[0]), tuple(v[1]))
    n = (v[0] - v[1]).rotate(math.pi/2).unit()
    for o in [2, -2, 4, -4]:
      aaline(surface, (200, 200, 200), tuple(v[0] + o*n), tuple(v[1] + o*n))

class Triangle:

  def __init__(self, vertices):
    cs = self.corners = map(lambda v: Corner(self, v), vertices)
    for i in xrange(3):
      cs[i].next = cs[(i+1) % 3]
      cs[i].prev = cs[(i+2) % 3]

class Corner:

  def __init__(self, triangle, vertex):
    self.triangle = triangle
    self.vertex = vertex
    self.next = self.prev = self.swing = self.unswing = None

def main():

  screen = pygame.display.set_mode((800, 600))

  vertices = Group(*[ Vertex() for i in xrange(50) ])

  edges = []

  def random_2d(space):
    return vec([ space[i] + random.random() * space[i+2] for i in xrange(2) ])

  def shuffle_vertices(space):
    for v in vertices.sprites():
      s = screen.get_size()
      p = 25
      v.move(random_2d((p, p, s[0]-2*p, s[1]-2*p)))

  shuffle_vertices(screen)

  def first_edge():
    a = min(vertices, key=lambda v: v.center().y())
    b = min(vertices, key=lambda v: (v.center()-a.center()).ang())
    return Edge(a,b)

  def add_edge(e):
    for i in xrange(2):
      e.vertices[i].adj.append(e.vertices[(i + 1)%2])
    edges.append(e)

  add_edge(first_edge())

  def distance(a, b):
    return math.sqrt(sum(map(lambda x: x**2, array(a) - array(b))))

  def first_vertex():
    e = edges[0]
    def bulge(v):
      if v.center() in e.line:
        return float('inf')
      return e.line.bulge(v.center())
    v = min(vertices, key=bulge)
    return v

  add_edge(Edge(edges[0].vertices[0], first_vertex()))

  background = Surface(screen.get_size()).convert()
  background.fill((100, 120, 150))

  def bg():
    screen.blit(background, (0, 0))

  dirty = True

  while True:

    Clock.tick(20)

    if dirty:
      bg()
      for e in edges:
        e.draw(screen)
      vertices.draw(screen)
      pygame.display.flip()
      dirty = False

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      else:
        pass#print event

if __name__ == '__main__':
  main()
