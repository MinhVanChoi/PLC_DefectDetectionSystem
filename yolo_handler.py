"""
main.py  —  Entry point
Điều phối giữa CameraControlGUI, RobotControlGUI, RobotController và PLCHandler.

Cấu trúc file trong cùng thư mục:
    main.py
    gui_camera.py
    gui_robot.py
    kinematic.py
    robot_controller.py
    plc_handler.py   (class PLCHandler)
    best.pt
"""

import sys
import cv2
import numpy as np

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QImage, QPixmap
from PyQt6.QtCore    import Qt, QThread, pyqtSignal

from gui_camera  import (
    CameraControlGUI,
    set_led, reset_led,
    LED_GREEN, LED_RED, LED_AMBER, LED_BLUE,
    ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, ACCENT_CYAN,
)
from gui_robot        import RobotControlGUI
from robot_controller import RobotController

# PLCHandler — import có điều kiện
try:
    from PLC_handler import PLCHandler
    PLC_AVAILABLE = True
except ImportError:
    PLC_AVAILABLE = False
    print("[WARN] plc_handler.py không tìm thấy — PLC sẽ bị bỏ qua.")

# YOLO — import có điều kiện
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARN] ultralytics không tìm thấy — camera sẽ chạy không có YOLO.")


# ─────────────────────────────────────────────────────────────────────────────
#  VideoThread
# ─────────────────────────────────────────────────────────────────────────────

class VideoThread(QThread):
    """
    Phát ra 2 signal mỗi frame:
      • frame_signal   : np.ndarray  (BGR image)
      • detect_signal  : list[str]   (tên class YOLO detect được)
    """
    frame_signal  = pyqtSignal(np.ndarray)
    detect_signal = pyqtSignal(list)

    def __init__(self, model_path: str = "best.pt", camera_index: int = 0):
        super().__init__()
        self._run_flag = True
        self.camera_index = camera_index

        self.model = None
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_path)
                print(f"[YOLO] Model '{model_path}' đã nạp thành công.")
            except Exception as e:
                print(f"[YOLO] Không nạp được model: {e}")

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("[CAMERA] Không mở được camera!")
            return

        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            detected_classes: list[str] = []

            if self.model is not None:
                results = self.model(frame, stream=True)
                for r in results:
                    for c in r.boxes.cls:
                        detected_classes.append(self.model.names[int(c)])
                    frame = r.plot()

            self.frame_signal.emit(frame)
            self.detect_signal.emit(detected_classes)

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


# ─────────────────────────────────────────────────────────────────────────────
#  AppController
# ─────────────────────────────────────────────────────────────────────────────

