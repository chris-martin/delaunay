package org.chris_martin.delaunay;

import java.awt.*;
import java.awt.event.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.awt.geom.Line2D;
import java.awt.geom.Rectangle2D;
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
import org.chris_martin.delaunay.Mesh.*;

import static com.google.common.collect.Lists.newArrayList;
import static javax.swing.WindowConstants.EXIT_ON_CLOSE;
import static org.chris_martin.delaunay.Geometry.*;

public class Graphics {

  public static void main(String[] args) {
    //RepeatingReleasedEventsFixer.install();
    new Graphics();
  }

  static final Color backgroundColor = new Color(150, 170, 200);
  static final Color foregroundColor = new Color(40, 120, 240);
  static final Color markerColor = transition(foregroundColor, Color.white, 0.5);
  static final Color strokeColor = Color.black;

  static final int numberOfPoints = 20;

  int fps = 30, physicsPerSecond = 30;

  Dimension screenSize = new Dimension(800, 600);
  Mesh mesh;
  Random random = new Random();
  JFrame frame;
  JPanel panel;
  PainterList<Vertex> vertexPainter;
  PainterList<Edge> edgePainter;
  PainterList<Triangle> trianglePainter;
  Corner marker;
  Mousing mousing = new Mousing();

  enum DisplayMode {
    PRETTY, DEBUG;
    DisplayMode next() {
      DisplayMode[] v = DisplayMode.values();
      return v[(ordinal()+1) % v.length];
    }
  }
  DisplayMode displayMode = DisplayMode.PRETTY;

  public Graphics() {
    frame = new JFrame("Triangulation");
    frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
    frame.addKeyListener(new Keying());
    FlowLayout layout = new FlowLayout(); layout.setVgap(0); layout.setHgap(0);
    panel = new JPanel(layout);
    panel.addMouseListener(mousing); panel.addMouseMotionListener(mousing);
    frame.add(panel);
    restart();

    new Timer(1000/fps, new ActionListener() { public void actionPerformed(ActionEvent e) {
      frame.repaint();
    }}).start();

    final double physicsTimeStep = 1000./physicsPerSecond;
    new Timer((int) physicsTimeStep, new ActionListener() { public void actionPerformed(ActionEvent e) {
      if (mesh != null) mesh.physics(physicsTimeStep);
    }}).start();
  }

  void quit() {
    WindowEvent wev = new WindowEvent(frame, WindowEvent.WINDOW_CLOSING);
    Toolkit.getDefaultToolkit().getSystemEventQueue().postEvent(wev);
  }

  void restart() {
    mesh = new Mesh(initialPoints());
    rebuildPainters();
  }

  void rebuildPainters() {

    vertexPainter = painterList();
    if (displayMode == DisplayMode.DEBUG) {
      for (Mesh.Vertex v : mesh.vertices()) vertexPainter.add(new Vertex(v));
    }

    edgePainter = painterList();
    for (Mesh.Edge e : mesh.edges()) edgePainter.add(new Edge(e));

    trianglePainter = painterList();
    for (Mesh.Triangle t : mesh.triangles()) trianglePainter.add(new Triangle(t));

    final PainterComponent comp = new PainterComponent(
      new Background(), trianglePainter, edgePainter, vertexPainter);
    comp.setPreferredSize(screenSize);

    panel.removeAll();
    panel.add(comp);
    frame.pack();
    frame.setVisible(true);
    frame.setResizable(false);
  }

  class Mousing extends MouseAdapter {
    Vec a; Line motion(MouseEvent e) { Vec b = xy(e); Line motion = a == null ? null : aToB(a, b); a = b; return motion; }

    public void mouseMoved(MouseEvent e) {
      Line motion = motion(e);
      if (motion != null) for (Edge edge : edgePainter.painters) if (Geometry.overlap(motion, edge.line())) edge.flash();
    }

    public void mouseDragged(MouseEvent event) {
      Line m;
      switch (mouseMode) {
        case SELECT: select(xy(event)); break;
        case DELETE: m = motion(event); if (m != null) {
          for (Mesh.Edge e : mesh.edges()) if (overlap(e.line(), m)) mesh.remove(e);
          rebuildPainters();
        } break;
        case CUT: m = motion(event); if (m != null) {
          List<Line> ms = newArrayList(m);
          while (ms.get(0).mag() > 1) {
            List<Line> ms2 = newArrayList();
            for (Line $ : ms) {
              ms2.add(aToB($.a(), $.midpoint()));
              ms2.add(aToB($.midpoint(), $.b()));
            }
            ms = ms2;
          }
          for (Line $ : ms) for (Mesh.Edge e : mesh.edges()) if (overlap(e.line(), $)) mesh.cut(e, $);
          rebuildPainters();
        } break;
      }
    }

    public void mouseExited(MouseEvent event) { a = null; }

