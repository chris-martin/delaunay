import sys
geometry = sys.modules[__name__]
import math
from numbers import Real
import numpy as np

pi2 = 2 * math.pi

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

def sign(x):
  return math.copysign(1, x)

def intersect_lines(a, b):

  (a, b) = map(line, (a, b))

  """Return None if lines are parallel."""
  if a.ang() == b.ang():
    return None

  """The intersection of lines a and b.

  http://en.wikipedia.org/wiki/Line-line_intersection

  """
  (((x1, y1), (x2, y2)), ((x3, y3), (x4, y4))) = map(tuple, (a, b))
  d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
  x = (( x1*y2 - y1*x2 )*( x3 - x4 ) - ( x1 - x2 )*( x3*y4 - y3*x4 )) / d
  y = (( x1*y2 - y1*x2 )*( y3 - y4 ) - ( y1 - y2 )*( x3*y4 - y3*x4 )) / d
  return vec(x, y)

def intersect_line_circle(line, circle):

  """The intersection of a line with a circle.

  http://mathworld.wolfram.com/Circle-LineIntersection.html

  """
  r = circle.radius()
  line = geometry.line(line)
  line = line - circle.center()
  d = line[1] - line[0]
  p1 = line[0]
  p2 = line[1]
  dx = d.x()
  dy = d.y()
  dr = math.sqrt(dx**2+dy**2)
  D = p1[0]*p2[1] - p2[0]*p1[1]
  q = math.sqrt(r**2 * dr**2 - D**2)

  # no intersection
  if q < 0:
    return []

  i = ( vec(D*dy+sign(dy)*dx*q, 0-D*dx+abs(dy)*q),
        vec(D*dy-sign(dy)*dx*q, 0-D*dx-abs(dy)*q), )

  i = list(map(lambda i: i/dr**2 + circle.center(), i))

  # one intersection (tangent)
  if i[0] == i[1]:
    return i[0:1]

  # two intersections
  return i

class Vec:

  """A point in a Euclidean plane."""

  __slots__ = [ '_x', '_y', '_ang', '_mag' ]

  def __init__(self, xy=None, x=None, y=None, ang=None, mag=None):

    if xy is not None:
      (x, y) = xy

    # make sure everything is floating-point arithmetic
    (x, y, ang, mag) = [ None if o is None else float(o)
                         for o in (x, y, ang, mag) ]

    (self._x, self._y) = (x, y)

    if ang is not None:
      ang = ang % pi2
    self._ang = ang

    self._mag = mag

  def __eq__(self, other):
    try:
      return tuple(self) == tuple(other)
    except:
      return False

  def __neq__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return '<Vec x=%f y=%f>' % tuple(self)

  def __str__(self):
    return '(%f, %f)' % tuple(self)

  def __getitem__(self, i):
    """Iteration over the X and Y positions."""
    if i == 0:
      return self.x()
    if i == 1:
      return self.y()
    raise IndexError

  def __add__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    return Vec( x = self.x() + other.x(),
                y = self.y() + other.y(), )

  def __radd__(self, other):
    return __add__(self, other);

  def __sub__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    return Vec( x = self.x() - other.x(),
                y = self.y() - other.y(), )

  def __rsub__(self, other):
    return -1 * self + other

  def __mul__(self, other):

    """Second argument must be Real."""
    if not isinstance(other, Real):
      return NotImplemented

    """
    Components are multiplied by the scalar.
    Direction is reversed if the scalar is negative.
    """
    return Vec(map(lambda c: c * other, self))

  def __rmul__(self, other):
    return self.__mul__(other)

  def __div__(self, other):

    """Second argument must be Real."""
    if not isinstance(other, Real):
      return NotImplemented

    return self.__mul__(1. / other)

  def __cmp__(self, other):
    if isinstance(other, Real):
      return cmp(self.mag(), other)
    try:
      other = vec(other)
    except:
      return NotImplemented
    return cmp(self.mag(), other.mag())

  def x(self):
    """X position on the Euclidean plane. Real."""
    if self._x is None:
      self._x = self._mag * math.cos(self._ang)
    return self._x

  def y(self):
    """Y position on the Euclidean plane. Real."""
    if self._y is None:
      self._y = self._mag * math.sin(self._ang)
    return self._y

  def ang(self):
    """Angle from origin to self. Real between 0 and 2 pi."""
    if self._ang is None:
      self._ang = math.atan2(self._x, self._y) % pi2
    return self._ang

  def mag(self):
    """The vector's L2 norm. Nonnegative real."""
    if self._mag is None:
      self._mag = math.sqrt(self._x**2 + self._y**2)
    return self._mag

class Line:

  """A line in a Euclidean plane."""

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
      ang = ang % math.pi
    self._ang = ang

  def __getitem__(self, i):
    """Iteration over two arbitrary points on the line."""
    if i == 0:
      return self._a
    if i == 1:
      if self._b is None:
        self._b = self._a + vec(ang = self.ang(), mag = 1)
      return self._b
    raise IndexError

  def ang(self):
    """Real between 0 and pi."""
    if self._ang is None:
      self._ang = (self._a - self._b).ang() % math.pi
    return self._ang

  def __add__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    return Line(map(lambda x: x + other, self))

  def __sub__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    return Line(map(lambda x: x - other, self))

class Circle:

  """A circle in a Euclidean plane."""

  __slots__ = [ '_center', '_radius' ]

  def __init__(self, center, radius):
    self._center = vec(center)
    self._radius = radius

  def center(self):
    return self._center

  def radius(self):
    return self._radius
