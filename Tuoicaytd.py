    import urequests
    import json
    import time
    import network
    from machine import Pin, I2C, ADC
    import ssd1306
    import dht

    # ----------------- CẤU HÌNH PHẦN CỨNG -----------------
    # OLED
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    # Cảm biến DHT11
    dht11 = dht.DHT11(Pin(4))

    # Cảm biến độ ẩm đất LM393
    soil_moisture = ADC(Pin(34))
    soil_moisture.atten(ADC.ATTN_11DB)
    dry_value = 3500
    wet_value = 800
    threshold = (dry_value + wet_value) // 2

    # Cảm biến ánh sáng
    light_sensor = ADC(Pin(35))
    light_sensor.atten(ADC.ATTN_11DB)

    # Relay (bơm)
    relay = Pin(25, Pin.OUT)
    relay.off()

    # LED báo hiệu
    led = Pin(15, Pin.OUT)
    led.off()

    # Buzzer
    buzzer = Pin(27, Pin.OUT)
    buzzer.off()

    # Nút nhấn
    button = Pin(32, Pin.IN, Pin.PULL_UP)

    # ----------------- CẤU HÌNH TELEGRAM -----------------
    BOT_TOKEN = '8113412114:AAEEBUSCe-Ak7RFgcemAxXsndXow00Uc6Dk'
    CHAT_ID = '-4789544636'

    # ----------------- HÀM GỬI TIN NHẮN TELEGRAM -----------------
    def send_telegram_message(message):
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        headers = {'Content-Type': 'application/json'}
        data = {'chat_id': CHAT_ID, 'text': message}
        try:
            response = urequests.post(url, json=data, headers=headers)
            response.close()
        except Exception as e:
            print(f"Error sending message: {e}")

    # ----------------- HÀM LẤY CẬP NHẬT LỆNH TELEGRAM -----------------
    def get_updates():
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
        try:
            response = urequests.get(url)
            updates = response.json()
            response.close()
            return updates.get('result', [])
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []

    # ----------------- HÀM XỬ LÝ LỆNH TELEGRAM -----------------
    last_update_id = None

    def process_telegram_commands():
        global last_update_id

        updates = get_updates()
        for update in updates:
            update_id = update.get('update_id')
            if last_update_id is None or update_id > last_update_id:
                last_update_id = update_id
                message = update.get('message', {})
                text = message.get('text', '').lower()

                print(f"Processing command: {text}")  
                if text == "/pumpon":
                    if relay.value() == 0:
                        relay.on()
                        led.on()
                        send_telegram_message("Pump is now ON.")
                        buzzer.on()
                        time.sleep(1)
                        buzzer.off()
                        oled.fill(0)
                        oled.text(f"Temp: {temperature}C", 0, 0)
                        oled.text(f"Humidity: {humidity}%", 0, 10)
                        oled.text(f"Soil: {soil_status}", 0, 20)
                        oled.text(f"Light: {light_status}", 0, 30)
                        oled.text(f"Pump: ON", 0, 40)
                        oled.text(f"Weather: {weather_emoji}", 0, 50)
                        oled.show()
                        time.sleep(10)
                    else:
                        send_telegram_message("Pump is already ON.")
                elif text == "/pumpoff":
                    if relay.value() == 0:
                        send_telegram_message("Pump is already OFF.")
                    else:
                        relay.off()
                        led.off()
                        buzzer.on()
                        time.sleep(1)
                        buzzer.off()
                        send_telegram_message("Pump is now OFF.")
                elif text == "/status":
                    dht11.measure()
                    temp = dht11.temperature()
                    hum = dht11.humidity()
                    soil_value = soil_moisture.read()
                    soil_status = "Dry" if soil_value > threshold else "Wet"
                    pump_status = "ON" if relay.value() else "OFF"
                    weather_emoji = get_weather_data()
                    light_status = 4095 - light_sensor.read()        # Xử lý ánh sáng theo mức độ
                    if 1000 <= light_status < 3000:
                        light_status = "Medium Light"
                    elif light_status >= 3000:
                        light_status = "High Light"
                    else:
                        light_status = "Low Light"

                    send_telegram_message(
                        f"Temp: {temp}°C\nHumidity: {hum}%\nSoil: {soil_status}\nLight: {light_status}\nPump: {pump_status}\nWeather: {weather_emoji}"
                    )

                else:
                    send_telegram_message("Command not recognized. Use /pumpon, /pumpoff, /status.")

    # ----------------- HÀM KẾT NỐI WIFI -----------------
    def connect_wifi():
        wifi_ssid = 'DANH CAO'
        wifi_password = '12345678d'
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(wifi_ssid, wifi_password)
            while not wlan.isconnected():
                pass
        print('Connected to WiFi')
        print('IP address:', wlan.ifconfig()[0])

    # ----------------- HÀM LẤY DỮ LIỆU WEATHER -----------------
    def get_weather_data():
        api_key = '2e5f3f13539774eb804ca74b1d1e5327'  
        city = 'Turan'  
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        
        try:
            response = urequests.get(url)
            data = response.json()
            response.close()
            weather_condition = data['weather'][0]['description']

            
            if "clear sky" in weather_condition:
                return "Sunny"  # Nắng
            elif "clouds" in weather_condition:
                return "Cloudy"  # Nắng có mây
            elif "rain" in weather_condition:
                return "Rain"  # Mưa
            elif "thunderstorm" in weather_condition:
                return "Thunderstorm"  # Mưa giông
            else:
                return "Cloudy"  # Mặc định là có mây

        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return "Cloudy"  # Mặc định nếu có lỗi

    # ----------------- HÀM CHÍNH -----------------
    def main():
        connect_wifi()
        send_telegram_message("ESP32 System Started!")
        weather_emoji = get_weather_data()

        while True:
            try:
                # Cập nhật dữ liệu từ cảm biến
                dht11.measure()
                temperature = dht11.temperature()
                humidity = dht11.humidity()
                adc_value_soil = soil_moisture.read()
                soil_status = "Dry" if adc_value_soil > threshold else "Wet"
                adc_value_light = light_sensor.read()
                light_status = 4095 - adc_value_light  
                if 1000 <= light_status < 3000:
                    light_status = "Medium Light"
                else:
                    light_status = "High Light" if light_status >= 3000 else "Low Light"

                # Hiển thị thông tin lên OLED
                oled.fill(0)
                oled.text(f"Temp: {temperature}C", 0, 0)
                oled.text(f"Humidity: {humidity}%", 0, 10)
                oled.text(f"Soil: {soil_status}", 0, 20)
                oled.text(f"Light: {light_status}", 0, 30)
                oled.text(f"Pump: {'ON' if relay.value() else 'OFF'}", 0, 40)
                oled.text(f"Weather: {weather_emoji}", 0, 50)
                oled.show()

                # Điều khiển bơm tự động
                if soil_status == "Dry" and relay.value() == 0:
                    relay.on()
                    led.on()
                    buzzer.on()
                    time.sleep(1)
                    buzzer.off()
                    send_telegram_message("Pump turned ON due to dry soil.")
                elif soil_status == "Wet" and relay.value() == 1:
                    relay.off()
                    led.off()
                    buzzer.on()
                    time.sleep(1)
                    buzzer.off()
                    send_telegram_message("Pump turned OFF due to wet soil.")

                # Kiểm tra nút nhấn
                if button.value() == 0:
                    if relay.value() == 1:
                        oled.fill(0)
                        oled.text("Warning:", 0, 0)
                        oled.text("Pump is ON", 0, 10)
                        oled.show()
                        time.sleep(2)
                    else:
                        relay.on()
                        led.on()
                        buzzer.on()
                        time.sleep(1)
                        buzzer.off()
                        send_telegram_message("Manual Pump ON triggered.")
                        time.sleep(10)
                        relay.off()
                        led.off()
                        buzzer.on()
                        time.sleep(1)
                        buzzer.off()
                        send_telegram_message("Manual Pump OFF triggered.")

                # Xử lý lệnh Telegram
                process_telegram_commands()
                time.sleep(2)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)

    # ----------------- CHẠY CHƯƠNG TRÌNH -----------------
    if __name__ == "__main__":
        main()


