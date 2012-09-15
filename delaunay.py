def main():

  import pygame
  pygame.init()
  from pygame import draw, Surface
  from pygame.draw import aaline
  from pygame.gfxdraw import box, filled_circle
  from pygame.sprite import RenderUpdates, Sprite
  Clock = pygame.time.Clock()

  import itertools
  import math
  from numpy import array
  import random
  import sys

  screen = pygame.display.set_mode((800, 600))

  class Vertex(Sprite):
    def __init__(self, size=10, round=8):
      Sprite.__init__(self)
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

  def normalized(v):
    return array(v) / math.sqrt(sum(map(lambda x: x**2, v)))

  def normal(v):
    rotation = array([[0, -1], [1, 0]])
    return normalized(rotation.dot(array(v)))

  class Edge:
    def __init__(self, vertices, thickness=5):
      print(vertices)
      self.thickness = thickness
      self.vertices = vertices
    def draw(self, surface):
      v = map(lambda v: array(v.center()), self.vertices)
      aaline(surface, (200, 200, 200), v[0], v[1])
      n = normal(v[0] - v[1])
      for o in [2, -2, 4, -4]:
        aaline(surface, (200, 200, 200), v[0] + o*n, v[1] + o*n)

  vertices = RenderUpdates(*[ Vertex() for i in xrange(50) ])

  edges = [ Edge(tuple(itertools.islice(vertices, 2))) ]

  def random_2d(space):
    return tuple([ space[i] + random.random() * space[i+2] for i in xrange(2) ])

  def shuffle_vertices(space):
    for v in vertices.sprites():
      s = screen.get_size()
      p = 25
      v.move(random_2d((p, p, s[0]-2*p, s[1]-2*p)))

  background = Surface(screen.get_size()).convert()
  background.fill((100, 120, 150))

  def bg():
    screen.blit(background, (0, 0))

  shuffle_vertices(screen)

  dirty = True

  while True:

    if dirty:
      bg()
      for e in edges:
        e.draw(screen)

    pygame.display.update(vertices.draw(screen))

    if dirty:
      pygame.display.flip()

    dirty = False

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      else:
        print event

if __name__ == '__main__':
  main()
