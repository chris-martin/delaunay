import pygame
pygame.init()

import sys

window = pygame.display.set_mode((640, 480))
pygame.draw.line(window, (255, 255, 255), (0, 0), (30, 50))
pygame.display.flip()

while True: 
 for event in pygame.event.get(): 
   if event.type == pygame.QUIT: 
     sys.exit(0) 
   else: 
     print event
