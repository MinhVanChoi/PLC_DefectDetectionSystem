# PLC_DefectDetectionSystem

🤖 Robot Vision & PLC Integration System
Hệ thống điều khiển Robot gắp sản phẩm tự động tích hợp nhận diện hình ảnh (AI) và điều phối công nghiệp qua PLC Siemens S7-1200.

🌟 Tính năng nổi bật (Key Features)
AI Vision: Sử dụng YOLOv8 để nhận diện sản phẩm đạt chuẩn (DatChuan) và các lỗi phổ biến (Lỗi Logo, Lỗi Chữ, Ngược Mặt).

Smart Filtering: Tích hợp bộ lọc chuyển động (Motion Detection) và bộ lọc ổn định (Stability Filter) giúp loại bỏ nhiễu khi vật đang trôi trên băng tải.

Session Management: Cơ chế quản lý phiên làm việc chặt chẽ giữa Python và PLC, đảm bảo mỗi sản phẩm chỉ được xử lý một lần, tránh lặp lệnh.

PLC Coordination: Giao tiếp thời gian thực qua giao thức Snap7 (PUT/GET), điều phối nhịp nhàng giữa cảm biến vật cản và Robot.

Kinematics Control: Tính toán động học nghịch (Inverse Kinematics) trực tiếp để điều khiển Robot 3 chân (3-DOF) qua ESP32/Arduino.

🏗️ Kiến trúc hệ thống (System Architecture)
Hệ thống hoạt động dựa trên sự phối hợp của 3 thành phần chính:

AI Layer (Python): Xử lý hình ảnh, phân loại và chốt kết quả.

Control Layer (PLC): Quản lý cảm biến dừng vật, điều khiển băng tải và cấp lệnh gắp.

Execution Layer (Robot): Nhận tọa độ góc từ AI Layer và thực hiện quỹ đạo gắp-thả.

📂 Cấu trúc dự án (Project Structure)
Bash
├── main.py              # Entry point - Điều phối toàn bộ logic hệ thống
├── gui_camera.py        # Giao diện giám sát Camera & Kết nối
├── gui_robot.py         # Giao diện điều khiển động học Robot
├── plc_handler.py       # Class xử lý giao tiếp Snap7 với Siemens S7-1200
├── robot_controller.py  # Điều khiển quỹ đạo và Serial gửi lệnh ESP32
├── kinematic.py         # Thư viện tính toán động học nghịch (IK)
└── best.pt              # Model YOLOv8 đã được train
⚙️ Quy trình vận hành (Operational Flow)
Hệ thống tuân thủ nghiêm ngặt quy trình "Chốt phiên" để đảm bảo độ chính xác:

Cảm biến (I_M7) ON: Sản phẩm dừng đúng vị trí camera.

AI Chốt đơn: Python lấy kết quả trung bình từ Tracker, nếu đạt chuẩn gửi I_M3 về PLC.

Lệnh gắp (I_M6) ON: PLC gửi lệnh chạy Robot.

Robot hoàn tất: Sau khi gắp xong, Python gửi I_M4 báo PLC chạy tiếp băng tải hoặc đóng hộp.

🛠️ Cài đặt & Cấu hình (Setup)
1. Yêu cầu phần mềm
Python 3.9+

TIA Portal (Cấu hình PLC S7-1200)

2. Cấu hình PLC (Quan trọng)
Để Python có thể đọc/ghi vào DB1, bạn cần:

Bỏ chọn "Optimized block access" trong thuộc tính Data Block.

Tích chọn "Permit access with PUT/GET communication" trong phần Protection của PLC.

3. Cài đặt thư viện Python
Bash
pip install python-snap7 ultralytics pyserial PyQt6 numpy opencv-python
🖥️ Giao diện người dùng (User Interface)
Giao diện được thiết kế hiện đại trên nền PyQt6 với các thành phần:

Khung hiển thị Camera: Vẽ bounding box realtime.

Bảng trạng thái kết nối: Giám sát COM Port và PLC IP.

Hệ thống LED: Báo hiệu SP Đạt/Lỗi và trạng thái Robot theo thời gian thực.
