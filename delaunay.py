def main():

  import pygame
  pygame.init()
  from pygame import draw, Surface
  from pygame.gfxdraw import box, filled_circle
  from pygame.sprite import RenderUpdates, Sprite
  Clock = pygame.time.Clock()

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

  vertices = RenderUpdates(*[ Vertex() for i in xrange(50) ])

  def random_2d(space):
    return tuple([ space[i] + random.random() * space[i+2] for i in xrange(2) ])

  def shuffle_vertices(space):
    for v in vertices.sprites():
      s = screen.get_size()
      p = 25
      v.move(random_2d((p, p, s[0]-2*p, s[1]-2*p)))

  background = Surface(screen.get_size()).convert()
  background.fill((100, 120, 150))
  screen.blit(background, (0, 0))

  shuffle_vertices(screen)
  pygame.display.flip()

  while True:
    pygame.display.update(vertices.draw(screen))

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit(0)
      else:
        print event

if __name__ == '__main__':
  main()
