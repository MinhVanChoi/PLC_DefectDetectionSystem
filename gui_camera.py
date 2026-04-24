import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QFrame,
    QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

# Serial port scanning
try:
    import serial.tools.list_ports as list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[WARN] pyserial không tìm thấy — COM list sẽ trống.")

# ─────────────────────────────────────────────────────────────────────────────
#  Shared Design Tokens  (identical to gui_robot.py)
# ─────────────────────────────────────────────────────────────────────────────
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

# LED states
LED_OFF      = "#1e2535"
LED_GREEN    = "#00ff9d"
LED_RED      = "#ff4757"
LED_AMBER    = "#ffb700"
LED_BLUE     = "#00d4ff"

# ─────────────────────────────────────────────────────────────────────────────
#  Stylesheet
# ─────────────────────────────────────────────────────────────────────────────
STYLE_SHEET = f"""
/* ── Global ── */
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Consolas', 'Courier New', monospace;
}}

/* ── Panels / frames ── */
QFrame#card {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
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

/* ── Section headings ── */
QLabel#section_title {{
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 2px 0px;
}}
QLabel#section_title_cyan  {{ color: {ACCENT_CYAN};  }}
QLabel#section_title_green {{ color: {ACCENT_GREEN}; }}
QLabel#section_title_amber {{ color: {ACCENT_AMBER}; }}
QLabel#section_title_red   {{ color: {ACCENT_RED};   }}

/* ── Generic body labels ── */
QLabel#body {{
    color: {TEXT_MUTED};
    font-size: 13px;
    letter-spacing: 1px;
}}

/* ── Value display boxes ── */
QLabel#value_box {{
    background-color: {INPUT_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 5px;
    color: {ACCENT_CYAN};
    font-size: 16px;
    font-weight: bold;
    padding: 4px 10px;
}}

/* ── Camera frame ── */
QLabel#camera_frame {{
    background-color: #080a10;
    border: 2px solid {BORDER_COLOR};
    border-radius: 8px;
    color: {TEXT_MUTED};
    font-size: 13px;
}}

/* ── Checkboxes (detection filters) ── */
QCheckBox {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    letter-spacing: 1px;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: {INPUT_BG};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT_CYAN};
    border: 2px solid {ACCENT_CYAN};
    image: none;
}}
QCheckBox::indicator:hover {{
    border: 2px solid {ACCENT_CYAN};
}}
QCheckBox#status_check::indicator:checked {{
    background-color: {ACCENT_GREEN};
    border: 2px solid {ACCENT_GREEN};
}}

/* ── Navigation buttons ── */
QPushButton#btn_robot {{
    background-color: transparent;
    border: 2px solid {ACCENT_CYAN};
    border-radius: 7px;
    color: {ACCENT_CYAN};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 140px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_robot:hover {{
    background-color: {ACCENT_CYAN};
    color: {DARK_BG};
}}

QPushButton#btn_exit {{
    background-color: transparent;
    border: 2px solid {ACCENT_RED};
    border-radius: 7px;
    color: {ACCENT_RED};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 3px;
    padding: 12px 40px;
    min-width: 140px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_exit:hover {{
    background-color: {ACCENT_RED};
    color: {TEXT_PRIMARY};
}}

/* ── Divider ── */
QFrame#divider_h {{
    background-color: {BORDER_COLOR};
    max-height: 1px;
}}
QFrame#divider_v {{
    background-color: {BORDER_COLOR};
    max-width: 1px;
}}

/* ── COM combo box ── */
QComboBox#com_combo {{
    background-color: {INPUT_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 5px;
    color: {ACCENT_CYAN};
    font-size: 13px;
    font-family: 'Consolas', monospace;
    padding: 4px 10px;
    min-height: 32px;
    min-width: 160px;
}}
QComboBox#com_combo:focus {{
    border: 1px solid {ACCENT_CYAN};
}}
QComboBox#com_combo::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox#com_combo::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {ACCENT_CYAN};
    width: 0;
    height: 0;
    margin-right: 6px;
}}
QComboBox#com_combo QAbstractItemView {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_CYAN};
    selection-color: {DARK_BG};
    font-size: 13px;
    padding: 4px;
}}

/* ── PLC IP input ── */
QLineEdit#plc_input {{
    background-color: {INPUT_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 5px;
    color: {ACCENT_CYAN};
    font-size: 13px;
    font-family: 'Consolas', monospace;
    padding: 4px 10px;
    min-height: 32px;
    min-width: 180px;
}}
QLineEdit#plc_input:focus {{
    border: 1px solid {ACCENT_CYAN};
    background-color: #1e2840;
}}

/* ── Confirm / Refresh buttons (small inline) ── */
QPushButton#btn_confirm {{
    background-color: transparent;
    border: 1px solid {ACCENT_GREEN};
    border-radius: 5px;
    color: {ACCENT_GREEN};
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 4px 14px;
    min-height: 32px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_confirm:hover {{
    background-color: {ACCENT_GREEN};
    color: {DARK_BG};
}}
QPushButton#btn_confirm:pressed {{
    background-color: #00cc7a;
}}

QPushButton#btn_refresh {{
    background-color: transparent;
    border: 1px solid {ACCENT_AMBER};
    border-radius: 5px;
    color: {ACCENT_AMBER};
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 4px 14px;
    min-height: 32px;
    font-family: 'Consolas', monospace;
}}
QPushButton#btn_refresh:hover {{
    background-color: {ACCENT_AMBER};
    color: {DARK_BG};
}}

/* ── Connection status badge ── */
QLabel#conn_badge_ok {{
    color: {ACCENT_GREEN};
    font-size: 12px;
    letter-spacing: 1px;
}}
QLabel#conn_badge_err {{
    color: {ACCENT_RED};
    font-size: 12px;
    letter-spacing: 1px;
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  Helper builders
# ─────────────────────────────────────────────────────────────────────────────

def make_card() -> QFrame:
    f = QFrame()
    f.setObjectName("card")
    return f

def make_divider_h() -> QFrame:
    f = QFrame()
    f.setObjectName("divider_h")
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    return f

def make_divider_v() -> QFrame:
    f = QFrame()
    f.setObjectName("divider_v")
    f.setFrameShape(QFrame.Shape.VLine)
    f.setFixedWidth(1)
    return f

def make_section_label(text: str, color_suffix="cyan") -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_title")
    lbl.setProperty("class", f"section_title_{color_suffix}")
    
    color_map = {
        'cyan': ACCENT_CYAN, 
        'green': ACCENT_GREEN, 
        'amber': ACCENT_AMBER, 
        'red': ACCENT_RED
    }
    
    selected_color = color_map.get(color_suffix, ACCENT_CYAN)
    
    lbl.setStyleSheet(f"color: {selected_color}; font-size:14px; font-weight:bold; letter-spacing:3px;")
    
    return lbl

def make_body_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("body")
    lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:13px; letter-spacing:1px;")
    return lbl

def make_led(size=44) -> QLabel:
    lbl = QLabel()
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background-color: {LED_OFF};"
        f"border-radius: {size // 2}px;"
        f"border: 2px solid {BORDER_COLOR};"
    )
    return lbl

def set_led(led: QLabel, color: str, size=44):
    glow = f"0 0 10px {color}, 0 0 20px {color}"
    led.setStyleSheet(
        f"background-color: {color};"
        f"border-radius: {size // 2}px;"
        f"border: 2px solid {color};"
    )

def reset_led(led: QLabel, size=44):
    led.setStyleSheet(
        f"background-color: {LED_OFF};"
        f"border-radius: {size // 2}px;"
        f"border: 2px solid {BORDER_COLOR};"
    )

def make_value_box(text="—") -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("value_box")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setMinimumWidth(60)
    lbl.setMinimumHeight(34)
    return lbl

def make_conn_box(text="—") -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background-color:{INPUT_BG}; border:1px solid {BORDER_COLOR};"
        f"border-radius:5px; color:{ACCENT_GREEN}; font-size:13px; padding:4px 10px;"
    )
    lbl.setMinimumHeight(30)
    return lbl


# ─────────────────────────────────────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────────────────────────────────────

class CameraControlGUI(QMainWindow):
    # ── Signals emitted to AppController ─────────────────────────────────────
    com_connected  = pyqtSignal(str)   # port string e.g. "COM4"  (or "" = None)
    plc_confirmed  = pyqtSignal(str)   # IP string e.g. "192.168.0.1"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Control — Robot Vision")
        self.setFixedSize(1373, 824)
        self._build_ui()
        self.setStyleSheet(STYLE_SHEET)

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(14)

        # Header
        root.addLayout(self._build_header())
        root.addWidget(make_divider_h())

        # Main body: left camera | right panels
        body = QHBoxLayout()
        body.setSpacing(16)
        body.addLayout(self._build_left_column(), stretch=55)
        body.addLayout(self._build_right_column(), stretch=45)
        root.addLayout(body, stretch=1)

        root.addWidget(make_divider_h())

        # Bottom bar
        root.addLayout(self._build_bottom_bar())

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self) -> QHBoxLayout:
        hbox = QHBoxLayout()

        prefix = QLabel("CAMERA ")
        prefix.setObjectName("main_title")
        suffix = QLabel("NHẬN DIỆN")
        suffix.setObjectName("title_accent")

        hbox.addStretch()
        hbox.addWidget(prefix)
        hbox.addWidget(suffix)
        hbox.addStretch()

        self.status_lbl = QLabel("● SYSTEM READY")
        self.status_lbl.setStyleSheet(f"color:{ACCENT_GREEN}; font-size:13px; letter-spacing:1px;")
        hbox.addWidget(self.status_lbl)
        return hbox

    # ── Left column: camera feed + detection filters ─────────────────────────

    def _build_left_column(self) -> QVBoxLayout:
        vbox = QVBoxLayout()
        vbox.setSpacing(12)

        # Camera feed
        cam_card = make_card()
        cam_layout = QVBoxLayout(cam_card)
        cam_layout.setContentsMargins(12, 12, 12, 12)
        cam_layout.setSpacing(8)

        cam_title = make_section_label("◈  CAMERA NHẬN DIỆN", "cyan")
        cam_layout.addWidget(cam_title)
        cam_layout.addWidget(make_divider_h())

        self.khung_camera = QLabel("[ NO SIGNAL ]")
        self.khung_camera.setObjectName("camera_frame")
        self.khung_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.khung_camera.setMinimumHeight(420)
        cam_layout.addWidget(self.khung_camera, stretch=1)

        vbox.addWidget(cam_card, stretch=1)

        # Detection filter checkboxes
        filter_card = make_card()
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 12, 20, 12)
        filter_layout.setSpacing(20)

        filter_title = make_section_label("◈  BỘ LỌC NHẬN DIỆN", "amber")
        filter_layout.addWidget(filter_title)
        filter_layout.addWidget(make_divider_v())

        self.check_nguocmat = QCheckBox("LỖI NGƯỢC MẶT")
        self.check_loichu   = QCheckBox("LỖI CHỮ")
        self.check_loilogo  = QCheckBox("LỖI LOGO")

        for cb in (self.check_nguocmat, self.check_loichu, self.check_loilogo):
            cb.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; letter-spacing:1px; spacing:8px;")
            filter_layout.addWidget(cb)

        filter_layout.addStretch()
        vbox.addWidget(filter_card)

        return vbox

    # ── Right column: results + progress + connection ────────────────────────

    def _build_right_column(self) -> QVBoxLayout:
        vbox = QVBoxLayout()
        vbox.setSpacing(12)

        vbox.addWidget(self._build_result_card())
        vbox.addWidget(self._build_progress_card())
        vbox.addWidget(self._build_connection_card())

        return vbox

    # ── Result card ──────────────────────────────────────────────────────────

    def _build_result_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        title = make_section_label("◈  KẾT QUẢ NHẬN DIỆN", "green")
        layout.addWidget(title)
        layout.addWidget(make_divider_h())

        row = QHBoxLayout()
        row.setSpacing(30)

        # SP ĐẠT
        col_pass = QVBoxLayout()
        col_pass.setSpacing(8)
        col_pass.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.den_sp_dat = make_led(60)
        lbl_pass = QLabel("SP ĐẠT CHUẨN")
        lbl_pass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_pass.setStyleSheet(f"color:{ACCENT_GREEN}; font-size:12px; font-weight:bold; letter-spacing:1px;")
        col_pass.addWidget(self.den_sp_dat, alignment=Qt.AlignmentFlag.AlignHCenter)
        col_pass.addWidget(lbl_pass)

        # Divider
        vdiv = make_divider_v()
        vdiv.setFixedHeight(80)

        # SP LỖI
        col_fail = QVBoxLayout()
        col_fail.setSpacing(8)
        col_fail.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.den_sp_loi = make_led(60)
        lbl_fail = QLabel("SP LỖI")
        lbl_fail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_fail.setStyleSheet(f"color:{ACCENT_RED}; font-size:12px; font-weight:bold; letter-spacing:1px;")
        col_fail.addWidget(self.den_sp_loi, alignment=Qt.AlignmentFlag.AlignHCenter)
        col_fail.addWidget(lbl_fail)

        row.addStretch()
        row.addLayout(col_pass)
        row.addWidget(vdiv, alignment=Qt.AlignmentFlag.AlignVCenter)
        row.addLayout(col_fail)
        row.addStretch()

        layout.addLayout(row)
        return card

    # ── Progress card ────────────────────────────────────────────────────────

    def _build_progress_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(14)

        title = make_section_label("◈  TIẾN TRÌNH", "amber")
        layout.addWidget(title)
        layout.addWidget(make_divider_h())

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)

        # ── Robot status LED ──
        self.den_robot = make_led(40)
        lbl_robot = make_body_label("ROBOT ĐANG GẮP")
        grid.addWidget(self.den_robot, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(lbl_robot, 0, 1)

        # ── Đóng hộp LED ──
        self.den_donghop = make_led(40)
        lbl_donghop = make_body_label("ĐANG ĐÓNG HỘP")
        grid.addWidget(self.den_donghop, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(lbl_donghop, 1, 1)

        # ── Sản phẩm cần gắp còn ──
        lbl_slg = make_body_label("SẢN PHẨM CẦN GẮP CÒN:")
        self.soluong_gap = make_value_box("0")
        h_slg = QHBoxLayout()
        h_slg.addWidget(lbl_slg)
        h_slg.addWidget(self.soluong_gap)
        h_slg.addStretch()
        grid.addLayout(h_slg, 2, 0, 1, 2)

        layout.addLayout(grid)
        layout.addWidget(make_divider_h())

        # ── Status checkboxes ──
        cb_row = QHBoxLayout()
        cb_row.setSpacing(20)
        self.check_gapxong   = QCheckBox("ĐÃ GẮP XONG")
        self.check_donghopxong = QCheckBox("ĐÃ ĐÓNG HỘP XONG")

        for cb in (self.check_gapxong, self.check_donghopxong):
            cb.setObjectName("status_check")
            cb.setStyleSheet(
                f"color:{TEXT_PRIMARY}; font-size:13px; letter-spacing:1px; spacing:8px;"
                f"QCheckBox::indicator {{ width:20px; height:20px; border:2px solid {BORDER_COLOR};"
                f"border-radius:4px; background:{INPUT_BG}; }}"
                f"QCheckBox::indicator:checked {{ background:{ACCENT_GREEN}; border:2px solid {ACCENT_GREEN}; }}"
            )
            cb_row.addWidget(cb)

        cb_row.addStretch()
        layout.addLayout(cb_row)

        return card

    # ── Connection card ───────────────────────────────────────────────────────

    def _build_connection_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(12)

        # ── Header row ──
        hdr = QHBoxLayout()
        title = make_section_label("◈  KẾT NỐI", "cyan")
        hdr.addWidget(title)
        hdr.addStretch()
        # COM status badge
        self._com_badge = QLabel("○  CHƯA KẾT NỐI")
        self._com_badge.setObjectName("conn_badge_err")
        hdr.addWidget(self._com_badge)
        layout.addLayout(hdr)
        layout.addWidget(make_divider_h())

        # ── COM row ──
        com_row = QHBoxLayout()
        com_row.setSpacing(10)

        lbl_com = make_body_label("COM :")
        lbl_com.setFixedWidth(60)

        self.com_combo = QComboBox()
        self.com_combo.setObjectName("com_combo")
        self.com_combo.setPlaceholderText("None")
        self._refresh_com_list()            # populate on start

        btn_refresh = QPushButton("↻  SCAN")
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.setToolTip("Quét lại danh sách cổng COM")
        btn_refresh.clicked.connect(self._refresh_com_list)

        btn_com_connect = QPushButton("KẾT NỐI")
        btn_com_connect.setObjectName("btn_confirm")
        btn_com_connect.clicked.connect(self._on_com_connect)

        com_row.addWidget(lbl_com)
        com_row.addWidget(self.com_combo)
        com_row.addWidget(btn_refresh)
        com_row.addWidget(btn_com_connect)
        com_row.addStretch()
        layout.addLayout(com_row)

        layout.addWidget(make_divider_h())

        # ── PLC row ──
        plc_row = QHBoxLayout()
        plc_row.setSpacing(10)

        lbl_plc = make_body_label("PLC IP :")
        lbl_plc.setFixedWidth(70)

        self.plc_input = QLineEdit()
        self.plc_input.setObjectName("plc_input")
        self.plc_input.setPlaceholderText("192.168.0.1")
        self.plc_input.returnPressed.connect(self._on_plc_confirm)

        btn_plc_confirm = QPushButton("XÁC NHẬN")
        btn_plc_confirm.setObjectName("btn_confirm")
        btn_plc_confirm.clicked.connect(self._on_plc_confirm)

        self._plc_badge = QLabel("○  CHƯA KẾT NỐI")
        self._plc_badge.setObjectName("conn_badge_err")

        plc_row.addWidget(lbl_plc)
        plc_row.addWidget(self.plc_input)
        plc_row.addWidget(btn_plc_confirm)
        plc_row.addWidget(self._plc_badge)
        plc_row.addStretch()
        layout.addLayout(plc_row)

        return card

    # ── COM helpers ──────────────────────────────────────────────────────────

    def _refresh_com_list(self):
        """Quét lại tất cả cổng COM đang kết nối và cập nhật combobox."""
        self.com_combo.clear()
        self.com_combo.addItem("None")      # luôn có option trống ở đầu

        if SERIAL_AVAILABLE:
            ports = list_ports.comports()
            for p in sorted(ports, key=lambda x: x.device):
                # Hiện "COM4 — CP210x (Silicon Labs)" cho dễ nhận biết ESP32
                desc = p.description or ""
                display = f"{p.device}  —  {desc}" if desc else p.device
                self.com_combo.addItem(display, userData=p.device)
        else:
            # Fallback: thêm một vài cổng phổ biến nếu pyserial chưa cài
            for c in ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]:
                self.com_combo.addItem(c, userData=c)

        # Reset badge về chờ
        self._com_badge.setText("○  CHƯA KẾT NỐI")
        self._com_badge.setObjectName("conn_badge_err")
        self._com_badge.setStyleSheet(f"color:{ACCENT_RED}; font-size:12px; letter-spacing:1px;")

    def _on_com_connect(self):
        """Gọi khi người dùng nhấn 'KẾT NỐI' ở phần COM."""
        idx = self.com_combo.currentIndex()
        port = self.com_combo.currentData()   # userData = device string e.g. "COM4"

        if idx == 0 or port is None:
            self._com_badge.setText("○  NONE")
            self._com_badge.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; letter-spacing:1px;")
            self.com_connected.emit("")
            return

        # Phát signal ra ngoài để AppController xử lý thực sự
        self._com_badge.setText(f"● {port}")
        self._com_badge.setStyleSheet(f"color:{ACCENT_AMBER}; font-size:12px; letter-spacing:1px;")
        self.com_connected.emit(port)

    def set_com_status(self, port: str, success: bool):
        """Gọi từ AppController sau khi connect_serial() trả về kết quả."""
        if success:
            self._com_badge.setText(f"●  {port}  OK")
            self._com_badge.setStyleSheet(f"color:{ACCENT_GREEN}; font-size:12px; letter-spacing:1px;")
        else:
            self._com_badge.setText(f"✕  {port}  LỖI")
            self._com_badge.setStyleSheet(f"color:{ACCENT_RED}; font-size:12px; letter-spacing:1px;")

    # ── PLC helpers ──────────────────────────────────────────────────────────

    def _on_plc_confirm(self):
        """Gọi khi người dùng nhấn 'XÁC NHẬN' hoặc Enter ở PLC input."""
        ip = self.plc_input.text().strip()
        if not ip:
            ip = self.plc_input.placeholderText()  # dùng default nếu trống

        self._plc_badge.setText(f"● {ip}  …")
        self._plc_badge.setStyleSheet(f"color:{ACCENT_AMBER}; font-size:12px; letter-spacing:1px;")
        self.plc_confirmed.emit(ip)

    def set_plc_status(self, ip: str, success: bool):
        """Gọi từ AppController sau khi PLCHandler.connect() trả về kết quả."""
        if success:
            self._plc_badge.setText(f"●  {ip}  OK")
            self._plc_badge.setStyleSheet(f"color:{ACCENT_GREEN}; font-size:12px; letter-spacing:1px;")
        else:
            self._plc_badge.setText(f"✕  {ip}  LỖI")
            self._plc_badge.setStyleSheet(f"color:{ACCENT_RED}; font-size:12px; letter-spacing:1px;")

    # ── Bottom bar ────────────────────────────────────────────────────────────

    def _build_bottom_bar(self) -> QHBoxLayout:
        hbox = QHBoxLayout()
        hbox.setSpacing(16)

        self.bt_donghoc = QPushButton("  ROBOT  ")
        self.bt_donghoc.setObjectName("btn_robot")
        self.bt_donghoc.clicked.connect(self._on_robot)

        self.bt_thoat = QPushButton("  THOÁT  ")
        self.bt_thoat.setObjectName("btn_exit")
        self.bt_thoat.clicked.connect(self._on_exit)

        hbox.addStretch()
        hbox.addWidget(self.bt_donghoc)
        hbox.addWidget(self.bt_thoat)

        return hbox

    # ── Public API (for integration) ─────────────────────────────────────────

    def set_camera_frame(self, pixmap):
        """Feed a QPixmap from OpenCV/camera capture."""
        self.khung_camera.setPixmap(
            pixmap.scaled(
                self.khung_camera.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def set_result(self, passed: bool):
        """Light up SP ĐẠT (green) or SP LỖI (red)."""
        if passed:
            set_led(self.den_sp_dat, LED_GREEN, 60)
            reset_led(self.den_sp_loi, 60)
        else:
            reset_led(self.den_sp_dat, 60)
            set_led(self.den_sp_loi, LED_RED, 60)

    def set_robot_active(self, active: bool):
        if active:
            set_led(self.den_robot, LED_AMBER, 40)
        else:
            reset_led(self.den_robot, 40)

    def set_packing_active(self, active: bool):
        if active:
            set_led(self.den_donghop, LED_BLUE, 40)
        else:
            reset_led(self.den_donghop, 40)

    def set_remaining_count(self, count: int):
        self.soluong_gap.setText(str(count))

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_robot(self):
        """Open robot kinematics window (import gui_robot)."""
        print("[NAV] → ROBOT window")
        try:
            from gui_robot import RobotControlGUI
            self._robot_win = RobotControlGUI()
            self._robot_win.show()
        except ImportError:
            print("[WARN] gui_robot.py not found in same directory.")
        self._flash_status("● SWITCHING TO ROBOT", ACCENT_CYAN)

    def _on_exit(self):
        print("[ACTION] THOÁT")
        self.close()

    def _flash_status(self, text: str, color: str):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"color:{color}; font-size:13px; letter-spacing:1px;")
        QTimer.singleShot(2000, self._reset_status)

    def _reset_status(self):
        self.status_lbl.setText("● SYSTEM READY")
        self.status_lbl.setStyleSheet(f"color:{ACCENT_GREEN}; font-size:13px; letter-spacing:1px;")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

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

    window = CameraControlGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()