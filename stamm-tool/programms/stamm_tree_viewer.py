import sys, zipfile, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
)
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import QRectF, Qt

BOX_W, BOX_H = 160, 60
X_PAD, Y_PAD = 50, 120

class StammViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(".stamm Family Tree Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Button to open .stamm
        self.button = QPushButton("Open .stamm File", self)
        self.button.clicked.connect(self.open_stamm)
        self.button.move(10, 10)

        # Graphics view for the tree
        self.view = QGraphicsView(self)
        self.view.setGeometry(10, 50, 1180, 740)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

    def open_stamm(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open .stamm File", "", "STAMM Files (*.stamm)")
        if not fname:
            return
        profiles, relationships = self.load_stamm(fname)
        self.draw_tree(profiles, relationships)

    def load_stamm(self, path):
        profiles, relationships = {}, {}
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                base = name.split("/")[-1]
                if base.endswith(".dfile"):
                    profiles[base] = z.read(name).decode("utf-8")
                elif base.endswith(".json"):
                    relationships = json.loads(z.read(name).decode("utf-8"))
        return profiles, relationships

    def extract_name(self, dfile):
        for line in dfile.splitlines():
            if line.startswith("NAME:"):
                return line.split(":",1)[1].strip()
        return "Unknown"

    def build_levels(self, profiles, relationships):
        levels = {p:0 for p in profiles}
        changed = True
        while changed:
            changed = False
            for person, rel in relationships.items():
                for parent in rel.get("parents", []):
                    if parent in levels and levels[person] <= levels[parent]:
                        levels[person] = levels[parent]+1
                        changed = True
        return levels

    def draw_tree(self, profiles, relationships):
        self.scene.clear()
        levels = self.build_levels(profiles, relationships)
        rows = {}
        for p, lvl in levels.items():
            rows.setdefault(lvl, []).append(p)
        positions = {}

        # Draw boxes
        max_width = max(len(r) for r in rows.values())*(BOX_W+X_PAD)+100
        max_height = (max(rows.keys())+1)*(BOX_H+Y_PAD)+100
        for lvl, persons in rows.items():
            y = 50 + lvl*(BOX_H+Y_PAD)
            total_w = len(persons)*(BOX_W+X_PAD)
            start_x = max((max_width-total_w)//2, 20)
            for i, p in enumerate(persons):
                x = start_x + i*(BOX_W+X_PAD)
                positions[p] = (x,y)
                rect = QGraphicsRectItem(QRectF(x, y, BOX_W, BOX_H))
                rect.setPen(QPen(Qt.GlobalColor.black, 2))
                self.scene.addItem(rect)
                name = self.extract_name(profiles[p])
                text = QGraphicsTextItem(name)
                text.setDefaultTextColor(QColor("black"))
                text.setPos(x+10, y+BOX_H/4)
                self.scene.addItem(text)

        # Parent -> child lines
        for p, rel in relationships.items():
            for parent in rel.get("parents", []):
                if parent in positions and p in positions:
                    px, py = positions[parent]
                    cx, cy = positions[p]
                    self.scene.addLine(px+BOX_W/2, py+BOX_H, cx+BOX_W/2, cy, QPen(Qt.GlobalColor.black, 2))

        # Spouse lines
        for p, rel in relationships.items():
            spouse = rel.get("spouse")
            if spouse and spouse in positions:
                px, py = positions[p]
                sx, sy = positions[spouse]
                self.scene.addLine(px+BOX_W, py+BOX_H/4, sx, sy+BOX_H/4, QPen(Qt.GlobalColor.red, 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StammViewer()
    window.show()
    sys.exit(app.exec())
