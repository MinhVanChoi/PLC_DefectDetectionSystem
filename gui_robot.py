import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QDoubleValidator

# Import kinematics module
try:
    from kinematic import RobotKinematics
    KINEMATICS_AVAILABLE = True
except ImportError:
    KINEMATICS_AVAILABLE = False
    print("[WARNING] kinematic.py not found. Using identity placeholder formulas.")


# ─────────────────────────────────────────────
#  Reusable styled widgets
# ─────────────────────────────────────────────

DARK_BG      = "#0d0f14"
PANEL_BG     = "#13161e"
BORDER_COLOR = "#2a2f3d"
ACCENT_CYAN  = "#00d4ff"
ACCENT_GREEN = "#00ff9d"
ACCENT_AMBER = "#ffb700"
ACCENT_RED   = "#ff4757"
TEXT_PRIMARY = "#e8eaf0"
TEXT_MUTED   = "#6b7280"
INPUT_BG     = "#1c2030"
RESULT_BG    = "#0a1a2e"


STYLE_SHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Consolas', 'Courier New', monospace;
}}

/* ── Section panels ── */
QFrame#panel {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
}}

/* ── Section title labels ── */
QLabel#section_title {{
    color: {ACCENT_CYAN};
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 4px;
    padding: 6px 0px;
}}

/* ── Field labels ── */
QLabel#field_label {{
    color: {TEXT_MUTED};
    font-size: 16px;
    letter-spacing: 2px;
    font-weight: bold;
    min-width: 100px;
}}

/* ── Input fields ── */
QLineEdit#input_field {{
    background-color: {INPUT_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    color: {ACCENT_CYAN};
    font-size: 18px;
    font-family: 'Consolas', monospace;
    padding: 10px 16px;
    min-height: 44px;
    selection-background-color: {ACCENT_CYAN};
    selection-color: {DARK_BG};
}}
QLineEdit#input_field:focus {{
    border: 1px solid {ACCENT_CYAN};
    background-color: #1e2840;
}}

/* ── Read-only result fields ── */
QLineEdit#result_field {{
    background-color: {RESULT_BG};
    border: 1px solid #0e2d4a;
    border-radius: 6px;
    color: {ACCENT_GREEN};
    font-size: 18px;
    font-family: 'Consolas', monospace;
    padding: 10px 16px;
    min-height: 44px;
}}

/* ── Main title ── */
QLabel#main_title {{
    color: {TEXT_PRIMARY};
    font-size: 30px;
    font-weight: bold;
    letter-spacing: 8px;
    font-family: 'Consolas', monospace;
}}

QLabel#title_accent {{
    color: {ACCENT_CYAN};
    font-size: 30px;
    font-weight: bold;
    letter-spacing: 8px;
    font-family: 'Consolas', monospace;
}}

/* ── Divider ── */
QFrame#divider {{
    background-color: {BORDER_COLOR};
}}

/* ── Bottom action buttons ── */
QPushButton#btn_grip {{
    background-color: transparent;
    border: 2px solid {ACCENT_AMBER};
    border-radius: 7px;
    color: {ACCENT_AMBER};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 120px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_grip:hover {{
    background-color: {ACCENT_AMBER};
    color: {DARK_BG};
}}
QPushButton#btn_grip:pressed {{
    background-color: #cc9200;
}}

QPushButton#btn_release {{
    background-color: transparent;
    border: 2px solid {ACCENT_GREEN};
    border-radius: 7px;
    color: {ACCENT_GREEN};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 120px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_release:hover {{
    background-color: {ACCENT_GREEN};
    color: {DARK_BG};
}}

QPushButton#btn_home {{
    background-color: transparent;
    border: 2px solid {ACCENT_CYAN};
    border-radius: 7px;
    color: {ACCENT_CYAN};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 120px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_home:hover {{
    background-color: {ACCENT_CYAN};
    color: {DARK_BG};
}}

QPushButton#btn_back {{
    background-color: transparent;
    border: 2px solid {ACCENT_RED};
    border-radius: 7px;
    color: {ACCENT_RED};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 120px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_back:hover {{
    background-color: {ACCENT_RED};
    color: {TEXT_PRIMARY};
}}

