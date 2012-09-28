package org.chris_martin.delaunay;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.Shape;
import java.awt.Stroke;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Random;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.Timer;

import com.google.common.base.Function;
import com.google.common.collect.Ordering;
import org.chris_martin.delaunay.Geometry.Line;
import org.chris_martin.delaunay.Geometry.Vec;
import org.chris_martin.delaunay.Mesh.Corner;
import org.chris_martin.delaunay.Mesh.VertexConfig;
import org.chris_martin.delaunay.Mesh.VertexPhysics;

import static com.google.common.collect.Lists.newArrayList;
import static javax.swing.WindowConstants.EXIT_ON_CLOSE;
import static org.chris_martin.delaunay.Geometry.aToB;
import static org.chris_martin.delaunay.Geometry.xy;

public class Graphics {

  public static void main(String[] args) {
    new Graphics();
  }

  static final Color backgroundColor = new Color(150, 170, 200);
  static final Color foregroundColor = new Color(40, 120, 240);
  static final Color markerColor = transition(foregroundColor, Color.white, 0.5);
  static final Color strokeColor = Color.black;

  static final int numberOfPoints = 100;

  Dimension screenSize = new Dimension(800, 600);
  Mesh mesh;
  Random random = new Random();
  JFrame frame;
  PainterList<Vertex> vertexPainter;
  PainterList<Edge> edgePainter;
  PainterList<Triangle> trianglePainter;
  Corner marker;

  public Graphics() {
    frame = new JFrame("Triangulation");
    frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
    restart();
  }

  void restart() {

    mesh = new Mesh(initialPoints());

    vertexPainter = painterList();
    for (Mesh.Vertex v : mesh.vertices()) vertexPainter.add(new Vertex(v));

    edgePainter = painterList();
    for (Mesh.Edge e : mesh.edges()) edgePainter.add(new Edge(e));

    trianglePainter = painterList();
    for (Mesh.Triangle t : mesh.triangles()) trianglePainter.add(new Triangle(t));

    final PainterComponent comp = new PainterComponent(
      new Background(), trianglePainter, edgePainter, vertexPainter);
    comp.setPreferredSize(screenSize);
    frame.setContentPane(comp);

    Mousing mousing = new Mousing();
    comp.addMouseListener(mousing);
    comp.addMouseMotionListener(mousing);

    frame.addKeyListener(new Keying());

    frame.pack();
    frame.setVisible(true);

    int fps = 30;
    new Timer(1000/fps, new ActionListener() { public void actionPerformed(ActionEvent e) {
      frame.repaint();
    }}).start();

    int physicsPerSecond = 30;
    final double physicsTimeStep = 1000./physicsPerSecond;
    new Timer((int) physicsTimeStep, new ActionListener() { public void actionPerformed(ActionEvent e) {
      //mesh.physics(physicsTimeStep);
    }}).start();

  }

  class Mousing extends MouseAdapter {
    Vec a;

    public void mouseMoved(MouseEvent e) {
      Vec b = xy(e);
      if (a != null) mouseMotion(aToB(a, b));
      a = b;
    }
    public void mouseExited(MouseEvent e) {
      a = null;
    }

    public void mousePressed(MouseEvent e) {
      final Vec p = xy(e);
      Mesh.Triangle t = findTriangle(p);
      marker = t == null ? null : Ordering.natural().onResultOf(new Function<Corner, Double>() {
        public Double apply(Corner c) { return p.sub(c.vertex().loc()).mag(); }}).min(t.corners());
    }
    Mesh.Triangle findTriangle(Vec p) {
      for (Mesh.Triangle t : mesh.triangles()) if (t.contains(p)) return t; return null; }
  }

  class Keying extends KeyAdapter {
    public void keyPressed(KeyEvent e) {
      System.out.println(e.getKeyChar());
      char C = e.getKeyChar();
      char c = Character.toLowerCase(C);
      boolean upper = C != c;
      if (marker != null) {
        if (c == 's') marker = marker.swing(upper);
        if (c == 'u') marker = marker.unswing(upper);
        if (c == 'n') marker = marker.next();
        if (c == 'p') marker = marker.prev();
      }
    }
  }

  void mouseMotion(Line motion) {
    for (Edge e : edgePainter.painters) if (Geometry.overlap(motion, e.line())) e.flash(); }

