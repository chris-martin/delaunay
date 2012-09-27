package org.chris_martin.delaunay;

import javax.swing.*;

import java.awt.*;

import static javax.swing.WindowConstants.EXIT_ON_CLOSE;

public class Main {

  public static void main(String[] args) {
    new Main();
  }

  JFrame frame;

  public Main() {
    frame = new JFrame("Triangulation");
    frame.setSize(800, 600);
    frame.setDefaultCloseOperation(EXIT_ON_CLOSE);
    frame.setVisible(true);
    frame.add(new Background());
    System.out.println(-5 % 2);
  }

  static class Background extends JComponent {

    Color color = new Color(150, 170, 200);

    @Override
    protected void paintComponent(Graphics g) {
      super.paintComponent(g);
      g.setColor(color);
      Rectangle rect = g.getClipBounds();
      g.fillRect(0, 0, rect.width, rect.height);
    }

  }

}
