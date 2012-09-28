package org.chris_martin.delaunay;

import static java.lang.Math.*;
import static org.chris_martin.delaunay.Geometry.Side.LEFT;
import static org.chris_martin.delaunay.Geometry.Side.RIGHT;

public final class Geometry {
  private Geometry() {}

  private static final double PI2 = PI*2;
  private static final double HALFPI = PI/2;
  private static double angle(double a) { return a < 0 ? ((a % PI2) + PI2) : (a % PI2); }
  private static double angle(double a, boolean flip) { return angle(flip ? a + PI : a); }
  private static int sign(double x) { return x == 0 ? 0 : (x < 0 ? -1 : 1); }

  /** A point in a Euclidean plane. */
  public static interface Vec extends Comparable<Vec> {

    public double x();
    public double y();

    public double ang();

    public double mag();
    public Vec mag(double newMag);

    /** Equivalent to mag(1). */
    public Vec unit();

    public Vec add(Vec o);
    public Vec sub(Vec o);
    public Vec mult(double factor);
    public Vec mult(Number factor);
    public Vec div(double divisor);
    public Vec div(Number divisor);
    public Vec rot(double ang);
    public Vec rot(Number ang);

    public Vec addX(double o);
    public Vec addY(double o);
    public Vec subX(double o);
    public Vec subY(double o);

    /** This is exactly (0, 0). */
    public boolean isOrigin();

    public Vec rot90();
    public Vec rot180();

    /** Scalar (dot) product. */
    public double dot(Vec o);

    /** U x V = U dot rot90(V). */
    public double cross(Vec o);

  }

  private static abstract class BaseVec implements Vec {
    public int compareTo(Vec o) { return Double.compare(mag(), o.mag()); }
    public Vec add(Vec o) { return new XY(this.x()+o.x(), this.y()+o.y()); }
    public Vec sub(Vec o) { return new XY(this.x()-o.x(), this.y()-o.y()); }
    public Vec mag(double newMag) { return new Ang(ang(), newMag); }
    public Vec unit() { return new Ang(ang(), 1); }
    public Vec mult(Number factor) { return mult(factor.doubleValue()); }
    public Vec div(Number divisor) { return div(divisor.doubleValue()); }
    public Vec addX(double $) { return xy(x()+$, y()); }
    public Vec addY(double $) { return xy(x(), y()+$); }
    public Vec subX(double $) { return xy(x()-$, y()); }
    public Vec subY(double $) { return xy(x(), y()-$); }
    public double dot(Vec o) { return x()*o.x() + y()*o.y(); }
    public double cross(Vec o) { return dot(o.rot90()); }
    public Vec rot(double ang) { return new Ang(ang() + ang, mag()); }
    public Vec rot(Number ang) { return rot(ang.doubleValue()); }
    public boolean isOrigin() { return false; }
    public String toString() { return String.format("(%f, %f)", x(), y()); }
  }

  private static class XY extends BaseVec {
    final double x, y; double ang, mag; boolean hasAng, hasMag;
    XY(double x, double y) { this.x = x; this.y = y; }
    public double x() { return x; }
    public double y() { return y; }
    public double ang() { if (!hasAng) { ang = atan2(y, x); hasMag = true; } return ang; }
    public double mag() { if (!hasMag) { mag = sqrt(pow(x,2)+pow(y,2)); hasMag = true; } return mag; }
    public XY rot180() { return new XY(-1*x, -1*y); }
    public XY rot90() { return new XY(-1 * y, x); }
    public XY mult(double f) { return new XY(f*x, f*y); }
    public XY div(double d) { return new XY(x/d, y/d); }
  }
  public static Vec xy(double x, double y) { return x == 0 && y == 0 ? ORIGIN : new XY(x, y); }
  public static Vec xy(Number x, Number y) { return xy(x.doubleValue(), y.doubleValue()); }
  public static Vec xy(java.awt.Point p) { return new XY(p.x, p.y); }
  public static Vec xy(java.awt.event.MouseEvent e) { return new XY(e.getX(), e.getY()); }

