import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal
from kinematic import RobotKinematics

class RobotController(QThread):
    # Các tín hiệu gửi về giao diện chính
    status_signal = pyqtSignal(str, str) # (Nội dung thông báo, màu sắc)
    step_finished_signal = pyqtSignal(int) # Báo bước vừa xong

    def __init__(self):
        super().__init__()
        self.robot = RobotKinematics()
        self.ser = None
        self.is_running = False
        
        # Quỹ đạo 11 bước (X, Y, Z)
        self.trajectory = [
            (0, 250, 334.5), (0, 250, 150), (0, 250, 70),  # Bước 1-3 (B3 Gắp)
            (0, 250, 334.5), (250, 0, 334.5), (0, -250, 334.5), # Bước 4-6
            (0, -250, 250), (0, -250, 150), (0, -250, 250), # Bước 7-9 (B8 Thả)
            (0, -250, 334.5), (250, 0, 334.5) # Bước 10-11
        ]

    def connect_serial(self, port):
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2) # Chờ ESP32 khởi động lại sau khi mở cổng Serial
            
            # --- THÊM TỰ ĐỘNG GỬI HOME KHI KẾT NỐI ---
            self.send_raw("HOME") 
            return True
        except:
            return False

    def send_ik_command(self, x, y, z):
        # Tính toán động học nghịch
        angles = self.robot.inverse_kinematics(x, y, z)
        if angles:
            q1, q2, q3 = angles
            # Format lệnh: X{q3} Y{q2} Z{q1}
            command = f"X{q3} Y{q2} Z{q1}\n"
            if self.ser and self.ser.is_open:
                self.ser.write(command.encode())
                return True
        return False

    def send_raw(self, cmd):
        if self.ser and self.ser.is_open:
            self.ser.write((cmd + "\n").encode())
            # In ra console để kiểm tra
            print(f"Đã gửi lệnh: {cmd}")

    def run(self):
        """Hàm thực hiện trình tự 11 bước gắp thả"""
        self.is_running = True
        
        # Gửi HOME một lần nữa khi bắt đầu chu trình chạy nếu cần chắc chắn
        self.send_raw("HOME")
        time.sleep(1)
        
        try:
            for i, (x, y, z) in enumerate(self.trajectory):
                if not self.is_running: break
                
                step_num = i + 1
                self.status_signal.emit(f"Bước {step_num}: Tới ({x}, {y}, {z})", "cyan")

                # 1. Gửi lệnh di chuyển
                if self.send_ik_command(x, y, z):
                    time.sleep(2.7) 

                    # 2. Xử lý tác vụ AUTO GAP/THA
                    if step_num == 3:
                        self.status_signal.emit("BƯỚC 3: ĐANG GẮP...", "yellow")
                        self.send_raw("GAP")
                        time.sleep(1)
                    
                    if step_num == 8:
                        self.status_signal.emit("BƯỚC 8: ĐANG THẢ...", "yellow")
                        self.send_raw("THA")
                        time.sleep(1)
                    
                    self.step_finished_signal.emit(step_num)
                else:
                    self.status_signal.emit(f"LỖI: Bước {step_num} ngoài tầm với!", "red")
                    time.sleep(1)

            self.status_signal.emit("HOÀN THÀNH TRÌNH TỰ!", "green")
            # Sau khi xong 11 bước, quay về HOME
            self.send_raw("HOME")
            
        except Exception as e:
            self.status_signal.emit(f"LỖI ROBOT: {str(e)}", "red")
        finally:
            self.is_running = False

    def stop(self):
        self.is_running = False
        self.wait()