    public void mousePressed(MouseEvent event) {
      final Vec p = xy(event);
      switch (mouseMode) {
        case SELECT: select(p); break;
        case DELETE: Mesh.Triangle t = findTriangle(p); if (t != null) { mesh.remove(t); rebuildPainters(); } break;
      }
    }
    public void mouseReleased(MouseEvent e) {
      mesh.stopCutting();
    }
    void select(final Vec p) {
      Mesh.Triangle t = findTriangle(p);
      marker = t == null ? null : Ordering.natural().onResultOf(new Function<Corner, Double>() {
        public Double apply(Corner c) { return p.sub(c.vertex().loc()).mag(); }}).min(t.corners());
    }
    Mesh.Triangle findTriangle(Vec p) {
      for (Mesh.Triangle t : mesh.triangles()) if (t.contains(p)) return t; return null; }
  }

  public enum MouseMode { SELECT, DELETE, CUT }
  private MouseMode mouseMode = MouseMode.CUT;

  class Keying extends KeyAdapter {
    public void keyPressed(KeyEvent e) {
      char C = e.getKeyChar();
      char c = Character.toLowerCase(C);
      boolean upper = C != c;
      if (marker != null) {
        switch (c) {
          case 's': marker = markerSwing(marker.swing().next(), upper); break;
          case 'u': marker = markerSwing(marker.swing().prev(), upper); break;
          case 'n': marker = marker.next(); break;
          case 'p': marker = marker.prev(); break;
        }
      }
      switch (c) {
        case 'r': restart(); break;
        case '1': mouseMode = MouseMode.SELECT; break;
        case '2': mouseMode = MouseMode.DELETE; break;
        case '3': mouseMode = MouseMode.CUT; break;
        case 'q': quit(); break;
        case 'd': displayMode = displayMode.next(); rebuildPainters(); break;
      }
    }
    Corner markerSwing(Swing swing, boolean allowSuper) {
      return (!swing.isSuper() || allowSuper) ? swing.corner() : marker;
    }
  }

  List<VertexConfig> initialPoints() {
    List<VertexConfig> ps = newArrayList();
    double top = 50, padX = 50, screenWidth = 800, midX = screenWidth/2,
      screenHeight = 600, bottom = screenHeight-100, midY = (top+bottom)/2;
    for (Vec p : Arrays.<Vec>asList(xy(padX, top), xy(screenWidth-padX, top), xy(midX, top+20),
        xy((padX+midX)/2, top-10), xy((screenWidth-padX+midX)/2, top-10)))
      ps.add(new VertexConfig(p, VertexPhysics.PINNED));
    for (Vec p : Arrays.<Vec>asList(xy(padX, bottom), xy(screenWidth-padX, bottom),
      xy(midX, bottom+5), xy(padX-5, midY), xy(screenWidth-padX+5, midY)))
      ps.add(new VertexConfig(p, VertexPhysics.FREE));
    for (VertexConfig vc : ps) vc.loc = vc.loc.add(angleVec(2 * Math.PI * random.nextDouble(), 3 * random.nextDouble()));
    double p = 20, rPadX = padX+p, rTop = top+p, rBottom = bottom-p;
    for (int i = 0; i < numberOfPoints; i++) ps.add(new VertexConfig(
      xy( rPadX + random.nextDouble() * (screenWidth - 2*rPadX),
          rTop + random.nextDouble() * (rBottom-rTop) ), VertexPhysics.FREE));
    return ps;
  }

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

  private static final int vertex_size = 15;
  private static final Stroke vertex_stroke = new BasicStroke(2);
  class Vertex implements Painter {
    private final Mesh.Vertex meshVertex; Vertex(Mesh.Vertex meshVertex) { this.meshVertex = meshVertex; }
    public void paint(Graphics2D g) {
      Vec loc = meshVertex.loc();
      Shape s = new Ellipse2D.Double(loc.x() - vertex_size, loc.y() - vertex_size, 2 * vertex_size, 2 * vertex_size);
      g.setPaint(marker!=null&&marker.vertex()==meshVertex ? markerColor : foregroundColor); g.fill(s);
      g.setPaint(strokeColor); g.setStroke(vertex_stroke); g.draw(s);
      String label = Integer.toString(meshVertex.id());
      Rectangle2D labelRect = g.getFontMetrics().getStringBounds(label, g);
      g.drawString(label, (int) (loc.x() - labelRect.getWidth()/2), (int) (loc.y() + labelRect.getHeight()/2));
    }
  }

  static class Edge implements Painter {
    private static final Stroke stroke = new BasicStroke(2);
    private static final Color flashColor = new Color(255, 0, 255);
    private final Mesh.Edge meshEdge; Edge(Mesh.Edge meshEdge) { this.meshEdge = meshEdge; }
    public void paint(Graphics2D g) {
      Vec a = meshEdge.a().loc(), b = meshEdge.b().loc();
      g.setStroke(stroke); g.setColor(transition(strokeColor, flashColor, getFlash()));
      g.draw(new Line2D.Double(a.x(), a.y(), b.x(), b.y()));
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
