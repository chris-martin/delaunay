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
    self.rect.center = position

  def move_random(self, space):
    self.move(random_2d(space))

  def center(self):
    return self.rect.center

def normalized(vec):
  return array(vec) / math.sqrt(sum(map(lambda x: x**2, vec)))

def normal(vec):
  rotation = array([[0, -1], [1, 0]])
  return normalized(rotation.dot(array(vec)))

"""
  q: 2 (point, direction vector)-tuples
  return: the lines' intersection point
  http://en.wikipedia.org/wiki/Line-line_intersection
"""
def line_intersect(*q):
  (x1, y1) = p1 = q[0][0]
  (x2, y2) = p2 = tuple(array(p1)+array(q[0][1]))
  (x3, y3) = p3 = q[1][0]
  (x4, y4) = p4 = tuple(array(p3)+array(q[1][1]))
  d = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
  return (
    ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / d,
    ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / d,
  )

def sign(x):
  return math.copysign(1, x)

def angle(vec):
  n = normalized(vec)
  if n[0] == 0: return math.pi/2
  return math.atan(-1 * n[1] / n[0]) % (2*math.pi)

"""
  line: (point, direction)
  circle: (center, radius)
  s: vector pointing in the general direction of the
     desired intersection point
  return: the intersection point in the direction along
          the line most similar to the direction of s
  http://mathworld.wolfram.com/Circle-LineIntersection.html
"""
def line_circle_intersect(line, circle, s):
  r = circle[1]
  p1 = tuple(array(line[0]) - circle[0])
  p2 = tuple(array(p1) + array(line[1]))
  dx = p2[0] - p1[0]
  dy = p2[1] - p1[1]
  dr = math.sqrt(dx**2+dy**2)
  D = p1[0]*p2[1] - p2[0]*p1[1]
  q = math.sqrt(r**2 * dr**2 - D**2)
  I = tuple(map(
    lambda x: tuple(array(x)/dr**2 + array(circle[0])),
    ( (D*dy+sign(dy)*dx*q, 0-D*dx+abs(dy)*q),
      (D*dy-sign(dy)*dx*q, 0-D*dx-abs(dy)*q), )
  ))
  print(I)
  def angle_diff(i):
    d = angle(s) - angle(tuple(array(i)-array(line[0])))
    print(d)
    d = d % (2 * math.pi)
    if d > math.pi: d = math.pi - d
    print(d)
    return d
  return min(I, key=angle_diff)

class Edge:

  def __init__(self, *vertices):
    print(vertices)
    v = self.vertices = vertices

  def draw(self, surface):
    v = map(lambda v: array(v.center()), self.vertices)
    aaline(surface, (200, 200, 200), v[0], v[1])
    n = normal(v[0] - v[1])
    for o in [2, -2, 4, -4]:
      aaline(surface, (200, 200, 200), v[0] + o*n, v[1] + o*n)

  def np_points(self):
    return map(lambda v: array(v.center()), self.vertices)

  # vector pointing from v0 to v1
  def direction(self):
    p = self.np_points()
    return tuple(p[1] - p[0])

  # point at the center of the line segment
  def center(self):
    return tuple(sum(self.np_points()) / 2.)

  # (center point, normal direction)
  def normal(self):
    return (self.center(), normalized(self.direction()))

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
    return tuple([ space[i] + random.random() * space[i+2] for i in xrange(2) ])

  def shuffle_vertices(space):
    for v in vertices.sprites():
      s = screen.get_size()
      p = 25
      v.move(random_2d((p, p, s[0]-2*p, s[1]-2*p)))

  shuffle_vertices(screen)

  def first_edge():
    a = max(vertices, key=lambda v: v.center()[1])
    b = min(vertices, key=lambda v: angle(array(v.center())-array(a.center())))
    print(angle(array(b.center())-array(a.center())))
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
    n = e.normal()
    ev = e.vertices[0]

    """
      The distance, along the line normal to the edge,
      from the edge to the circle.
    """
    def bulge(v):
      new_edge = Edge(ev, v)
      center = line_intersect(n, new_edge.normal())
      circle = (center, distance(center, v.center()))
      return distance(e.center(), line_circle_intersect(n, circle))

    return min(vertices, key=bulge)

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
        print event

if __name__ == '__main__':
  main()
