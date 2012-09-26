from array import array
from itertools import imap, permutations
import sys
geometry = sys.modules[__name__]
from math import sin, cos, atan2, pi, sqrt, copysign
from numbers import Real
import numpy as np

pi2 = 2 * pi
halfpi = pi / 2

def vec(*vargs, **kwargs):

  if len(vargs) == 1:
    arg = vargs[0]
    if arg is None:
      return None
    if isinstance(arg, Vec):
      return arg
    vargs = arg

  if len(vargs) == 2:
    return Vec(vargs)

  return Vec(**kwargs)

def line(*vargs, **kwargs):

  if len(vargs) == 1:
    arg = vargs[0]
    if arg is None:
      return None
    if isinstance(arg, Line):
      return arg
    vargs = arg

  if len(vargs) == 2:
    return Line(vargs)

  return Line(**kwargs)

def circle(**kwargs):
  return Circle(**kwargs)

def triangle(*vargs):
  if len(vargs) == 1:
    vargs = vargs[0]
  return Triangle(vargs)

def sign(x):
  return copysign(1, x)

def _line_between_segment(x):
  (a, b) = x
  """Does line a pass through segment b?"""
  return 0 == sum(map(a.side, b))

def overlap_line_segments(a, b):
  """Do the line segments intersect?"""
  return all(imap(_line_between_segment, permutations((a, b))))

def intersect_lines(a, b):
  """The intersection of two lines. None or a vector."""

  (a, b) = map(line, (a, b))

  """Return None if lines are parallel."""
  if a.ang() == b.ang():
    return None

  """
  The intersection of lines a and b.

  http://en.wikipedia.org/wiki/Line-line_intersection

  """
  (((x1,y1),(x2,y2)),((x3,y3),(x4,y4))) = (a, b)
  d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
  x = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / d
  y = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / d
  return Vec(x=x, y=y)

def intersect_line_circle(line, circle):
  """
  The intersection of a line with a circle.
  A list of 0, 1, or 2 distinct vectors.

  http://mathworld.wolfram.com/Circle-LineIntersection.html

  """
  r = circle.radius()
  cc = circle.center()
  line = line - cc
  (dx, dy) = line[1] - line[0]
  (p1, p2) = line
  dr = sqrt(dx**2+dy**2)
  D = p1[0]*p2[1] - p2[0]*p1[1]
  q = sqrt(r**2 * dr**2 - D**2)

  # no intersection
  if q < 0:
    return []

  i = ( Vec(x=D*dy+sign(dy)*dx*q, y=0-D*dx+abs(dy)*q),
        Vec(x=D*dy-sign(dy)*dx*q, y=0-D*dx-abs(dy)*q), )

  i = list(map(lambda i: i/dr**2 + cc, i))

  # one intersection (tangent)
  if i[0] == i[1]:
    return i[0:1]

  # two intersections
  return i

class Vec:

  """A point in a Euclidean plane."""

  __slots__ = [ '_xy', '_ang', '_mag' ]

  def __init__(self, xy=None, x=None, y=None, ang=None, mag=None):

    if xy is not None:
      xy = array('f', xy)
    elif x is not None and y is not None:
      xy = array('f', (x, y))

    if ang is not None:
      ang = ang % pi2
      """If only ang is given, mag defaults to 1."""
      if xy is None and mag is None:
        mag = 1

    (self._xy, self._ang, self._mag) = (xy, ang, mag)

  def __eq__(self, other):
    return other and tuple(self) == tuple(other)

  def __neq__(self, other):
    return not (self == other)

  def __repr__(self):
    return '<Vec x=%f y=%f>' % tuple(self)

  def __str__(self):
    return '(%f, %f)' % tuple(self)

  def __getitem__(self, i):
    """Iteration over the X and Y positions."""
    return self.xy()[i]

  def __abs__(self):
    return self.mag()

  def __add__(self, other):
    ((x1, y1), (x2, y2)) = (self.xy(), other.xy())
    return Vec([x1 + x2, y1 + y2])

  def __radd__(self, other):

    # awkward special case to work with sum()
    if not other:
      return self

    return self + other;

  def __sub__(self, other):
    ((x1, y1), (x2, y2)) = (self.xy(), other.xy())
    return Vec([x1 - x2, y1 - y2])

  def __rsub__(self, other):
    return -1 * self + other

  def __mul__(self, other):
    """
    Components are multiplied by the scalar.
    Direction is reversed if the scalar is negative.

    """
    xy = self.xy()
    return Vec([xy[0]*other, xy[1]*other])

  def __rmul__(self, other):
    return self * other

  def __div__(self, other):
    xy = self.xy()
    return Vec([xy[0]/other, xy[1]/other])

  def __cmp__(self, other):
    return cmp(self.mag(), other.mag())

  def dot(self, other):
    """Scalar (dot) product of two vectors"""
    (a, b) = (self.xy(), other.xy())
    return a[0] * b[0] + a[1] * b[1]

  def xy(self):
    xy = self._xy
    if xy is None:
      (ang, mag) = (self._ang, self._mag)
      xy = self._xy = array('f', [
        mag * cos(ang),
        mag * sin(ang)
      ])
    return xy

  def x(self):
    """X position on the Euclidean plane. Real."""
    return self.xy()[0]

  def y(self):
    """Y position on the Euclidean plane. Real."""
    return self.xy()[1]

  def ang(self):
    """Angle from origin to self. Real between 0 and 2 pi."""
    if self._ang is None:
      (x, y) = self._xy
      if (x == y == 0) == tuple(self):
        self._ang = float('nan')
      else:
        self._ang = atan2(y, x) % pi2
    return self._ang

  def mag(self):
    """The vector's L2 norm. Nonnegative real."""
    mag = self._mag
    if mag is None:
      (x, y) = self._xy
      mag = self._mag = sqrt(x**2 + y**2)
    return mag

  def unit(self):
    return self / abs(self)

  def rotate(self, ang):
    return Vec(ang = self.ang() + ang, mag = self.mag())

