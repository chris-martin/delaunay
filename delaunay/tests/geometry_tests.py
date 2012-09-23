from delaunay.geometry import *
from nose.tools import *
import math

epsilon = 0.0001

def test_vec_eq():
  assert vec(4, 7) == vec(4, 7)

def test_vec_add():
  assert vec(1, 2) + vec(5, 11) - vec(6, 13) < epsilon

def test_vec_add_tuple():
  assert vec(1, 2) + (5, 11) - vec(6, 13) < epsilon

def test_vec_sub():
  assert vec(1, 2) - vec(5, 11) - vec(-4, -9) < epsilon

def test_vec_sub_tuple():
  assert vec(1, 2) - (5, 11) - vec(-4, -9) < epsilon

def test_vec_rsub():
  assert (1, 2) - vec(5, 11) - vec(-4, -9) < epsilon

def test_vec_reverse():
  x = vec(2, 1)
  assert -1 * x + x < epsilon

def test_line_intersect():
  i = intersect_lines(
    ((0, 0), (2, 2)),
    ((2, 0), (-1, 3))
  )
  assert i - (1, 1) < epsilon

def test_intersect_line_circle():
  p = intersect_line_circle(
    line = ((3, 1), (4, 2)),
    circle = circle(
      center = (3, 1),
      radius = math.sqrt(2)
    )
  )
  assert all(map(
    lambda q: 1 == len(filter(lambda i: i - q < epsilon, p)),
    ( (4, 2), (2, 0) )
  ))