  private static class Ang extends BaseVec {
    final double ang, mag; double x, y; boolean hasXy;
    Ang(double ang, double mag) { this.ang = angle(ang, mag<0); this.mag = abs(mag); }
    Ang(double ang) { this.ang = angle(ang); mag = 1; }
    private void ensureXy() { if (hasXy) return; x = mag * cos(ang); y = mag * sin(ang); hasXy = true; }
    public double x() { ensureXy(); return x; }
    public double y() { ensureXy(); return y; }
    public double ang() { return ang; }
    public double mag() { return mag; }
    public Ang rot180() { return new Ang(ang+PI, mag); }
    public Ang rot90() { return new Ang(ang+HALFPI, mag); }
    public Ang mult(double f) { return new Ang(ang, f*mag); }
    public Ang div(double d) { return new Ang(ang, mag/d); }
  }
  public static Vec angleVec(double ang, double mag) { return mag == 0 ? ORIGIN : new Ang(ang, mag); }
  public static Vec angleVec(Number ang, Number mag) { return angleVec(ang.doubleValue(), mag.doubleValue()); }
  public static Vec angleVec(double ang, Number mag) { return angleVec(ang, mag.doubleValue()); }
  public static Vec angleVec(Number ang, double mag) { return angleVec(ang.doubleValue(), mag); }
  public static Vec angleVec(double ang) { return new Ang(ang); }
  public static Vec angleVec(Number ang) { return new Ang(ang.doubleValue()); }

  private static class Origin implements Vec {
    public double x() { return 0; }
    public double y() { return 0; }
    public double ang() { throw new UnsupportedOperationException(); }
    public double mag() { return 0; }
    public Vec mult(double factor) { return this; }
    public Vec div(double divisor) { return this; }
    public Vec rot90() { return this; }
    public Vec rot180() { return this; }
    public Vec add(Vec o) { return o; }
    public Vec sub(Vec o) { return o.mult(-1); }
    public Vec addX(double $) { return xy($, 0); }
    public Vec addY(double $) { return xy(0, $); }
    public Vec subX(double $) { return xy(-$, 0); }
    public Vec subY(double $) { return xy(0, -$); }
    public Vec mag(double newMag) { throw new UnsupportedOperationException(); }
    public Vec unit() { throw new UnsupportedOperationException(); }
    public Vec mult(Number factor) { return this; }
    public Vec div(Number divisor) { return this; }
    public double dot(Vec o) { return 0; }
    public double cross(Vec o) { return 0; }
    public Vec rot(double ang) { return this; }
    public Vec rot(Number ang) { return this; }
    public int compareTo(Vec o) { return Double.compare(0, o.mag()); }
    public boolean isOrigin() { return true; }
  }
  private static final Origin ORIGIN = new Origin();
  public static Vec origin() { return ORIGIN; }

  /** A directed line segment in a Euclidean plane. */
  public static interface Line {

    Vec a();
    Vec b();
    Vec ab();

    double mag();
    double ang();
    Side side(Vec p);
    Line add(Vec offset);
    Line sub(Vec offset);
    Vec midpoint();
    Line bisect();

    /** Not equal, but correlated, to "bulge" as defined by Jarek Rossignac. */
    double bulge(Vec p);

  }

  public static enum Side { LEFT(-1), RIGHT(1);
    final int i; Side(int i) { this.i = i; }
    Side opposite() { return this == LEFT ? RIGHT : LEFT; }
  }

  private static abstract class BaseLine implements Line {
    public Side side(Vec p) { return p.sub(a()).cross(b().sub(a())) > 0 ? LEFT : RIGHT; }
    public Line bisect() { return pointAndStep(midpoint(), angleVec(ang()).rot90()); }
    public double bulge(Vec p) { Circle c = circle(a(), b(), p); return c.radius() * side(p).i * side(c.center()).i; }
  }

  private static class OriginLine extends BaseLine {
    final Vec b;
    OriginLine(Vec b) { this.b = b; }
    public Vec a() { return ORIGIN; }
    public Vec b() { return b; }
    public Vec ab() { return b; }
    public double ang() { return b.ang(); }
    public double mag() { return b.mag(); }
    public Line add(Vec offset) { return aToB(offset, b.add(offset)); }
    public Line sub(Vec offset) { return aToB(offset.mult(-1), b.sub(offset)); }
    public Vec midpoint() { return b.div(2); }
  }
  public static Line oTo(double ang) { return new OriginLine(angleVec(ang)); }
  public static Line oTo(Number ang) { return new OriginLine(angleVec(ang)); }
  public static Line oTo(Vec p) { return new OriginLine(p); }

