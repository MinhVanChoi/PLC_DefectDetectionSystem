import math

class RobotKinematics:
    def __init__(self):
        # --- KÍCH THƯỚC ROBOT (mm) ---
        self.l1 = 134.5  # Độ cao từ đế đến khớp J2
        self.l2 = 200.0  # Chiều dài cánh tay chính
        self.l3 = 200.0  # Chiều dài cánh tay phụ
        self.l4 = 55.0   # Tool offset (khoảng cách từ khớp cuối đến điểm gắp)

    def rad_to_deg(self, rad):
        return rad * 180.0 / math.pi

    def inverse_kinematics(self, x, y, z):
        try:
            # 1. J1: Xoay đế
            theta1 = math.atan2(y, x)

            # 2. Tính toạ độ khớp 3 (sau khi trừ phần l4) so với gốc toạ độ base
            x3 = x - self.l4 * math.cos(theta1)
            y3 = y - self.l4 * math.sin(theta1)
            z3 = z - self.l1
            
            # Khoảng cách từ khớp 2 đến khớp 3 trong không gian 3D
            r = math.sqrt(x3 ** 2 + y3 ** 2 + z3 ** 2)

            # 3. J3 (Định lý hàm cos) - Sử dụng r để tìm góc giữa l2 và l3
            cos_t3 = (r ** 2 - self.l2 ** 2 - self.l3 ** 2) / (2 * self.l2 * self.l3)
            cos_t3 = max(-1.0, min(1.0, cos_t3))  # Giới hạn tránh lỗi math
            theta3 = -math.acos(cos_t3)  # Elbow-down configuration

            # 4. J2: Tính dựa trên hình chiếu phẳng
            # Dùng atan2 thay cho asin(z3/r) để ổn định hơn ở mọi góc độ
            planar_dist = math.sqrt(x3**2 + y3**2)
            alpha = math.atan2(z3, planar_dist)
            beta = -math.atan2(self.l3 * math.sin(theta3), self.l2 + self.l3 * math.cos(theta3))
            theta2 = alpha + beta

            # 5. Chuyển sang độ và áp dụng Offset cơ khí
            q1 = self.rad_to_deg(theta1)
            q2 = self.rad_to_deg(theta2) - 90.0
            q3 = self.rad_to_deg(theta3) + 90.0

            return round(q1, 2), round(q2, 2), round(q3, 2)

        except Exception as e:
            print(f"Lỗi IK: {e}")
            return None

    def forward_kinematics(self, q1, q2, q3):
        """Tính toán ngược lại từ góc ra tọa độ để kiểm tra"""
        # Giải mã ngược các Offset để quay về Radian gốc
        theta1 = math.radians(q1)
        theta2 = math.radians(q2 + 90.0)
        theta3 = math.radians(q3 - 90.0)

        # r_arm là hình chiếu ngang của toàn bộ cánh tay (l2 + l3)
        # l3 xoay một góc (theta2 + theta3) so với phương ngang
        r_arm = self.l2 * math.cos(theta2) + self.l3 * math.cos(theta2 + theta3)
        
        # Tọa độ XYZ thực tế tính cả l4
        x = (r_arm + self.l4) * math.cos(theta1)
        y = (r_arm + self.l4) * math.sin(theta1)
        z = self.l1 + self.l2 * math.sin(theta2) + self.l3 * math.sin(theta2 + theta3)

        return round(x, 2), round(y, 2), round(z, 2)