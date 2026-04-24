# 🤖 PLC Defect Detection System

**Robot Vision & PLC Integration System**

Hệ thống điều khiển robot gắp sản phẩm tự động, tích hợp nhận diện hình ảnh (AI) và điều phối công nghiệp thông qua PLC Siemens S7-1200.

---

## 🌟 Key Features

### 🔍 AI Vision

* Sử dụng **YOLOv8** để nhận diện:

  * Sản phẩm đạt chuẩn (`DatChuan`)
  * Lỗi Logo
  * Lỗi Chữ
  * Ngược Mặt

### 🎯 Smart Filtering

* Motion Detection: Loại bỏ nhiễu khi vật đang di chuyển
* Stability Filter: Đảm bảo chỉ xử lý khi vật đã ổn định

### 🔄 Session Management

* Cơ chế quản lý phiên giữa Python và PLC
* Đảm bảo mỗi sản phẩm chỉ được xử lý **một lần duy nhất**
* Tránh gửi lệnh trùng lặp

### ⚡ PLC Coordination

* Giao tiếp realtime qua **Snap7 (PUT/GET)**
* Đồng bộ giữa:

  * Cảm biến
  * Băng tải
  * Robot

### 🦾 Kinematics Control

* Tính toán **Inverse Kinematics (IK)** cho robot 3 bậc tự do (3-DOF)
* Gửi lệnh điều khiển qua **ESP32 / Arduino**

---

## 🏗️ System Architecture

Hệ thống gồm 3 lớp chính:

### 1. AI Layer (Python)

* Xử lý hình ảnh
* Phân loại sản phẩm
* Quyết định kết quả cuối cùng

### 2. Control Layer (PLC)

* Điều khiển cảm biến
* Quản lý băng tải
* Gửi lệnh gắp

### 3. Execution Layer (Robot)

* Nhận tọa độ góc
* Thực hiện gắp & thả

---

## 📂 Project Structure

```bash
├── main.py              # Entry point - Điều phối toàn bộ hệ thống
├── gui_camera.py        # Giao diện camera & kết nối
├── gui_robot.py         # Giao diện điều khiển robot
├── plc_handler.py       # Giao tiếp Snap7 với PLC S7-1200
├── robot_controller.py  # Điều khiển robot & giao tiếp Serial
├── kinematic.py         # Tính toán động học nghịch (IK)
└── best.pt              # Model YOLOv8 đã train
```

---

## ⚙️ Operational Flow

Quy trình hoạt động theo cơ chế **"Chốt phiên"**:

1. **Sensor ON (I_M7)**
   → Sản phẩm dừng tại vị trí camera

2. **AI xử lý & chốt kết quả**
   → Lấy kết quả trung bình từ tracker
   → Nếu đạt → gửi tín hiệu `I_M3` về PLC

3. **PLC gửi lệnh gắp (I_M6 ON)**
   → Robot bắt đầu thực hiện

4. **Robot hoàn tất**
   → Python gửi `I_M4`
   → PLC tiếp tục băng tải hoặc đóng gói

---

## 🛠️ Setup & Configuration

### 1. Requirements

* Python >= 3.9
* TIA Portal (cấu hình PLC S7-1200)

---

### 2. PLC Configuration (Quan trọng)

Để Python có thể truy cập DB:

* ❌ Bỏ chọn: `Optimized block access`
* ✅ Bật: `Permit access with PUT/GET communication`

---

### 3. Install Dependencies

```bash
pip install python-snap7 ultralytics pyserial PyQt6 numpy opencv-python
```

---

## 🖥️ User Interface

Giao diện xây dựng bằng **PyQt6**, bao gồm:

* 📷 Camera View
  → Hiển thị bounding box realtime

* 🔌 Connection Status
  → Theo dõi PLC IP & COM Port

* 🚦 LED Indicators
  → Báo trạng thái:

  * Sản phẩm đạt / lỗi
  * Trạng thái robot

---

## 📌 Notes

* Đảm bảo PLC và máy tính cùng mạng
* Kiểm tra đúng địa chỉ DB và offset khi đọc/ghi dữ liệu
* Hiệu chỉnh camera và robot để đạt độ chính xác cao

---

## 🚀 Future Improvements

* Thêm dashboard web giám sát từ xa
* Logging & thống kê sản xuất
* Tích hợp nhiều loại sản phẩm
* Nâng cấp mô hình AI (multi-class / segmentation)

---
