# Hệ thống giám sát và tự động hóa nông nghiệp qua Telegram 🌿🤖

Hệ thống IoT sử dụng ESP32 để giám sát nhiệt độ, độ ẩm không khí, độ ẩm đất và ánh sáng trong môi trường nông nghiệp. Hệ thống hỗ trợ điều khiển tưới cây thủ công hoặc tự động thông qua **Telegram bot**, đồng thời hiển thị dữ liệu lên màn hình OLED và lấy thông tin thời tiết qua API.

## 🔧 Công nghệ sử dụng

- Ngôn ngữ chính: Python (MicroPython)
- Vi điều khiển: ESP32
- Giao tiếp: Telegram Bot API
- Cảm biến: DHT11, LM393 (độ ẩm đất), LDR (ánh sáng)
- Màn hình hiển thị: OLED 0.96"
- Dịch vụ thời tiết: OpenWeatherMap API
- Phụ kiện khác: Relay, LED, buzzer, nút nhấn

## ⚙️ Tính năng chính

- Đo nhiệt độ, độ ẩm không khí, ánh sáng và độ ẩm đất theo thời gian thực  
- Hiển thị thông tin trên màn hình OLED  
- Gửi thông báo trạng thái hệ thống qua Telegram  
- Điều khiển bật/tắt bơm tự động khi đất khô  
- Nhận lệnh từ người dùng qua Telegram (/pumpon, /pumpoff, /status)  
- Cập nhật thời tiết hiện tại qua OpenWeatherMap API  
![image](https://github.com/user-attachments/assets/2820e249-2050-41e3-982d-ac5100a760fe)