class Line:

  """
  A line in a Euclidean plane.
  Since two fixed points on the line are always available,
  this class may also be used to represent a line segment.
  """

  __slots__ = [ '_a', '_b', '_ang' ]

  def __init__(self, ab=None, a=None, b=None, ang=None):

    if ab is not None:
      (a, b) = ab

    (a, b) = map(vec, (a, b))

    if a is None:

      """At least one point is required"""
      if b is None:
        raise ValueError

      (a, b) = (b, a) # a is always non-None

    if a == b:
      raise ValueError

    (self._a, self._b) = (a, b)

    if ang is not None:
      ang = ang % pi
    self._ang = ang

  def __repr__(self):
    return '<Line a=%s b=%s>' % tuple(self)

  def __getitem__(self, i):
    """Iteration over two arbitrary points on the line."""
    if i == 0:
      return self.a()
    if i == 1:
      return self.b()
    raise IndexError

  def a(self):
    return self._a

  def b(self):
    b = self._b
    if b is None:
      b = self._b = self._a + Vec(ang = self.ang(), mag = 1)
    return b

  def ang(self):
    """Real between 0 and pi."""
    ang = self._ang
    if ang is None:
      ang = self._ang = (self._a - self._b).ang() % pi
    return ang

  def __add__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
      return NotImplemented
    return Line(map(lambda x: x + other, self))

  def __sub__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
      return NotImplemented
    return Line(map(lambda x: x - other, self))

  def mid(self):
    """The midpoint of a and b"""
    return sum(self) / 2

  def perp(self):
    """
    A line perpendicular to self, passing
    through the midpoint of a and b.
    """
    return Line(
      a = self.mid(),
      ang = self.ang() + halfpi
    )

  def side(self, p):
    """
    Returns -1 or 1 depending on the side of the
    line on which p resides. Which side is which
    is arbitrary but consistent.
    Uses Jarek's "2-dimensional cross-product".
    """
    p = vec(p)
    def cross(a, b):
      return a.dot(b.rotate(halfpi))
    (a, b) = self
    q = cross(p - a, b - a) < 0
    return -1 if q else 1

  def same_side(self, *ps):
    """Are all the points on the same side of self?"""
    return len(set(map(self.side, ps))) == 1

  def bulge(self, point):
    """
    A number not equal, but correlated, to
    bulge as defined by Jarek Rossignac.
    """
    c = Triangle(list(self) + [point]).circle()
    side = self.side
    return c.radius() * side(point) * side(c.center())

  def intersect(self, other):

    """The intersection of this line with another line."""
    if isinstance(other, Line):
      return intersect_lines(self, other)

    """The intersections of this line with a circle."""
    if isinstance(other, Circle):
      return intersect_line_circle(self, other)

    raise TypeError

  def overlap(self, other):

    """
    Does this line segment intersect with
    other line segment?

    """
    if isinstance(other, Line):
      return overlap_line_segments(self, other)

    raise TypeError


class Circle:

  """A circle in a Euclidean plane."""

  __slots__ = [ '_center', '_radius' ]

  def __init__(self, center, radius):
    self._center = vec(center)
    self._radius = radius

  def __repr__(self):
    return '<Circle center=%s radius=%f>' \
      % (repr(self._center), self._radius)

  def center(self):
    return self._center

  def radius(self):
    return self._radius

  def intersect(self, other):

    """The intersections of this circle with a line."""
    if isinstance(other, Line):
      return intersect_line_circle(other, self)

    raise TypeError

class Triangle:

  """
  Three distinct points in a Euclidean plane.
  The points are allowed to be collinear, but
  you probably don't want them to be.
  """

  __slots__ = [ '_points', '_center' ]

  def __init__(self, points):
    assert len(points) == 3
    self._points = list(map(vec, points))
    self._center = None

  def __getitem__(self, i):
    """Iteration over the three points."""
    return self._points[i]

  def center(self):
    """
    The circumcenter of the triangle.
    None if the points are collinear.
    """
    c = self._center
    if c is None:
      c = self._center = intersect_lines(
        Line(self[0:2]).perp(),
        Line(self[1:3]).perp(),
      )
    return c

  def circle(self):
    """The circle that circumscribes self."""
    c = self.center()
    if c is not None:
      return Circle(
        center = c,
        radius = abs(c - self[0])
      )
