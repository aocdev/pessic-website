import javafx.application.Platform;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.stage.Stage;
import javafx.stage.Window;
import java.awt.image.BufferedImage;
public class WebShots extends cat.pessic.app.PessicApp {
  static String dir = System.getProperty("dir");
  static void shot(Scene sc, String f) {
    var img = sc.snapshot(null); int w=(int)img.getWidth(), h=(int)img.getHeight();
    var bi = new BufferedImage(w,h,BufferedImage.TYPE_INT_RGB); var pr = img.getPixelReader();
    for (int y=0;y<h;y++) for (int x=0;x<w;x++) bi.setRGB(x,y,pr.getArgb(x,y));
    try { javax.imageio.ImageIO.write(bi,"png",new java.io.File(dir, f)); } catch(Exception e){throw new RuntimeException(e);} }
  static <T extends Node> T find(Scene s, Class<T> t, java.util.function.Predicate<T> p) {
    return s.getRoot().lookupAll("*").stream().filter(t::isInstance).map(t::cast).filter(p).findFirst().orElseThrow(() -> new RuntimeException("not found")); }
  static void nav(Scene s, String text) { find(s, ToggleButton.class, b -> text.equals(b.getText())).fire(); }
  static void scroll(Scene s, double v) { find(s, ScrollPane.class, x -> true).setVvalue(v); }
  static void step(long ms, Runnable r) { try { Thread.sleep(ms); } catch (Exception e) {}
    Platform.runLater(() -> { try { r.run(); } catch (Exception e) { System.out.println("STEP FAILED " + e); } }); }
  @Override public void start(Stage stage) {
    super.start(stage);
    Scene sc = stage.getScene();
    boolean late = System.getenv("PESSIC_TODAY").endsWith("-28");
    new Thread(() -> {
      step(1500, () -> { stage.setWidth(1280); stage.setHeight(860); });
      if (late) {
        step(300, () -> find(sc, Button.class, b -> b.getText() != null && b.getText().startsWith("Tanca ") && b.getStyleClass().contains("primary")).fire());
        step(1000, () -> shot(Window.getWindows().stream().filter(w -> w != stage && w.isShowing()).findFirst().orElseThrow().getScene(), "close.png"));
        step(300, () -> { Window d = Window.getWindows().stream().filter(w -> w != stage && w.isShowing()).findFirst().orElseThrow();
          find(d.getScene(), Button.class, b -> "Cancel·la".equals(b.getText())).fire(); });
      } else {
        step(900, () -> shot(sc, "resum.png"));
        step(300, () -> scroll(sc, 0.55));
        step(600, () -> shot(sc, "sobres.png"));
        String[][] tabs = {{"Moviments", "moviments.png"}, {"Pagaments fixos", "pagaments.png"}, {"Estalvi", "estalvi.png"},
            {"Límits", "limits.png"}, {"Històric", "historic.png"}, {"Anuals", "anuals.png"}};
        for (String[] t : tabs) { step(400, () -> nav(sc, t[0])); step(800, () -> shot(sc, t[1])); }
        step(300, () -> nav(sc, "Estalvi"));
        step(500, () -> scroll(sc, 1.0));
        step(600, () -> shot(sc, "guardioles.png"));
      }
      step(400, () -> { System.out.println("SHOTS DONE"); Platform.exit(); });
    }).start();
  }
}
