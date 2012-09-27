package org.chris_martin.delaunay;

import org.chris_martin.delaunay.Geometry.Line;
import org.chris_martin.delaunay.Geometry.Vec;

import java.util.*;
import java.util.Map.Entry;

import static java.util.Collections.min;
import static java.util.Collections.unmodifiableCollection;
import static org.chris_martin.delaunay.Geometry.aToB;
import static org.chris_martin.delaunay.Geometry.circle;
import static org.testng.collections.Lists.newArrayList;
import static org.testng.collections.Maps.newHashMap;

public final class Mesh {

  private int previousVertexId;

  private List<Triangle> triangles;
  public Collection<Triangle> triangles() { return unmodifiableCollection(triangles); }

  private List<Vertex> vertices;
  public Collection<Vertex> vertices() { return unmodifiableCollection(vertices); }

  private void setPoints(Collection<Vec> points) {
    Delaunay d = new Delaunay(points);
    triangles = d.triangles;
    vertices = d.vertices;
  }

  public class Vertex {
    private final int id = ++previousVertexId;
    private Vec loc;
    private Corner corner;
    private Vertex(Vec loc) { this.loc = loc; }
    public int id() { return id; }
    public Vec loc() { return loc; }
    public Corner corner() { return corner; }
    public int hashCode() { return id; }
  }

  public class Corner {
    private Triangle triangle;
    private Vertex vertex;
    private Swings swings;
    private Corner(Vertex vertex, Triangle triangle) {
      this.vertex = vertex; this.triangle = triangle;
      if (vertex.corner == null) vertex.corner = this; }
    public Corner swing(boolean isSuper) { return swings.next.get(isSuper); }
    public Corner unswing(boolean isSuper) { return swings.prev.get(isSuper); }
  }
  private class Swings {
    Swing prev = new Swing(), next = new Swing();
  }
  private class Swing {
    Corner corner; boolean isSuper;
    Corner get(boolean allowSuper) { return isSuper && !allowSuper ? null : corner; }
  }

  public class Edge {
    private final Vertex a, b;
    private Edge(Vertex a, Vertex b) {
      boolean flip = a.id > b.id;
      this.a = flip ? b : a; this.b = flip ? a : b; }
    public Vertex a() { return a; }
    public Vertex b() { return b; }
    public Line line() { return aToB(a.loc, b.loc); }
    public boolean equals(Object o) {
      return this == o || (o instanceof Edge && a == ((Edge) o).a && b == ((Edge) o).b); }
    public int hashCode() { return 31 * a.hashCode() + b.hashCode(); }
  }

  public class Triangle {
    private final Corner a, b, c;
    public Triangle(Vertex a, Vertex b, Vertex c) {
      // vertices are sorted in clockwise rotation about the circumcenter
      final Vec cc = circle(a.loc(), b.loc(), c.loc()).center();
      class X { final double ang; final Vertex v; X(Vertex v) { this.v = v; ang = v.loc().sub(cc).ang(); } }
      X[] xs = { new X(a), new X(b), new X(c) };
      Arrays.sort(xs, new Comparator<X>() { public int compare(X a, X b) { return Double.compare(a.ang, b.ang); }});
      this.a = new Corner(xs[0].v, this); this.b = new Corner(xs[1].v, this); this.c = new Corner(xs[2].v, this);
    }

  }

  private class Delaunay {

    List<Triangle> triangles = newArrayList();
    List<Vertex> vertices = newArrayList();
    List<Edge> edges = newArrayList();
    Map<Edge, Vertex> openEdges = newHashMap();

    Delaunay(Collection<Vec> points) {
      if (points.size() < 3) throw new IllegalArgumentException();
      for (Vec p : points) vertices.add(new Vertex(p));
      Edge firstEdge = firstEdge();
      edges.add(firstEdge);
      openEdges.put(firstEdge, null);
      while (openEdges.size() != 0) tryNextEdge();
      calculateSwing();
    }

    Edge firstEdge() {
      final Vertex a = min(vertices, new Comparator<Vertex>() {
        public int compare(Vertex i, Vertex j) { return Double.compare(key(i), key(j)); }
        double key(Vertex v) {return v.loc().y(); }
      });
      Vertex b = min(vertices, new Comparator<Vertex>() {
        public int compare(Vertex i, Vertex j) { return Double.compare(key(i), key(j)); }
        double key(Vertex v) { return v == a ? Double.MAX_VALUE : (v.loc().sub(a.loc())).ang(); }
      });
      return new Edge(a, b);
    }

    void tryNextEdge() {
      Edge edge; Vertex previousVertex; {
        Entry<Edge, Vertex> entry = openEdges.entrySet().iterator().next();
        edge = entry.getKey(); previousVertex = entry.getValue(); openEdges.remove(edge); }
      Line line = edge.line();
      if (previousVertex == null) {
        
      }

/*

    edges = self._edges
    open_edges = self._open_edges
    append_edge = edges.append

    (edge, previous_vertex) = open_edges.iteritems().next()
    del open_edges[edge]
    line = edge.line()
    if previous_vertex is None:
      candidate_vertices = (v for v in self._vertices
        if v not in edge)
    else:
      if self.is_boundary_edge(edge):
        return
      side = -1 * line.side(previous_vertex.loc())
      candidate_vertices = (v for v in self._vertices
        if v not in edge and line.side(v.loc()) == side)
    v = min(candidate_vertices, key = lambda v: line.bulge(v.loc()))
    t = Triangle(list(edge) + [v])
    self._triangles.append(t)
    for (u, w) in permutations(edge):
      uv = Edge(u, v)
      if uv in open_edges:
        del open_edges[uv]
      else:
        append_edge(uv)
        open_edges[uv] = w

  def is_boundary_edge(self, e):
    vertices = [ v.loc() for v in self._vertices if v not in e ]
    return e.line().same_side(*vertices)
*/

    }

  }

}
