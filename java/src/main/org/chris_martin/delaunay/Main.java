package org.chris_martin.delaunay;

import javax.swing.*;

import java.awt.*;
import java.awt.geom.AffineTransform;
import java.awt.geom.Rectangle2D;
import java.awt.image.ColorModel;
import java.util.Random;
import java.util.List;

import org.chris_martin.delaunay.Geometry.Vec;
import org.chris_martin.delaunay.Mesh.Edge;
import org.chris_martin.delaunay.Mesh.Vertex;

import static com.google.common.collect.Lists.newArrayList;
import static javax.swing.WindowConstants.EXIT_ON_CLOSE;
import static org.chris_martin.delaunay.Geometry.xy;

public class Main {

  public static void main(String[] args) {
    new Main();
  }

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

    frame = new JFrame("Triangulation");
    frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
    PainterComponent comp = new PainterComponent(new PainterList(
      new Background(),
      edgePainter,
      vertexPainter
    ));
    comp.setPreferredSize(screenSize);
    frame.setContentPane(comp);
    frame.pack();
    frame.setVisible(true);
  }

  List<Vec> initialPoints() {
    List<Vec> ps = newArrayList(xy(25, 25), xy(775, 25), xy(25, 575),
      xy(775, 575), xy(400, 20), xy(400, 580), xy(20, 300), xy(780, 300));
    for (int i = 0; i < 50; i++) ps.add(randomPoint());
    return ps;
  }

  Vec randomPoint() {
    double p = 50;
    return xy( p + random.nextDouble() * (screenSize.width - 2*p),
               p + random.nextDouble() * (screenSize.height - 2*p) );
  }

  static class PainterComponent extends JPanel {
    private final Painter painter; PainterComponent(Painter painter) { this.painter = painter; }
    public void paint(Graphics g) { super.paintComponent(g);
      ((Graphics2D) g).setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
      painter.paint(g); }
  }

  interface Painter { void paint(Graphics g); }

  static class PainterList implements Painter {
    private final List<Painter> painters = newArrayList();
    public PainterList(Painter ... ps) { for (Painter p : ps) add(p); }
    public void paint(Graphics g) { for (Painter p : painters) p.paint(g); }
    public void add(Painter p) { painters.add(p); }
  }

  static class Vertex implements Painter {
    private static final int size = 8;
    private static final Color color = Color.white;
    private final Mesh.Vertex meshVertex; Vertex(Mesh.Vertex meshVertex) { this.meshVertex = meshVertex; }
    public void paint(Graphics g) {
      Vec loc = meshVertex.loc();
      g.setColor(color); g.fillOval((int) (loc.x() - size/2), (int) (loc.y() - size/2), size, size);
    }
  }

  static class Edge implements Painter {
    private static final Color color = Color.black;
    private final Mesh.Edge meshEdge; Edge(Mesh.Edge meshEdge) { this.meshEdge = meshEdge; }
    public void paint(Graphics g) {
      Vec a = meshEdge.a().loc(), b = meshEdge.b().loc();
      g.setColor(color); g.drawLine((int) a.x(), (int) a.y(), (int) b.x(), (int) b.y());
    }
  }

  static class Background implements Painter {

    private static final Color color = new Color(150, 170, 200);

    public void paint(Graphics g) {
      Rectangle rect = g.getClipBounds();
      g.setColor(color); g.fillRect(0, 0, rect.width, rect.height);
    }

  }

}
