import re

class MavlinkManager:
    def __init__(self):
        self.telemetry = {
            "mode": "N/A",
            "voltage": "0.0V",
            "satellites": "0",
            "rssi": "0"
        }

    def parse_data(self, raw_line):
        line = raw_line.strip()
        found = False
        
        # Lọc điện áp (Ví dụ: "Batt: 12.6V" hoặc "V: 12.6")
        if "V" in line or "Batt" in line:
            match = re.search(r"(\d+\.\d+|\d+)V?", line)
            if match:
                self.telemetry["voltage"] = f"{match.group(1)}V"
                found = True
        
        # Lọc chế độ bay
        if "Mode:" in line:
            self.telemetry["mode"] = line.split("Mode:")[1].strip()
            found = True

        # Lọc số vệ tinh
        if "Sats:" in line:
            match = re.search(r"Sats:\s*(\d+)", line)
            if match:
                self.telemetry["satellites"] = match.group(1)
                found = True

        return found, self.telemetry