  List<VertexConfig> initialPoints() {
    List<VertexConfig> ps = newArrayList();
    for (Vec p : Arrays.<Vec>asList(xy(25, 25), xy(775, 25))) ps.add(new VertexConfig(p, VertexPhysics.PINNED));
    for (Vec p : Arrays.<Vec>asList(xy(25, 575), xy(775, 575), xy(400, 20),
      xy(400, 580), xy(20, 300), xy(780, 300))) ps.add(new VertexConfig(p, VertexPhysics.FREE));
    for (int i = 0; i < numberOfPoints; i++) ps.add(new VertexConfig(randomPoint(), VertexPhysics.FREE));
    return ps;
  }

  Vec randomPoint() { double p = 50;
    return xy( p + random.nextDouble() * (screenSize.width - 2*p),
               p + random.nextDouble() * (screenSize.height - 2*p) ); }

  static class PainterComponent extends JPanel {
    private final Painter painter; PainterComponent(Painter painter) { this.painter = painter; }
    PainterComponent(Painter... ps) { this(painterList(ps)); }
    public void paint(java.awt.Graphics g_) { super.paintComponent(g_);
      Graphics2D g = ((Graphics2D) g_);
      g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
      painter.paint(g); } }

  interface Painter { void paint(Graphics2D g); }

  static <P extends Painter> PainterList<P> painterList() { return new PainterList<P>(); }
  static <P extends Painter> PainterList<P> painterList(P... ps) { return new PainterList<P>(ps); }
  static class PainterList<P extends Painter> implements Painter {
    private final List<P> painters = newArrayList();
    public PainterList() {}
    public PainterList(P... ps) { for (P p : ps) add(p); }
    public void paint(Graphics2D g) { for (P p : painters) p.paint(g); }
    public void add(P p) { painters.add(p); }
  }


  private static final int vertex_size = 5;
  private static final Stroke vertex_stroke = new BasicStroke(2);
  class Vertex implements Painter {
    private final Mesh.Vertex meshVertex; Vertex(Mesh.Vertex meshVertex) { this.meshVertex = meshVertex; }
    public void paint(Graphics2D g) {
      Vec loc = meshVertex.loc();
      Shape s = new Ellipse2D.Double(loc.x() - vertex_size, loc.y() - vertex_size, 2 * vertex_size, 2 * vertex_size);
      g.setPaint(marker!=null&&marker.vertex()==meshVertex ? markerColor : foregroundColor); g.fill(s);
      g.setPaint(strokeColor); g.setStroke(vertex_stroke); g.draw(s);
    }
  }

  static class Edge implements Painter {
    private static final Stroke stroke = new BasicStroke(2);
    private static final Color flashColor = new Color(255, 0, 255);
    private final Mesh.Edge meshEdge; Edge(Mesh.Edge meshEdge) { this.meshEdge = meshEdge; }
    public void paint(Graphics2D g) {
      Vec a = meshEdge.a().loc(), b = meshEdge.b().loc();
      g.setStroke(stroke); g.setColor(transition(strokeColor, flashColor, getFlash()));
      g.drawLine((int) a.x(), (int) a.y(), (int) b.x(), (int) b.y());
    }
    Line line() { return meshEdge.line(); }
    Long flashStart;
    void flash() { flashStart = new Date().getTime(); }
    double getFlash() {
      if (flashStart != null) {
        long d = new Date().getTime() - flashStart;
        if (d > 1000) flashStart = null; else return (1000-d)/1000.;
      }
      return 0; }
  }

  class Triangle implements Painter {
    private final Mesh.Triangle t; Triangle(Mesh.Triangle t) { this.t = t; }
    public void paint(Graphics2D g) {
      Vec a = t.a().vertex().loc(), b = t.b().vertex().loc(), c = t.c().vertex().loc();
      g.setColor(marker!=null&&marker.triangle()==t ? markerColor : foregroundColor);
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

  static Color transition(Color a, Color b, double t) {
    return new Color(
      a.getRed() + (int) (t * (b.getRed() - a.getRed())),
      a.getGreen() + (int) (t * (b.getGreen() - a.getGreen())),
      a.getBlue() + (int) (t * (b.getBlue() - a.getBlue()))
    ); }

}
