from delaunay.geometry import *
from nose.tools import *
from math import pi, sqrt

epsilon = 0.0001

def small(v):
  return v.mag() < epsilon

def test_vec_eq():
  assert vec(4, 7) == vec(4, 7)

def test_vec_add():
  x = vec(1, 2) + vec(5, 11)
  print(x)
  assert small(x - vec(6, 13))

def test_vec_add_tuple():
  x = vec(1, 2) + vec(5, 11)
  print(x)
  assert small(x - vec(6, 13))

def test_vec_sub():
  x = vec(1, 2) - vec(5, 11)
  print(x)
  assert small(x - vec(-4, -9))

def test_vec_sub_tuple():
  x = vec(1, 2) - vec(5, 11)
  print(x)
  assert small(x - vec(-4, -9))

def test_vec_rsub():
  x = vec(1, 2) - vec(5, 11)
  print(x)
  assert small(x - vec(-4, -9))

def test_vec_mult_scalar():
  x = vec(3, -4) * 5
  print(x)
  assert small(x - vec(15, -20))

def test_vec_rmult_scalar():
  x = 5 * vec(3, -4)
  print(x)
  assert small(x - vec(15, -20))

def test_vec_dot():
  x = vec(2, 6).dot(vec(4, 1.5))
  print(x)
  assert x - 17 < epsilon

def test_vec_reverse():
  x = vec(2, 1)
  neg = -1 * x
  print(neg)
  assert small(neg + x)

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
    line((0, 0), ( 2, 2)),
    line((2, 0), (-1, 3)),
  )
  print(i)
  assert small(i - vec(1, 1))

def test_intersect_line_circle():
  p = intersect_line_circle(
    line = line((3, 1), (4, 2)),
    circle = circle(
      center = vec(3, 1),
      radius = sqrt(2)
    )
  )
  print(p)
  assert all(map(
    lambda q: 1 == len(filter(lambda i: small(i - q), p)),
    ( vec(4, 2), vec(2, 0) )
  ))

def test_line_ang():
  x = line((0, 0), (1, 0)).ang()
  print(x)
  assert x < epsilon

def test_line_side():
  l = line((10, 10), (14, 11))
  top = l.side(vec(-1000, 1000))
  bottom = l.side(vec(1000, -1000))
  assert top != bottom
  assert l.side(vec(1000, 0)) == bottom
  assert l.side(vec(10, 11)) == top
  assert l.side(vec(10, 9)) == bottom
  assert l.side(vec(14., 11.1)) == top

def test_line_side_2():
  l = line((660, 28), (707, 113))
  assert l.side(vec(119, 563)) == l.side(vec(350, 255))

def test_triangle_center():
  x = triangle(vec(1, 0), vec(0, 2), vec(0, 0)).center()
  print(x)
  assert small(x - vec(.5, 1))

def test_bulge():
  l = line((0, 0), (1, 0))
  assert l.bulge(vec(.5, .1)) < l.bulge(vec(.5, .2))
  assert l.bulge(vec(.5, -.1)) < l.bulge(vec(.5, -.2))
  assert l.bulge(vec(.5, .1)) < l.bulge(vec(.5, 20))
  assert l.bulge(vec(.5, 10)) < l.bulge(vec(.5, 20))

def test_bulge_2():
  l = line((660, 28), (707, 113))
  p = vec(119, 563)
  assert l.bulge(p) > 0
