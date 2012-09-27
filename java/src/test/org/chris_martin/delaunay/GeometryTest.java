package org.chris_martin.delaunay;

import org.testng.annotations.Test;

import java.util.Collection;

import static java.lang.Math.*;
import static java.util.Arrays.asList;
import static org.chris_martin.delaunay.Geometry.*;
import static org.chris_martin.delaunay.Geometry.Side.LEFT;
import static org.chris_martin.delaunay.Geometry.Side.RIGHT;
import static org.testng.Assert.assertEquals;

public class GeometryTest {

  double epsilon = pow(10, -6);

  boolean approx(double a, double b) { return a - b < epsilon; }

  boolean approx(Geometry.Vec a, Geometry.Vec b) {
    return approx(a.x(), b.x()) && approx(a.y(), b.y()); }

  void assertApprox(double actual, double expected) {
    if (!approx(actual, expected)) throw new AssertionError(
      String.format("Expected %f but got %f", expected, actual)); }

  void assertApprox(Geometry.Vec actual, Geometry.Vec expected) {
    if (!approx(actual, expected)) throw new AssertionError(
      String.format("Expected %s but got %s", expected, actual)); }

  void assertApproxUnordered(Vec[] actual, Vec[] expected) {
    assertApproxUnordered(asList(actual), asList(expected)); }

  void assertApproxUnordered(Collection<Vec> actual, Collection<Vec> expected) {
    String message = String.format("Expected %s but got %s", expected, actual);
    if (actual.size() != expected.size()) throw new AssertionError(message);
    for (Vec v : actual) if (!containsApprox(expected, v)) throw new AssertionError(message); }

  boolean containsApprox(Collection<Vec> haystack, Vec needle) {
    for (Vec v : haystack) if (approx(v, needle)) return true; return false; }

  void assertLess(double a, double b) {
    if (a >= b) throw new AssertionError(String.format("Expected a < b, got a=%f, b=%f", a ,b)); }

  @Test public void testVecAdd() { assertApprox(xy(1, 2).add(xy(5, 11)), xy(6, 13)); }
  @Test public void testVecSub() { assertApprox(xy(1, 2).sub(xy(5, 11)), xy(-4, -9)); }

  @Test public void testVecMult1() { assertApprox(xy(3, -4).mult(5), xy(15, -20)); }
  @Test public void testVecMult2() { assertApprox(xy(3, -4).mult(-2), xy(-6, 8)); }
  @Test public void testVecMult3() { assertApprox(xy(1, 1).mult(-1), xy(-1, -1)); }

  @Test public void testVecDot1() { assertApprox(xy(2, 6).dot(xy(4, 1.5)), 17); }
  @Test public void testVecDot2() { assertApprox(xy(2, 6).dot(origin()), 0); }
  @Test public void testVecDot3() { assertApprox(origin().dot(xy(4, 19)), 0); }

  @Test public void testVecMag1() { assertApprox(xy(3, 4).mag(), 5); }
  @Test public void testVecMag2() { assertApprox(xy(-1, 1).mag(), sqrt(2)); }

  @Test public void testVecAng1() { assertApprox(xy(1, 0).ang(), 0); }
  @Test public void testVecAng2() { assertApprox(xy(-1, 0).ang(), PI); }

  @Test public void testLineSide1() { assertEquals(oTo(xy(0, 1)).side(xy(1, 1)), RIGHT); }
  @Test public void testLineSide2() { assertEquals(oTo(xy(0, 1)).side(xy(-1, 1)), LEFT); }
  @Test public void testLineSide3() { assertEquals(oTo(xy(0, -1)).side(xy(1, 1)), LEFT); }
  @Test public void testLineSide4() { assertEquals(oTo(xy(0, -1)).side(xy(-1, 1)), RIGHT); }
  @Test public void testLineSide5() { assertEquals(oTo(xy(1, 1)).side(xy(1, 0)), RIGHT); }
  @Test public void testLineSide6() { assertEquals(oTo(xy(1, 1)).side(xy(0, 1)), LEFT); }
  @Test public void testLineSide7() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(-1000, 1000)), LEFT); }
  @Test public void testLineSide8() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(1000, -1000)), RIGHT); }
  @Test public void testLineSide9() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(1000, 0)), RIGHT); }
  @Test public void testLineSide10() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(10, 11)), LEFT); }
  @Test public void testLineSide11() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(10, 9)), RIGHT); }
  @Test public void testLineSide12() { assertEquals(aToB(xy(10, 10), xy(14, 11)).side(xy(14, 11.1)), LEFT); }

  @Test public void testLineAng() { assertApprox(aToB(xy(2, 3), xy(4, 3)).ang(), 0); }

  @Test public void testLineIntersect() { assertApprox(
    intersect(aToB(xy(0, 0), xy(2, 2)), aToB(xy(2, 0), xy(-1, 3))),
    xy(1, 1) ); }

  @Test public void testLineCircleIntersect() { assertApproxUnordered(
    intersect(aToB(xy(3, 1), xy(4, 2)), circle(xy(3, 1), sqrt(2))),
    new Vec[]{ xy(4, 2), xy(2, 0) } ); }

  @Test public void testTriangleCircle() {
    assertApprox(circle(xy(1, 0), xy(0, 2), xy(0, 0)).center(), xy(.5, 1)); }

  @Test public void testBulge1() { Line l = aToB(xy(0, 0), xy(1, 0));
    assertLess(l.bulge(xy(.5, .1)), l.bulge(xy(.5, .2))); }
  @Test public void testBulge2() { Line l = aToB(xy(0, 0), xy(1, 0));
    assertLess(l.bulge(xy(.5, -.1)), l.bulge(xy(.5, -.2))); }
  @Test public void testBulge3() { Line l = aToB(xy(0, 0), xy(1, 0));
    assertLess(l.bulge(xy(.5, .1)), l.bulge(xy(.5, 20))); }
  @Test public void testBulge4() { Line l = aToB(xy(0, 0), xy(1, 0));
    assertLess(l.bulge(xy(.5, 10)), l.bulge(xy(.5, 20))); }
  @Test public void testBulge5() { Line l = aToB(xy(660, 28), xy(707, 113));
    assertLess(0, l.bulge(xy(119, 563))); }

}