  private static class AtoB extends BaseLine {
    final Vec a, b; Vec ab;
    AtoB(Vec a, Vec b) { this.a = a; this.b = b; }
    AtoB(Vec a, Vec b, Vec ab) { this.a = a; this.b = b; this.ab = ab; }
    public Vec a() { return a; }
    public Vec b() { return b; }
    public Vec ab() { if (ab == null) ab = b.sub(a); return ab; }
    public double ang() { return ab().ang(); }
    public double mag() { return ab().mag(); }
    public Line add(Vec offset) { return new AtoB(offset.add(a), b.add(offset), ab); }
    public Line sub(Vec offset) { return new AtoB(offset.sub(a), b.sub(offset), ab); }
    public Vec midpoint() { return a.add(b).div(2); }
  }
  public static Line aToB(Vec a, Vec b) { return new AtoB(a, b); }

  private static class PointAndDirection extends BaseLine {
    final Vec a, ab; Vec b;
    PointAndDirection(Vec a, Vec ab) { this.a = a; this.ab = ab; }
    public Vec a() { return a; }
    public Vec b() { if (b == null) b = a.add(ab); return b; }
    public Vec ab() { return ab; }
    public double ang() { return ab.ang(); }
    public double mag() { return ab.mag(); }
    public Line add(Vec offset) { return pointAndStep(a.add(offset), ab); }
    public Line sub(Vec offset) { return pointAndStep(a.sub(offset), ab); }
    public Vec midpoint() { return ab.div(2).add(a); }
  }
  public static Line pointAndStep(Vec a, Vec ab) { return new PointAndDirection(a, ab); }
  public static Line pointAndStep(Vec a, double ang) { return new PointAndDirection(a, angleVec(ang)); }
  public static Line pointAndStep(Vec a, Number ang) { return new PointAndDirection(a, angleVec(ang)); }

  public static Vec intersect(Line ab, Line cd) { Vec v1 = ab.a(), v2 = ab.b(), v3 = cd.a(), v4 = cd.b();
    // http://en.wikipedia.org/wiki/Line-line_intersection
    double x1 = v1.x(), y1 = v1.y(), x2 = v2.x(), y2 = v2.y(), x3 = v3.x(), y3 = v3.y(), x4 = v4.x(), y4 = v4.y();
    double d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4);
    double x = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / d;
    double y = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / d;
    return xy(x, y); }

  public static boolean overlap(Line ab, Line cd) { Vec a = ab.a(), b = ab.b(), c = cd.a(), d = cd.b();
    return ab.side(c) != ab.side(d) && cd.side(a) != cd.side(b); }

  public static interface Circle {
    Vec center();
    double radius();
  }

  private static class SimpleCircle implements Circle {
    final Vec center; final double radius;
    SimpleCircle(Vec center, double radius) { this.center = center; this.radius = radius; }
    public Vec center() { return center; }
    public double radius() { return radius; }
  }
  public static Circle circle(Vec center, double radius) { return new SimpleCircle(center, radius); }
  public static Circle circle(Vec center, Number radius) { return new SimpleCircle(center, radius.doubleValue()); }

  private static class TriangleCircle implements Circle {
    final Vec[] vs; Vec center; double radius; boolean hasRadius;
    TriangleCircle(Vec[] vs) { this.vs = vs; }
    public Vec center() { if (center == null) _center(); return center; }
    void _center() { center = intersect(aToB(vs[0], vs[1]).bisect(), aToB(vs[1], vs[2]).bisect()); }
    public double radius() { if (!hasRadius) _radius(); return radius; }
    void _radius() { radius = center().sub(vs[0]).mag(); hasRadius = true; }
  }
  public static Circle circle(Vec a, Vec b, Vec c) { return new TriangleCircle(new Vec[]{a,b,c}); }

  /** 0, 1, or 2 intersections. */
  public static Vec[] intersect(Line line, Circle circle) {
    // http://mathworld.wolfram.com/Circle-LineIntersection.html
    double r = circle.radius(); Vec cc = circle.center(); line = line.sub(cc);
    Vec a = line.a(), b = line.b(), ab = line.ab();
    double dx = ab.x(), dy = ab.y();
    double dr = sqrt(pow(dx,2) + pow(dy,2));
    double D = a.x()*b.y() - b.x()*a.y();
    double q = sqrt(pow(r,2) * pow(dr,2) - pow(D,2));
    if (q < 0) return new Vec[0];
    double qx = sign(dy) * dx * q, qy = abs(dy) * q;
    double Ddy = D*dy, nDdx = 0-D*dx;
    if (qx == 0 && qy == 0) return new Vec[]{ xy(Ddy, nDdx) };
    Vec[] is = new Vec[]{ xy(Ddy+qx, nDdx+qy), xy(Ddy-qx, nDdx-qy) };
    for (int i = 0; i < 2; i++) is[i] = is[i].div(pow(dr, 2)).add(cc);
    return is;
  }

}
