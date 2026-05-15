import serial
import serial.tools.list_ports
import time

class CLIManager:
    def __init__(self):
        self.ser = None
        self.connected = False

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baud):
        try:
            self.ser = serial.Serial(port, int(baud), timeout=1)
            self.connected = True
            return True, f"✅ Đã kết nối {port} ({baud} baud)"
        except Exception as e:
            return False, f"❌ Lỗi: {e}"

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        return "⚠️ Đã ngắt kết nối"

    def send_raw(self, command):
        if self.connected and self.ser:
            if not command.endswith(";"): command += ";"
            self.ser.write((command + "\n").encode())
            return True, f"📤 Gửi: {command}"
        return False, "⚠️ Chưa kết nối thiết bị!"

    def get_version_info(self):
        if not self.connected: return ""
        self.ser.reset_input_buffer()
        self.ser.write(b"v;\n")
        time.sleep(0.2)
        lines = []
        while self.ser.in_waiting:
            line = self.ser.readline().decode(errors="ignore").strip()
            if line: lines.append(line)
        return "\n".join(lines)