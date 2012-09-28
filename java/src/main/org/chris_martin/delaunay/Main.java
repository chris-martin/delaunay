package org.chris_martin.delaunay;

import org.chris_martin.delaunay.Geometry.Vec;

import javax.swing.*;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.List;
import java.util.Random;

import static com.google.common.collect.Lists.newArrayList;
import static javax.swing.WindowConstants.EXIT_ON_CLOSE;
import static org.chris_martin.delaunay.Geometry.xy;

public class Main {

  public static void main(String[] args) {
    new Main();
  }

  static final Color backgroundColor = new Color(150, 170, 200);
  static final Color foregroundColor = new Color(40, 120, 240);
  static final Color strokeColor = Color.black;

  static final int numberOfPoints = 100;

  Dimension screenSize = new Dimension(800, 600);
  Mesh mesh;
  Random random = new Random();
  JFrame frame;

  public Main() {
    restart();
  }

  void restart() {

    mesh = new Mesh(initialPoints());

    PainterList vertexPainter = new PainterList();
    for (Mesh.Vertex v : mesh.vertices()) vertexPainter.add(new Vertex(v));

    PainterList edgePainter = new PainterList();
    for (Mesh.Edge e : mesh.edges()) edgePainter.add(new Edge(e));

    PainterList trianglePainter = new PainterList();
    for (Mesh.Triangle t : mesh.triangles()) trianglePainter.add(new Triangle(t));

    frame = new JFrame("Triangulation");
    frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
    PainterComponent comp = new PainterComponent(new PainterList(
      new Background(), trianglePainter, edgePainter, vertexPainter));
    comp.setPreferredSize(screenSize);
    frame.setContentPane(comp);
    frame.pack();
    frame.setVisible(true);
  }

  List<Vec> initialPoints() {
    List<Vec> ps = newArrayList(xy(25, 25), xy(775, 25), xy(25, 575),
      xy(775, 575), xy(400, 20), xy(400, 580), xy(20, 300), xy(780, 300));
    for (int i = 0; i < numberOfPoints; i++) ps.add(randomPoint());
    return ps;
  }

  Vec randomPoint() { double p = 50;
    return xy( p + random.nextDouble() * (screenSize.width - 2*p),
               p + random.nextDouble() * (screenSize.height - 2*p) ); }

  static class PainterComponent extends JPanel {
    private final Painter painter; PainterComponent(Painter painter) { this.painter = painter; }
    public void paint(Graphics g_) { super.paintComponent(g_);
      Graphics2D g = ((Graphics2D) g_);
      g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
      painter.paint(g); } }

  interface Painter { void paint(Graphics2D g); }

  static class PainterList implements Painter {
    private final List<Painter> painters = newArrayList();
    public PainterList(Painter ... ps) { for (Painter p : ps) add(p); }
    public void paint(Graphics2D g) { for (Painter p : painters) p.paint(g); }
    public void add(Painter p) { painters.add(p); }
  }

  static class Vertex implements Painter {
    private static final int size = 5;
    private static final Stroke stroke = new BasicStroke(2);
    private final Mesh.Vertex meshVertex; Vertex(Mesh.Vertex meshVertex) { this.meshVertex = meshVertex; }
    public void paint(Graphics2D g) {
      Vec loc = meshVertex.loc();
      Shape s = new Ellipse2D.Double(loc.x() - size, loc.y() - size, 2 * size, 2 * size);
      g.setPaint(foregroundColor);
      g.fill(s);
      g.setPaint(strokeColor);
      g.setStroke(stroke);
      g.draw(s);
    }
  }

  static class Edge implements Painter {
    private static final Stroke stroke = new BasicStroke(2);
    private final Mesh.Edge meshEdge; Edge(Mesh.Edge meshEdge) { this.meshEdge = meshEdge; }
    public void paint(Graphics2D g) {
      Vec a = meshEdge.a().loc(), b = meshEdge.b().loc();
      g.setStroke(stroke); g.setColor(strokeColor);
      g.drawLine((int) a.x(), (int) a.y(), (int) b.x(), (int) b.y());
    }
  }

  static class Triangle implements Painter {
    private final Mesh.Triangle t; Triangle(Mesh.Triangle t) { this.t = t; }
    public void paint(Graphics2D g) {
      Vec a = t.a().vertex().loc(), b = t.b().vertex().loc(), c = t.c().vertex().loc();
      g.setColor(foregroundColor);
      Path2D.Double path = new Path2D.Double();
      path.moveTo(a.x(), a.y()); path.lineTo(b.x(), b.y()); path.lineTo(c.x(), c.y());
      g.fill(path);
    }
  }

  static class Background implements Painter {
    public void paint(Graphics2D g) {
      Rectangle rect = g.getClipBounds();
      g.setColor(backgroundColor); g.fillRect(0, 0, rect.width, rect.height);
    }
  }

}
