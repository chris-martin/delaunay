from collections import defaultdict
from itertools import chain, imap, permutations

import geometry
from geometry import vec

class Mesh:

  """A triangle mesh."""

  __slots__ = [ '_triangles', '_vertices' ]

  def __init__(self, points):
    d = Delaunay(points)
    self._triangles = d._triangles
    self._vertices = d._vertices

  def __str__(self):
    return 'Mesh with %d triangles' % len(self._triangles)

  def triangles(self):
    return self._triangles

  def vertices(self):
    return self._vertices

  def edges(self):
    return set(chain(*imap(lambda t: t.edges(), self._triangles)))

class Edge:

  """A pair of distinct vertices."""

  __slotes__ = [ '_a', '_b' ]

  def __init__(self, a, b):
    if a == b:
      raise ValueError
    self._a = a
    self._b = b

  def line(self):
    return geometry.line(map(lambda v: v.loc(), self))

  def __getitem__(self, i):
    """Iteration over the vertices."""
    if i == 0:
      return self._a
    if i == 1:
      return self._b
    raise IndexError

  def __eq__(self, other):
    (a, b) = tuple(self)
    other = tuple(other)
    return (a, b) == other or (b, a) == other

  def __neq__(self, other):
    return not (self == other)

  def __hash__(self):
    (x, y) = [hash(t) for t in permutations(tuple(self))]
    return x^y

class Triangle:

  """A triangle belonging to a mesh."""

  __slots__ = [ '_corners' ]

  def __init__(self, vertices):
    assert len(vertices) == 3

    """Vertices are sorted in clockwise rotation."""
    t = geometry.triangle(map(lambda v: v.loc(), vertices))
    c = t.center()
    vertices = sorted(vertices, key=lambda v: (v.loc() - c).ang())

    def corner(v):
      return Corner(triangle = self, vertex = v)
    self._corners = list(map(corner, vertices))

  def __getitem__(self, i):
    """Iteration over the three corners."""
    return self._corners[i]

  def corner_step(self, corner, step):
    cs = self._corners
    return cs[(cs.index(corner) + step) % 3]

  def vertices(self):
    return map(lambda c: c.vertex(), self)

  def edges(self):
    vs = self.vertices()
    return list([ Edge(vs[i], vs[(i+1)%3])
      for i in xrange(3) ])

  def __eq__(self, other):
    return set(self.vertices()) == set(other.vertices())

  def __neq__(self, other):
    return not (self == other)

class Vertex:

  """The vertex of one of more mesh triangles."""

  __slots__ = [ '_loc', '_corner' ]

  def __init__(self, loc):
    self._loc = vec(loc)
    self._corner = None

  def loc(self, new_loc = None):
    if new_loc is None:
      return self._loc
    self._loc = new_loc

  def corner(self):
    """One arbitrary corner."""
    return self._corner

class Corner:

  """A mesh triangle has three corners."""

  __slots__ = [ '_triangle', '_vertex', '_swing' ]

  def __init__(self, triangle, vertex):
    self._triangle = triangle
    self._vertex = vertex
    self._swing = Swings()
    if vertex._corner is None:
      vertex._corner = self

  def vertex(self):
    return self._vertex

  def triangle(self):
    return self._triangle

  def loc(self):
    return self.vertex().loc()

  def next(self):
    return self._triangle.corner_step(self, 1)

  def prev(self):
    return self._triangle.corner_step(self, -1)

  def swing(self, rev=False, sup=False):
    swing = self._swing[rev]
    if swing.sup and not sup:
      return self
    c = swing.corner
    assert c is not None
    return c

  def super_swing(self):
    return self.swing(sup=True)

  def unswing(self, sup=False):
    return self.swing(rev=True, sup=sup)

  def super_unswing(self):
    return self.swing(rev=True, sup=True)

class Swings:

  __slots__ = [ 'next', 'prev' ]

  def __init__(self):
    self.next = Swing()
    self.prev = Swing()

  def __getitem__(self, i):
    if i == 0: return self.next
    if i == 1: return self.prev
    raise IndexError

class Swing:

  __slots__ = [ 'corner', 'sup' ]

  def __init__(self):
    self.corner = None
    self.sup = False

class Delaunay:

  def __init__(self, points):
    """Do a Delaunay triangulation about the given points."""
    assert len(points) >= 3
    self._triangles = []
    self._vertices = map(Vertex, points)
    self._edges = []
    self._open_edges = {}
    first_edge = self.first_edge()
    self._edges.append(first_edge)
    self._open_edges[first_edge] = None
    while len(self._open_edges) != 0:
      self.try_next_edge()
    self.calculate_swing()

  def first_edge(self):
    a = min(self._vertices, key = lambda v: v.loc().y())
    b = min(
      [v for v in self._vertices if v is not a],
      key = lambda v: (v.loc() - a.loc()).ang()
    )
    return Edge(a, b)

  def try_next_edge(self):
    (edge, previous_vertex) = self._open_edges.iteritems().next()
    del self._open_edges[edge]
    line = edge.line()
    if previous_vertex is None:
      candidate_vertices = [v for v in self._vertices
        if v not in edge]
    else:
      if self.is_boundary_edge(edge):
        return
      side = -1 * line.side(previous_vertex.loc())
      candidate_vertices = [v for v in self._vertices
        if v not in edge and line.side(v.loc()) == side]
    v = min(candidate_vertices, key = lambda v: line.bulge(v.loc()))
    t = Triangle(list(edge) + [v])
    self._triangles.append(t)
    for (u, w) in permutations(edge):
      uv = Edge(u, v)
      if uv in self._open_edges:
        del self._open_edges[uv]
      else:
        self._edges.append(uv)
        self._open_edges[uv] = w

  def is_boundary_edge(self, e):
    vertices = [ v.loc() for v in self._vertices if v not in e ]
    return e.line().same_side(*vertices)

  def calculate_swing(self):
    v2c = defaultdict(list)
    for t in self._triangles:
      for c in t:
        v2c[c.vertex()].append(c)
    for cs in v2c.itervalues():
      for i in cs:
        for j in cs:
          if i.next().vertex() == j.prev().vertex():
            j._swing.next.corner = i
            i._swing.prev.corner = j
      sups = [None, None]
      for i in cs:
        if i._swing.next.corner is None:
          assert sups[0] is None
          sups[0] = i
        if i._swing.prev.corner is None:
          assert sups[1] is None
          sups[1] = i
      if sups[0] is not None:
        sups[0]._swing.next.corner = sups[1]
        sups[0]._swing.next.sup = True
        sups[1]._swing.prev.corner = sups[0]
        sups[1]._swing.prev.sup = True
