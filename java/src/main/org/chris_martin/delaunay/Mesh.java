package org.chris_martin.delaunay;

import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import com.google.common.base.Function;
import com.google.common.base.Predicate;
import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Multimap;
import com.google.common.collect.Ordering;
import org.chris_martin.delaunay.Geometry.Line;
import org.chris_martin.delaunay.Geometry.Side;
import org.chris_martin.delaunay.Geometry.Vec;

import static com.google.common.collect.Sets.newHashSet;
import static java.util.Arrays.asList;
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

  public Mesh() {}
  public Mesh(Collection<Vec> points) { setPoints(points); }

  public void setPoints(Collection<Vec> points) {
    Delaunay d = new Delaunay(points);
    triangles = d.triangles;
    vertices = d.vertices;
  }

  public Collection<Edge> edges() {
    Set<Edge> edges = newHashSet();
    for (Triangle t : triangles) edges.addAll(t.edges());
    return edges;
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
    private Swings swings = new Swings();
    private Corner next, prev;
    private Corner(Vertex vertex, Triangle triangle) {
      this.vertex = vertex; this.triangle = triangle;
      if (vertex.corner == null) vertex.corner = this; }
    public Corner next() { return next; }
    public Corner prev() { return prev; }
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
    public List<Vertex> vertices() { return asList(a(), b()); }
    public Line line() { return aToB(a.loc, b.loc); }
    public boolean equals(Object o) {
      return this == o || (o instanceof Edge && a == ((Edge) o).a && b == ((Edge) o).b); }
    public int hashCode() { return 31 * a.hashCode() + b.hashCode(); }
    public boolean onConvexHull(List<Vertex> vertices) { Line line = line(); Side side = null;
      for (Vertex v : vertices) if (v != a && v != b) { Side s = line.side(v.loc());
        if (side == null) side = s; else if (s != side) return false; }
      return true; }
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
      initNextPrev();
    }
    private void initNextPrev() { a.next = b; b.next = c; c.next = a; a.prev = c; b.prev = a; c.prev = b; }
    public List<Corner> corners() { return asList(a, b, c); }
    public List<Edge> edges() { Vertex a = this.a.vertex, b = this.b.vertex, c = this.c.vertex;
      return asList(new Edge(a, b), new Edge(b, c), new Edge(c, a)); }
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
      final Edge edge; Vertex previousVertex; {
        Entry<Edge, Vertex> entry = openEdges.entrySet().iterator().next();
        edge = entry.getKey(); previousVertex = entry.getValue(); openEdges.remove(edge); }
      final Line line = edge.line();
      Iterable<Vertex> candidateVertices;
      if (previousVertex == null) {
        candidateVertices = Iterables.filter(vertices, new Predicate<Vertex>() { public boolean apply(Vertex vertex) {
          return !edge.vertices().contains(vertex); } });
      } else {
        if (edge.onConvexHull(vertices)) return;
        final Side side = line.side(previousVertex.loc()).opposite();
        candidateVertices = Iterables.filter(vertices, new Predicate<Vertex>() { public boolean apply(Vertex vertex) {
          return !edge.vertices().contains(vertex) && line.side(vertex.loc()) == side; } });
      }
      final Vertex v = Ordering.natural().onResultOf(new Function<Vertex, Double>() { public Double apply(Vertex v) {
        return line.bulge(v.loc()); }}).min(candidateVertices);
      Triangle t = new Triangle(edge.a(), edge.b(), v);
      triangles.add(t);
      for (List<Vertex> vertexPair : ImmutableList.of(edge.vertices(), Lists.reverse(edge.vertices()))) {
        Vertex u = vertexPair.get(0), w = vertexPair.get(1); Edge uv = new Edge(u, v);
        if (openEdges.remove(uv) == null) { edges.add(uv); openEdges.put(uv, w); }
      }
    }

    void calculateSwing() {
      Multimap<Vertex, Corner> v2c = ArrayListMultimap.create();
      for (Triangle t : triangles) for (Corner c : t.corners()) v2c.put(c.vertex, c);
      for (Collection<Corner> cs : v2c.asMap().values()) {
        for (Corner i : cs) for (Corner j : cs) if (i.next.vertex == j.prev.vertex)
          { j.swings.next.corner = i; i.swings.next.corner = j; }
        Corner si = null, sj = null;
        for (Corner i : cs) {
          if (i.swings.next.corner == null) si = i;
          if (i.swings.prev.corner == null) sj = i;
        }
        if (si != null) {
          si.swings.next.corner = sj; si.swings.next.isSuper = true;
          sj.swings.prev.corner = si; sj.swings.prev.isSuper = true;
        }
      }
    }

  }

}
