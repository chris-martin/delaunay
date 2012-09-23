from delaunay.geometry import *
from nose.tools import *
from math import pi, sqrt

epsilon = 0.0001

def test_vec_eq():
  assert vec(4, 7) == vec(4, 7)

def test_vec_add():
  x = vec(1, 2) + vec(5, 11)
  print(x)
  assert x - vec(6, 13) < epsilon

def test_vec_add_tuple():
  x = vec(1, 2) + (5, 11)
  print(x)
  assert x - vec(6, 13) < epsilon

def test_vec_sub():
  x = vec(1, 2) - vec(5, 11)
  print(x)
  assert x - vec(-4, -9) < epsilon

def test_vec_sub_tuple():
  x = vec(1, 2) - (5, 11)
  print(x)
  assert x - vec(-4, -9) < epsilon

def test_vec_rsub():
  x = (1, 2) - vec(5, 11)
  print(x)
  assert x - vec(-4, -9) < epsilon

def test_vec_mult_scalar():
  x = vec(3, -4) * 5
  print(x)
  assert x - vec(15, -20) < epsilon

def test_vec_rmult_scalar():
  x = 5 * vec(3, -4)
  print(x)
  assert x - vec(15, -20) < epsilon

def test_vec_mult_vec():
  x = vec(2, 6) * vec(4, 1.5)
  print(x)
  assert x - 17 < epsilon

def test_vec_reverse():
  x = vec(2, 1)
  neg = -1 * x
  print(neg)
  assert neg + x < epsilon

def test_vec_ang_1():
  x = vec(1, 0).ang()
  print(x)
  assert x < epsilon

def test_vec_ang_2():
  x = vec(-1, 0).ang()
  print(x)
  assert x - pi < epsilon

def test_line_intersect():
  i = intersect_lines(
    ((0, 0), ( 2, 2)),
    ((2, 0), (-1, 3))
  )
  print(i)
  assert i - (1, 1) < epsilon

def test_intersect_line_circle():
  p = intersect_line_circle(
    line = ((3, 1), (4, 2)),
    circle = circle(
      center = (3, 1),
      radius = sqrt(2)
    )
  )
  print(p)
  assert all(map(
    lambda q: 1 == len(filter(lambda i: i - q < epsilon, p)),
    ( (4, 2), (2, 0) )
  ))

def test_line_ang():
  x = line((0, 0), (1, 0)).ang()
  print(x)
  assert x < epsilon

def test_line_side():
  l = line(a = (10, 10), b=(14, 11))
  top = l.side((-1000, 1000))
  bottom = l.side((1000, -1000))
  assert top != bottom
  assert l.side((1000, 0)) == bottom
  assert l.side((10, 11)) == top
  assert l.side((10, 9)) == bottom
  assert l.side((14., 11.1)) == top

def test_line_side_2():
  l = line((660, 28), (707, 113))
  assert l.side((119, 563)) == l.side((350, 255))

def test_triangle_center():
  x = triangle((1, 0), (0, 2), (0, 0)).center()
  print(x)
  assert x - (.5, 1) < epsilon

def test_bulge():
  l = line((0, 0), (1, 0))
  assert l.bulge((.5, .1)) < l.bulge((.5, .2))
  assert l.bulge((.5, -.1)) < l.bulge((.5, -.2))
  assert l.bulge((.5, .1)) < l.bulge((.5, 20))
  assert l.bulge((.5, 10)) < l.bulge((.5, 20))

def test_bulge_2():
  l = line((660, 28), (707, 113))
  p = vec(119, 563)
  assert l.bulge(p) > 0
