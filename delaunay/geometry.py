import sys
geometry = sys.modules[__name__]
import math
from math import pi
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
  return math.copysign(1, x)

def intersect_lines(a, b):
  """None or a vector."""

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
  return vec(x, y)

def intersect_line_circle(line, circle):
  """
  The intersection of a line with a circle.
  A list of 0, 1, or 2 distinct vectors.

  http://mathworld.wolfram.com/Circle-LineIntersection.html

  """
  r = circle.radius()
  line = geometry.line(line)
  line = line - circle.center()
  (dx, dy) = line[1] - line[0]
  (p1, p2) = line
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
      """If only ang is given, mag defaults to 1."""
      if all(map(lambda o: o is None, (x, y, mag))):
        mag = 1
    self._ang = ang

    self._mag = mag

  def __eq__(self, other):
    try:
      return tuple(self) == tuple(other)
    except:
      return False

  def __neq__(self, other):
    return not (self == other)

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

  def __abs__(self):
    return self.mag()

  def __add__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
      return NotImplemented
    return Vec( x = self.x() + other.x(),
                y = self.y() + other.y(), )

  def __radd__(self, other):

    # awkward special case to work with sum()
    if not other:
      return self

    return self + other;

  def __sub__(self, other):
    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
      return NotImplemented
    return Vec( x = self.x() - other.x(),
                y = self.y() - other.y(), )

  def __rsub__(self, other):
    return -1 * self + other

  def __mul__(self, other):

    if isinstance(other, Real):
      """
      Components are multiplied by the scalar.
      Direction is reversed if the scalar is negative.
      """
      return Vec(map(lambda c: c * other, self))

    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
      return NotImplemented

    """Scalar (dot) product of two vectors"""
    return self.x() * other.x() + self.y() * other.y()

  def __rmul__(self, other):
    return self * other

  def __div__(self, other):

    """Second argument must be Real."""
    if not isinstance(other, Real):
      return NotImplemented

    return self * (1. / other)

  def __cmp__(self, other):
    if isinstance(other, Real):
      return cmp(self.mag(), other)
    try:
      other = vec(other)
    except:
      return NotImplemented
    if other is None:
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
      if (0, 0) == tuple(self):
        self._ang = float('nan')
      else:
        self._ang = math.atan2(self._y, self._x) % pi2
    return self._ang

  def mag(self):
    """The vector's L2 norm. Nonnegative real."""
    if self._mag is None:
      self._mag = math.sqrt(self._x**2 + self._y**2)
    return self._mag

  def unit(self):
    return self / abs(self)

  def rotate(self, ang):
    return vec(ang = self.ang() + ang, mag = self.mag())

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
    if self._b is None:
      self._b = self._a + vec(ang = self.ang(), mag = 1)
    return self._b

  def ang(self):
    """Real between 0 and pi."""
    if self._ang is None:
      self._ang = (self._a - self._b).ang() % pi
    return self._ang

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
    def cross(a, b):
      return a * b.rotate(halfpi)
    q = cross(p - self.a(), self.b() - self.a()) < 0
    return -1 if q else 1

  def same_side(self, *ps):
    """Are all the points on the same side of self?"""
    return len(set(map(lambda p: self.side(p), ps))) == 1

  def bulge(self, point):
    """
    A number not equal, but correlated, to
    bulge as defined by Jarek Rossignac.
    """
    c = triangle(list(self) + [point]).circle()
    print(c)
    return c.radius() * self.side(point) * self.side(c.center())

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
    if self._center is None:
      ab = line(self[0], self[1])
      ac = line(self[0], self[2])
      self._center = intersect_lines(ab.perp(), ac.perp())
    return self._center

  def circle(self):
    """The circle that circumscribes self."""
    c = self.center()
    if c is not None:
      return circle(
        center = c,
        radius = abs(c - self[0])
      )
