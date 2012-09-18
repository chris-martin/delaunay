from delaunay import *
from nose.tools import *
import math

def test_line_intersect_1():
  assert_almost_equal(
    (1, 1),
    line_intersect(
      ((0, 0), (2, 2)),
      ((2, 0), (-4, 4))
    )
  )

def test_line_intersect_2():
  assert_almost_equal(
    (1., 1.),
    line_intersect(
      ((0., 0.), (2., 2.)),
      ((2., 0.), (-4., 4.))
    )
  )

def test_line_circle_intersect_1():
  p = line_circle_intersect(
    ((-5, -10), (40, 40)),
    ((8, 3), math.sqrt(2)),
    (0, 2),
  )
  assert_almost_equal(p, (9, 4))

def test_line_circle_intersect_2():
  p = line_circle_intersect(
    ((0, 0), (1, 1)),
    ((0, 0), math.sqrt(2)),
    (0, -2),
  )
  assert_almost_equal(p, (-1., -1.))