/* ── Status bar ── */
QLabel#status_bar {{
    color: {TEXT_MUTED};
    font-size: 13px;
    letter-spacing: 1px;
    padding: 2px 0px;
}}
"""


def make_input(placeholder="0.0") -> QLineEdit:
    le = QLineEdit()
    le.setObjectName("input_field")
    le.setPlaceholderText(placeholder)
    le.setValidator(QDoubleValidator(-9999.99, 9999.99, 4))
    le.setMinimumWidth(280)
    le.setMinimumHeight(48)
    return le


def make_result() -> QLineEdit:
    le = QLineEdit()
    le.setObjectName("result_field")
    le.setReadOnly(True)
    le.setPlaceholderText("—")
    le.setMinimumWidth(280)
    le.setMinimumHeight(48)
    return le


def make_label(text: str, obj_name="field_label") -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(obj_name)
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return lbl


def make_section_panel() -> QFrame:
    frame = QFrame()
    frame.setObjectName("panel")
    return frame


def make_divider_h() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    return line


def make_divider_v() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFixedWidth(1)
    return line


# ─────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────

class RobotControlGUI(QMainWindow):
    def __init__(self, robot_ctrl=None):
        super().__init__()
        self.robot_ctrl = robot_ctrl
        # Kinematics engine
        if KINEMATICS_AVAILABLE:
            from kinematic import RobotKinematics
            self.kin = RobotKinematics()
        else:
            self.kin = None

        # Debounce timer so calculation fires after user stops typing
        self._ik_timer = QTimer()
        self._ik_timer.setSingleShot(True)
        self._ik_timer.setInterval(300)
        self._ik_timer.timeout.connect(self._compute_ik)

        self._fk_timer = QTimer()
        self._fk_timer.setSingleShot(True)
        self._fk_timer.setInterval(300)
        self._fk_timer.timeout.connect(self._compute_fk)

        self._build_ui()
        self.setStyleSheet(STYLE_SHEET)

    # ── UI Construction ──────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("Robot Kinematics Controller")
        self.setMinimumSize(1373, 824)
        self.resize(1373, 824)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(40, 24, 40, 24)
        root.setSpacing(18)

        # ── Header ──────────────────────────────────
        root.addLayout(self._build_header())
        root.addWidget(make_divider_h())

        # ── Main content (IK left | divider | FK right) ──
        content = QHBoxLayout()
        content.setSpacing(0)
        content.addWidget(self._build_ik_panel(), stretch=1)
        content.addWidget(make_divider_v())
        content.addWidget(self._build_fk_panel(), stretch=1)
        root.addLayout(content, stretch=1)

        root.addWidget(make_divider_h())

        # ── Bottom bar ──────────────────────────────
        root.addLayout(self._build_bottom_bar())

    def _build_header(self) -> QHBoxLayout:
        hbox = QHBoxLayout()
        hbox.setSpacing(0)

        prefix = QLabel("ĐỘNG HỌC ")
        prefix.setObjectName("main_title")
        suffix = QLabel("ROBOT")
        suffix.setObjectName("title_accent")

        hbox.addStretch()
        hbox.addWidget(prefix)
        hbox.addWidget(suffix)
        hbox.addStretch()

        # Status indicator on the right
        if KINEMATICS_AVAILABLE:
            self.status_lbl = QLabel("● ENGINE READY")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 13px; letter-spacing:1px;")
        else:
            self.status_lbl = QLabel("● PLACEHOLDER MODE")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_AMBER}; font-size: 13px; letter-spacing:1px;")
        hbox.addWidget(self.status_lbl)
        return hbox

    def _build_ik_panel(self) -> QWidget:
        """Left panel — Inverse Kinematics: user inputs X,Y,Z → outputs Θ1,Θ2,Θ3"""
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(48, 30, 48, 30)
        vbox.setSpacing(18)

        title = QLabel("◈  ĐỘNG HỌC NGHỊCH")
        title.setObjectName("section_title")
        vbox.addWidget(title)

        subtitle = QLabel("Inverse Kinematics  ·  XYZ → Θ")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; letter-spacing:2px;")
        vbox.addWidget(subtitle)

        vbox.addSpacing(10)
        vbox.addWidget(make_divider_h())
        vbox.addSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        # ── Inputs ──
        in_header = QLabel("INPUT")
        in_header.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; letter-spacing:3px;")
        grid.addWidget(in_header, 0, 0, 1, 2)

        self.ik_x = make_input("X (mm)")
        self.ik_y = make_input("Y (mm)")
        self.ik_z = make_input("Z (mm)")

        for row, (lbl, widget) in enumerate([("X", self.ik_x), ("Y", self.ik_y), ("Z", self.ik_z)], start=1):
            grid.addWidget(make_label(lbl), row, 0)
            grid.addWidget(widget, row, 1)

        vbox.addLayout(grid)

        # Arrow indicator
        arrow = QLabel("↓  COMPUTE")
        arrow.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 14px; letter-spacing:3px;")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(arrow)

        # ── Outputs ──
        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(18)
        grid2.setVerticalSpacing(18)

        out_header = QLabel("OUTPUT  (READ ONLY)")
        out_header.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; letter-spacing:3px;")
        grid2.addWidget(out_header, 0, 0, 1, 2)

        self.ik_t1 = make_result()
        self.ik_t2 = make_result()
        self.ik_t3 = make_result()

        for row, (lbl, widget) in enumerate(
            [("Θ₁  (°)", self.ik_t1), ("Θ₂  (°)", self.ik_t2), ("Θ₃  (°)", self.ik_t3)], start=1
        ):
            grid2.addWidget(make_label(lbl), row, 0)
            grid2.addWidget(widget, row, 1)

        vbox.addLayout(grid2)
        vbox.addStretch()

        # Wire signals
        for field in (self.ik_x, self.ik_y, self.ik_z):
            field.textChanged.connect(lambda _: self._ik_timer.start())
            field.returnPressed.connect(self._compute_ik)

        return panel

    def _build_fk_panel(self) -> QWidget:
        """Right panel — Forward Kinematics: user inputs Θ1,Θ2,Θ3 → outputs X,Y,Z"""
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(48, 30, 48, 30)
        vbox.setSpacing(18)

        title = QLabel("◈  ĐỘNG HỌC THUẬN")
        title.setObjectName("section_title")
        title.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 18px; font-weight: bold; letter-spacing:4px;")
        vbox.addWidget(title)

        subtitle = QLabel("Forward Kinematics  ·  Θ → XYZ")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; letter-spacing:2px;")
        vbox.addWidget(subtitle)

        vbox.addSpacing(10)
        vbox.addWidget(make_divider_h())
        vbox.addSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        in_header = QLabel("INPUT")
        in_header.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; letter-spacing:3px;")
        grid.addWidget(in_header, 0, 0, 1, 2)

        self.fk_t1 = make_input("Θ₁ (°)")
        self.fk_t2 = make_input("Θ₂ (°)")
        self.fk_t3 = make_input("Θ₃ (°)")

        for row, (lbl, widget) in enumerate(
            [("Θ₁  (°)", self.fk_t1), ("Θ₂  (°)", self.fk_t2), ("Θ₃  (°)", self.fk_t3)], start=1
        ):
            grid.addWidget(make_label(lbl), row, 0)
            grid.addWidget(widget, row, 1)

        vbox.addLayout(grid)

        arrow = QLabel("↓  COMPUTE")
        arrow.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 14px; letter-spacing:3px;")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(arrow)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(18)
        grid2.setVerticalSpacing(18)

        out_header = QLabel("OUTPUT  (READ ONLY)")
        out_header.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; letter-spacing:3px;")
        grid2.addWidget(out_header, 0, 0, 1, 2)

        self.fk_x = make_result()
        self.fk_y = make_result()
        self.fk_z = make_result()

        self.fk_x.setStyleSheet(f"background-color: {RESULT_BG}; border: 1px solid #1a3a20; border-radius:6px; color: {ACCENT_GREEN}; font-size:18px; font-family:'Consolas',monospace; padding:10px 16px; min-height:48px;")
        self.fk_y.setStyleSheet(self.fk_x.styleSheet())
        self.fk_z.setStyleSheet(self.fk_x.styleSheet())

        for row, (lbl, widget) in enumerate([("X  (mm)", self.fk_x), ("Y  (mm)", self.fk_y), ("Z  (mm)", self.fk_z)], start=1):
            grid2.addWidget(make_label(lbl), row, 0)
            grid2.addWidget(widget, row, 1)

        vbox.addLayout(grid2)
        vbox.addStretch()

        for field in (self.fk_t1, self.fk_t2, self.fk_t3):
            field.textChanged.connect(lambda _: self._fk_timer.start())
            field.returnPressed.connect(self._compute_fk)

        return panel

    def _build_bottom_bar(self) -> QHBoxLayout:
        hbox = QHBoxLayout()
        hbox.setSpacing(16)

        btn_grip = QPushButton("  GẤP  ")
        btn_grip.setObjectName("btn_grip")
        btn_grip.clicked.connect(self._on_grip)

        btn_release = QPushButton("  THẢ  ")
        btn_release.setObjectName("btn_release")
        btn_release.clicked.connect(self._on_release)

        btn_home = QPushButton("  HOME  ")
        btn_home.setObjectName("btn_home")
        btn_home.clicked.connect(self._on_home)

        btn_back = QPushButton("  TRỞ VỀ  ")
        btn_back.setObjectName("btn_back")
        btn_back.clicked.connect(self._on_back)

        hbox.addWidget(btn_grip)
        hbox.addWidget(btn_release)
        hbox.addWidget(btn_home)
        hbox.addStretch()
        hbox.addWidget(btn_back)

        return hbox

    # ── Kinematics Computation ───────────────────────────────────────────

    def _get_float(self, field: QLineEdit):
        """Safely parse float from a QLineEdit; returns None on failure."""
        txt = field.text().strip()
        if not txt:
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    def _compute_ik(self):
        x = self._get_float(self.ik_x)
        y = self._get_float(self.ik_y)
        z = self._get_float(self.ik_z)

        if None in (x, y, z):
            self._clear_fields(self.ik_t1, self.ik_t2, self.ik_t3)
            return

        if self.kin:
            result = self.kin.inverse_kinematics(x, y, z)
        else:
            result = (x, y, z)  # placeholder identity

        if result is None:
            self._set_error(self.ik_t1, self.ik_t2, self.ik_t3)
        else:
            t1, t2, t3 = result
            self.ik_t1.setText(str(t1))
            self.ik_t2.setText(str(t2))
            self.ik_t3.setText(str(t3))

    def _compute_fk(self):
        t1 = self._get_float(self.fk_t1)
        t2 = self._get_float(self.fk_t2)
        t3 = self._get_float(self.fk_t3)

        if None in (t1, t2, t3):
            self._clear_fields(self.fk_x, self.fk_y, self.fk_z)
            return

        if self.kin:
            result = self.kin.forward_kinematics(t1, t2, t3)
        else:
            result = (t1, t2, t3)  # placeholder identity

        if result is None:
            self._set_error(self.fk_x, self.fk_y, self.fk_z)
        else:
            rx, ry, rz = result
            self.fk_x.setText(str(rx))
            self.fk_y.setText(str(ry))
            self.fk_z.setText(str(rz))

    def _clear_fields(self, *fields):
        for f in fields:
            f.clear()

    def _set_error(self, *fields):
        for f in fields:
            f.setText("ERR")

    # ── Button Handlers ──────────────────────────────────────────────────

    def _on_grip(self):
        print("[ACTION] GẤP — gripper close signal sent")
        self.status_lbl.setText("● GẤP")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_AMBER}; font-size:13px; letter-spacing:1px;")
        QTimer.singleShot(2000, self._reset_status)

    def _on_release(self):
        print("[ACTION] THẢ — gripper open signal sent")
        self.status_lbl.setText("● THẢ")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size:13px; letter-spacing:1px;")
        QTimer.singleShot(2000, self._reset_status)

    def _on_home(self):
        print("[ACTION] HOME — moving to home position")
        self.status_lbl.setText("● HOMING...")
        self.status_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size:13px; letter-spacing:1px;")
        # Clear all fields on HOME
        for f in (self.ik_x, self.ik_y, self.ik_z, self.ik_t1, self.ik_t2, self.ik_t3,
                  self.fk_t1, self.fk_t2, self.fk_t3, self.fk_x, self.fk_y, self.fk_z):
            f.clear()
        QTimer.singleShot(2000, self._reset_status)

    def _on_back(self):
        print("[ACTION] TRỞ VỀ — returning to previous screen")
        self.close()

    def _reset_status(self):
        if KINEMATICS_AVAILABLE:
            self.status_lbl.setText("● ENGINE READY")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size:13px; letter-spacing:1px;")
        else:
            self.status_lbl.setText("● PLACEHOLDER MODE")
            self.status_lbl.setStyleSheet(f"color: {ACCENT_AMBER}; font-size:13px; letter-spacing:1px;")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette baseline so native widgets don't bleed light colors
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base,            QColor(INPUT_BG))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(PANEL_BG))
    palette.setColor(QPalette.ColorRole.Text,            QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button,          QColor(PANEL_BG))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT_CYAN))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(DARK_BG))
    app.setPalette(palette)

    window = RobotControlGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