class AppController:
    """
    Controller thuần tuý — không kế thừa QMainWindow.
    Giữ tham chiếu tới:
        • self.cam_win    : CameraControlGUI
        • self.robot_ctrl : RobotController (QThread)
        • self.plc        : PLCHandler | None
        • self.video      : VideoThread
        • self.robot_win  : RobotControlGUI  (tạo khi cần)
    """

    def __init__(self):
        # ── 1. Cửa sổ Camera ────────────────────────────────────────────────
        self.cam_win = CameraControlGUI()

        # ── 2. Robot Controller ──────────────────────────────────────────────
        self.robot_ctrl = RobotController()
        self.robot_ctrl.status_signal.connect(self._on_robot_status)
        self.robot_ctrl.started.connect(self._on_robot_started)
        self.robot_ctrl.finished.connect(self._on_robot_finished)

        # ── 3. PLC Handler ───────────────────────────────────────────────────
        self.plc: PLCHandler | None = PLCHandler() if PLC_AVAILABLE else None

        # ── 4. Gắn nút ROBOT → mở RobotControlGUI ──────────────────────────
        self.cam_win.bt_donghoc.clicked.disconnect()
        self.cam_win.bt_donghoc.clicked.connect(self._open_robot_window)

        # ── 5. Gắn signals COM / PLC từ connection card ──────────────────────
        self.cam_win.com_connected.connect(self._on_com_connect)
        self.cam_win.plc_confirmed.connect(self._on_plc_confirm)

        # ── 6. Luồng camera + YOLO ───────────────────────────────────────────
        self.video = VideoThread(model_path="best.pt", camera_index=0)
        self.video.frame_signal.connect(self._on_new_frame)
        self.video.detect_signal.connect(self._on_detection)
        self.video.start()

        # Đóng app đúng cách
        self.cam_win.closeEvent = self._on_close

    # ── COM ───────────────────────────────────────────────────────────────────

    def _on_com_connect(self, port: str):
        """
        Nhận port string từ cam_win.com_connected signal.
        port == "" nghĩa là người dùng chọn None.
        """
        if not port:
            print("[COM] Người dùng chọn None — bỏ qua kết nối.")
            return

        success = self.robot_ctrl.connect_serial(port)
        self.cam_win.set_com_status(port, success)

        if success:
            print(f"[COM] Đã kết nối Robot tại {port}")
            self.cam_win._flash_status(f"● CONNECTED  {port}", ACCENT_GREEN)
        else:
            print(f"[COM] Thất bại tại {port}. Kiểm tra cáp!")
            self.cam_win._flash_status(f"● COM FAILED  {port}", ACCENT_RED)

    # ── PLC ───────────────────────────────────────────────────────────────────

    def _on_plc_confirm(self, ip: str):
        """Nhận IP string từ cam_win.plc_confirmed signal."""
        if self.plc is None:
            print(f"[PLC] PLCHandler không khả dụng — bỏ qua {ip}.")
            self.cam_win.set_plc_status(ip, False)
            return

        self.plc.ip = ip
        success = self.plc.connect()
        self.cam_win.set_plc_status(ip, success)

        if success:
            print(f"[PLC] Đã kết nối PLC tại {ip}")
            self.cam_win._flash_status(f"● PLC OK  {ip}", ACCENT_GREEN)
        else:
            print(f"[PLC] Thất bại tại {ip}. Kiểm tra mạng!")
            self.cam_win._flash_status(f"● PLC FAILED  {ip}", ACCENT_RED)

    # ── Mở cửa sổ Robot ───────────────────────────────────────────────────────

    def _open_robot_window(self):
        self.robot_win = RobotControlGUI(self.robot_ctrl)
        self.robot_win.show()
        self.cam_win._flash_status("● ROBOT WINDOW OPENED", ACCENT_CYAN)

    # ── Camera frame ──────────────────────────────────────────────────────────

    def _on_new_frame(self, cv_img: np.ndarray):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        q_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)

        lbl = self.cam_win.khung_camera
        pixmap = QPixmap.fromImage(q_img).scaled(
            lbl.width(), lbl.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        lbl.setPixmap(pixmap)

    # ── YOLO detection ────────────────────────────────────────────────────────

    def _on_detection(self, detected: list[str]):
        has_logo  = "LoiLogo"  in detected
        has_chu   = "LoiChu"   in detected
        has_nguoc = "NguocMat" in detected
        has_item  = len(detected) > 0
        is_ok     = has_item and not (has_logo or has_chu or has_nguoc)

        # Checkbox bộ lọc
        self.cam_win.check_loilogo.setChecked(has_logo)
        self.cam_win.check_loichu.setChecked(has_chu)
        self.cam_win.check_nguocmat.setChecked(has_nguoc)

        # LED đạt / lỗi
        if has_logo or has_chu or has_nguoc:
            self.cam_win.set_result(passed=False)
        elif has_item:
            self.cam_win.set_result(passed=True)
        else:
            reset_led(self.cam_win.den_sp_dat, 60)
            reset_led(self.cam_win.den_sp_loi, 60)

        # Tự động chạy Robot nếu SP đạt và robot đang rảnh
        serial_ok = (
            hasattr(self.robot_ctrl, "ser")
            and self.robot_ctrl.ser is not None
            and self.robot_ctrl.ser.is_open
        )
        if is_ok and serial_ok and not self.robot_ctrl.isRunning():
            self.robot_ctrl.start()

    # ── Robot status callbacks ────────────────────────────────────────────────

    def _on_robot_status(self, message: str, color: str):
        print(f"[ROBOT STATUS] {message}")
        self.cam_win.status_lbl.setText(f"● {message}")
        self.cam_win.status_lbl.setStyleSheet(
            f"color:{color}; font-size:13px; letter-spacing:1px;"
        )

    def _on_robot_started(self):
        self.cam_win.set_robot_active(True)
        self.cam_win.check_gapxong.setChecked(False)

    def _on_robot_finished(self):
        self.cam_win.set_robot_active(False)
        self.cam_win.check_gapxong.setChecked(True)
        self.cam_win._flash_status("● ROBOT IDLE", ACCENT_GREEN)

    # ── Close ─────────────────────────────────────────────────────────────────

    def _on_close(self, event):
        print("[APP] Đang tắt hệ thống...")
        self.video.stop()
        if self.robot_ctrl.isRunning():
            self.robot_ctrl.stop()
        if self.plc:
            self.plc.disconnect()
        event.accept()

    def show(self):
        self.cam_win.show()


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    controller = AppController()
    controller.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()