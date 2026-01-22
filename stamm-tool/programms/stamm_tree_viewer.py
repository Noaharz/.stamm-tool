import sys, zipfile, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QVBoxLayout, QWidget, QTextEdit, QSplitter
)
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import QRectF, Qt

BOX_W, BOX_H = 160, 60
X_PAD, Y_PAD = 50, 120

class CleanStammViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clean STAMM Family Tree Viewer")
        self.setGeometry(50, 50, 1400, 800)

        # Toolbar
        self.open_btn = QPushButton("Open .stamm")
        self.open_btn.clicked.connect(self.open_stamm)
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        toolbar = QWidget()
        t_layout = QVBoxLayout()
        t_layout.addWidget(self.open_btn)
        t_layout.addWidget(self.exit_btn)
        toolbar.setLayout(t_layout)

        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        from PyQt6.QtGui import QPainter
        self.view.setRenderHints(self.view.renderHints() | QPainter.RenderHint.Antialiasing)


        # Info panel
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)

        # Splitter layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(self.info_panel)
        splitter.setStretchFactor(0,3)
        splitter.setStretchFactor(1,1)
        splitter.setSizes([900,400])

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(toolbar)
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Data
        self.profiles = {}
        self.relationships = {}
        self.box_items = {}

    # ---------- Load .stamm ----------
    def open_stamm(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open .stamm File", "", "STAMM Files (*.stamm)")
        if not fname:
            return
        self.profiles, self.relationships = self.load_stamm(fname)
        self.draw_tree()

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

    # ---------- Helpers ----------
    def extract_name(self, dfile):
        for line in dfile.splitlines():
            if line.startswith("NAME:"):
                return line.split(":",1)[1].strip()
        return "Unknown"

    def extract_gender(self, dfile):
        for line in dfile.splitlines():
            if line.startswith("GENDER:"):
                return line.split(":",1)[1].strip().upper()
        return "M"

    # ---------- Draw Tree ----------
    def draw_tree(self):
        self.scene.clear()
        self.box_items.clear()

        # Step 1: Build levels for all profiles
        levels = {}
        for p in self.profiles:
            levels[p] = 0
        changed = True
        while changed:
            changed = False
            for person, rel in self.relationships.items():
                for parent in rel.get("parents", []):
                    if levels[person] <= levels.get(parent,0):
                        levels[person] = levels.get(parent,0)+1
                        changed = True

        # Step 2: Group by level
        rows = {}
        for p, lvl in levels.items():
            rows.setdefault(lvl, []).append(p)

        positions = {}
        max_width = max(len(r) for r in rows.values())*(BOX_W+X_PAD)+100
        max_height = (max(rows.keys())+1)*(BOX_H+Y_PAD)+100

        # Step 3: Draw family boxes
        drawn = set()
        for lvl in sorted(rows.keys()):
            y = 50 + lvl*(BOX_H+Y_PAD)
            x_cursor = 50
            # Arrange spouses together
            processed = set()
            for p in rows[lvl]:
                if p in processed:
                    continue
                spouse = self.relationships.get(p, {}).get("spouse")
                # Draw spouse side by side
                if spouse and spouse in rows[lvl] and spouse not in processed:
                    self.draw_box(p, x_cursor, y)
                    self.draw_box(spouse, x_cursor+BOX_W+10, y)
                    positions[p] = (x_cursor, y)
                    positions[spouse] = (x_cursor+BOX_W+10, y)
                    processed.add(p)
                    processed.add(spouse)
                    x_cursor += (BOX_W+10)*2 + X_PAD
                    drawn.add(p)
                    drawn.add(spouse)
                else:
                    self.draw_box(p, x_cursor, y)
                    positions[p] = (x_cursor, y)
                    processed.add(p)
                    x_cursor += BOX_W + X_PAD
                    drawn.add(p)

        # Step 4: Draw parent->child lines
        for child, rel in self.relationships.items():
            for parent in rel.get("parents", []):
                if parent in positions and child in positions:
                    px, py = positions[parent]
                    cx, cy = positions[child]
                    self.scene.addLine(px+BOX_W/2, py+BOX_H, cx+BOX_W/2, cy, QPen(Qt.GlobalColor.black,2))

        # Step 5: Draw spouse lines
        for p, rel in self.relationships.items():
            spouse = rel.get("spouse")
            if spouse and p in positions and spouse in positions:
                px, py = positions[p]
                sx, sy = positions[spouse]
                self.scene.addLine(px+BOX_W, py+BOX_H/4, sx, sy+BOX_H/4, QPen(Qt.GlobalColor.red,2))

        # Connect click event
        self.scene.selectionChanged.connect(self.show_selected_profile)

    # ---------- Draw single box ----------
    def draw_box(self, person, x, y):
        gender = self.extract_gender(self.profiles[person])
        color = QColor(173,216,230) if gender=="M" else QColor(255,182,193)
        rect = QGraphicsRectItem(QRectF(x, y, BOX_W, BOX_H))
        rect.setBrush(color)
        rect.setPen(QPen(Qt.GlobalColor.black,2))
        rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(rect)

        text = QGraphicsTextItem(self.extract_name(self.profiles[person]))
        text.setDefaultTextColor(QColor("black"))
        text.setPos(x+10, y+BOX_H/4)
        self.scene.addItem(text)

        self.box_items[rect] = person

    # ---------- Show info ----------
    def show_selected_profile(self):
        selected = [item for item in self.scene.selectedItems() if item in self.box_items]
        if not selected:
            return
        person = self.box_items[selected[0]]
        self.info_panel.setPlainText(self.profiles[person])

# ---------- Run ----------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = CleanStammViewer()
    window.show()
    sys.exit(app.exec())

