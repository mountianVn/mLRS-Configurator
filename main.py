import customtkinter as ctk
import serial
import serial.tools.list_ports


class SerialTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.reading = False

        self.title("mLRS Configurator_Version 0.1")
        self.geometry("800x600")
        self.resizable(False, False)

        

        # Khởi tạo biến serial
        self.ser = None
        self.connected = False
        
        # Dòng đầu tiên: Baudrate - COM - CONNECT
        self.row1 = ctk.CTkFrame(self)
        self.row1.pack(pady=(15, 10))
        
        
        self.baud_label = ctk.CTkLabel(self.row1, text="Baud")
        self.baud_label.grid(row=0, column=0, padx=10)
        
        self.baud_menu = ctk.CTkComboBox(self.row1, values=["9600", "19200", "38400", "57600", "115200"], width=100)
        self.baud_menu.set("115200")
        self.baud_menu.grid(row=0, column=1, padx=10)

        self.com_label = ctk.CTkLabel(self.row1, text="COM")
        self.com_label.grid(row=0, column=2, padx=10)

        self.com_menu = ctk.CTkComboBox(self.row1, values=[], width=100)
        self.com_menu.grid(row=0, column=3, padx=10)

        self.connect_button = ctk.CTkButton(self.row1, text="CONNECT", command=self.toggle_connection, width=100,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.connect_button.grid(row=0, column=5, padx=10)

        self.refresh_button = ctk.CTkButton(self.row1, text="♻️↻", width=50, command=self.load_com_ports,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.refresh_button.grid(row=0, column=4, padx=5)

        self.clear_button = ctk.CTkButton(self.row1, text="🧹 Clear Log",width=50, command=self.clear_log,fg_color="#facc15",hover_color="#3b82f6",text_color="black")
        self.clear_button.grid(row=0, column=6, padx=(5, 0))

        self.clear_button = ctk.CTkButton(self.row1, text="🛠️ View",width=20,command=self.send_view_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.clear_button.grid(row=0, column=7, padx=(10, 0))

        # panel chính chia trái-phải
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Khung bên trái: các nút điều khiển
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        # Dòng thứ 2: POW
        self.row2 = ctk.CTkFrame(self.left_panel)
        self.row2.pack(pady=5,  anchor="w")

        self.pow_button = ctk.CTkButton(self.row2, text="🔋Power", command=self.send_pow_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.pow_button.grid(row=0, column=0, padx=(20, 10,))
        
        
        self.pow_menu = ctk.CTkComboBox(self.row2, values=["Level 0","Level 1", "Level 2", "Level 3", "Level 4","Level 5"], width=100)
        self.pow_menu.set("Level 0")
        self.pow_menu.grid(row=0, column=1, padx=10)
        
        # Dòng thứ 3: RF
        self.row3 = ctk.CTkFrame(self.left_panel)
        self.row3.pack(pady=5, anchor="w")
        
        self.style_button = ctk.CTkButton(self.row3, text="📡RF Band", command=self.send_rf_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.style_button.grid(row=0, column=0, padx=(20, 10,))

        self.style_menu = ctk.CTkComboBox(self.row3, values=["868mhz", "915mhz"], width=100)
        self.style_menu.set("868mhz")
        self.style_menu.grid(row=0, column=1, padx=10)
        # Dòng thứ 4: tín hiệu đầu vào 
        self.row4 = ctk.CTkFrame(self.left_panel)
        self.row4.pack(pady=5, anchor="w")

        self.rc_button = ctk.CTkButton(self.row4, text="🎮CH Source", command=self.send_rc_protocol,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rc_button.grid(row=0, column=0, padx=(20, 10,))

        self.rc_menu = ctk.CTkComboBox(self.row4, values=["None","Sbus","CRSF","mBridge"], width=100)
        self.rc_menu.set("CRSF")
        self.rc_menu.grid(row=0, column=1, padx=10)

        # dòng thứ 5:Bind Phrase 
        self.row5 = ctk.CTkFrame(self.left_panel)
        self.row5.pack(pady=5, anchor="w")

        
        self.bind_button = ctk.CTkButton(self.row5,text="🔑Bind Phrase",command=self.send_bind_phrase,fg_color="#facc15",hover_color="#B0C0D3",text_color="black")
        self.bind_button.grid(row=0, column=0, padx=(20, 10,))


        self.bind_entry = ctk.CTkEntry(self.row5, width=100)
        self.bind_entry.grid(row=0, column=1, padx=10)


        # dòng thứ 6:Mode 
        
        self.row6 = ctk.CTkFrame(self.left_panel)
        self.row6.pack(pady=5, anchor="w")

        self.mode_button = ctk.CTkButton(self.row6, text="⚙️ Mode ", command=self.send_mode_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.mode_button.grid(row=0, column=0, padx=(20, 10,))

        self.mode_menu = ctk.CTkComboBox(self.row6, values=["50hz", "31hz", "19hz", "FLRC", "FSK"], width=100)
        self.mode_menu.set("31hz")
        self.mode_menu.grid(row=0, column=1, padx=10)

        # dòng thứ 7:order 
        
        self.row7 = ctk.CTkFrame(self.left_panel)
        self.row7.pack(pady=5, anchor="w")

        self.order_button = ctk.CTkButton(self.row7, text=" 📶Order ", command=self.send_order_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.order_button.grid(row=0, column=0, padx=(20, 10,))

        self.order_menu = ctk.CTkComboBox(self.row7, values=["AETR", "TAER", "ETAR"], width=100)
        self.order_menu.set("AETR")
        self.order_menu.grid(row=0, column=1, padx=10)


        # dòng thứ 8:dest đích đến 
        
        self.row8 = ctk.CTkFrame(self.left_panel)
        self.row8.pack(pady=5, anchor="w")

        self.dest_button = ctk.CTkButton(self.row8, text=" 🎯Dest ", command=self.send_dest_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.dest_button.grid(row=0, column=0, padx=(20, 10,))

        self.dest_menu = ctk.CTkComboBox(self.row8, values=["Serial", "mBridge"], width=100)
        self.dest_menu.set("Serial")
        self.dest_menu.grid(row=0, column=1, padx=10)






       #nút lưu
        self.save_button = ctk.CTkButton(self, text="SAVE", command=self.send_save_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.save_button.pack(pady=15)   # Đặt cuối với khoảng cách
        
      # Text log bên phải
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="left", fill="both", expand=True)
        self.log = ctk.CTkTextbox(self.right_panel, height=80)
        self.log.pack(fill="both", expand=True)

        # Tải danh sách cổng COM
        self.load_com_ports()

    def load_com_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.com_menu.configure(values=port_list)
        if port_list:
            self.com_menu.set(port_list[0])
        else:
            self.com_menu.set("")

    def toggle_connection(self):
        if not self.connected:
            try:
                port = self.com_menu.get()
                baud = int(self.baud_menu.get())
                self.ser = serial.Serial(port, baud, timeout=1)
                self.connected = True
                self.reading = True
                self.connect_button.configure(text="DISCONNECT")
                self.write_log(f"✅ Đã kết nối {port} ({baud} baud)")
                self.after(100, self.read_serial_loop)  # bắt đầu đọc dữ liệu
            except Exception as e:
                self.write_log(f"❌ Lỗi: {e}")
        else:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.connected = False
            self.reading = False
            self.connect_button.configure(text="CONNECT")
            self.write_log("⚠️ Đã ngắt kết nối")
     
     #Nút kết nối       
    def handle_disconnection(self):
        if self.ser and self.ser.is_open:
            try:  
                self.ser.close()
            except:
                pass
        self.ser = None
        self.connected = False
        self.reading = False
        self.connect_button.configure(text="CONNECT")
        self.write_log("⚠️ Kết nối đã bị mất. Đã ngắt kết nối.")
        self.load_com_ports()   

    def clear_log(self):
        self.log.delete("1.0", "end")               



    def send_pow_command(self):
        if self.ser and self.ser.is_open:
            pow_val = self.pow_menu.get()
            
            pow_command_map = {
                "Level 0": "tx_power=0",
                "Level 1": "tx_power=1",
                "Level 2": "tx_power=2",
                "Level 3": "tx_power=3",
                "Level 4": "tx_power=4",
                "Level 5": "tx_power=5"
                
            }
            if pow_val in pow_command_map:
                command = f"p {pow_command_map[pow_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định công suất: {pow_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")

    #đây là cài đặt tần số 
    def send_rf_command(self):
        if self.ser and self.ser.is_open:
            rf_val = self.style_menu.get()
            # Ánh xạ lựa chọn -> lệnh

            rf_command_map = {
            "868mhz": "p rf_band = 2",
            "915mhz": "p rf_band = 1"
            }
            if rf_val in rf_command_map:
                command = f"{rf_command_map[rf_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định kiểu truyền: {rf_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
    
    
    #đây là cài đặt mode ví dụ 50hz 
    def send_mode_command(self):
        if self.ser and self.ser.is_open:
            mode_val = self.mode_menu.get()
            # Ánh xạ lựa chọn -> lệnh

            mode_command_map = {
            "50hz": "p mode = 0",
            "31hz": "p mode = 1",
            "19hz": "p mode = 2",
            "FLRC":"p mode = 3",
            "FSK":  "p mode = 4"

            }
            if mode_val in mode_command_map:
                command = f"{mode_command_map[mode_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định kiểu tốc độ: {mode_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")

     #đây là cài đặt order ví dụ aetr 
    def send_order_command(self):
        if self.ser and self.ser.is_open:
            order_val = self.order_menu.get()
            # Ánh xạ lựa chọn -> lệnh

            order_command_map = {
            "AETR": "p tx_ch_order = 0",
            "TAER": "p tx_ch_order = 1",
            "ETAR": "p tx_ch_order = 2"
            

            }
            if order_val in order_command_map:
                command = f"{order_command_map[order_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định kiểu order: {order_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")       

    #đây là view module 
    def send_view_command(self):
        if self.ser and self.ser.is_open:
            command = "pl;\n"
            self.ser.write(command.encode())
            self.write_log(f"📤 Gửi: {command.strip()}")

        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")            
    #đây là CH source
    def send_rc_protocol(self):
        if self.ser and self.ser.is_open:
            protocol_val = self.rc_menu.get()

            protocol_map = {
             "None": "p tx_ch_source = 0",
             "Sbus": "p tx_ch_source = 2",
             "CRSF": "p tx_ch_source = 1",
             "mBridge": "p tx_ch_source = 3"
        }

            if protocol_val in protocol_map:
               command = f"{protocol_map[protocol_val]};\n"
               self.ser.write(command.encode())
               self.write_log(f"📤 Gửi: {command.strip()}")
            else:
               self.write_log(f"⚠️ Không xác định RC Protocol: {protocol_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
    #đây là dest
    
    def send_dest_command(self):
        if self.ser and self.ser.is_open:
            dest_val = self.dest_menu.get()
            # Ánh xạ lựa chọn -> lệnh

            dest_command_map = {
            "Serial": "p tx_ser_dest = 0",
            "mBridge": "p tx_ser_dest = 2"
            }
            if dest_val in dest_command_map:
                command = f"{dest_command_map[dest_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định kiểu đích đến: {dest_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")




    #đây là của bind     
    def send_bind_phrase(self):
        if self.ser and self.ser.is_open:
            phrase = self.bind_entry.get().strip()
            if phrase:
                command = f"p bind_phrase = {phrase};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log("⚠️ Vui lòng nhập nội dung bind_phrase!")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")  
     #đây là save 
    def send_save_command(self):
        if self.ser and self.ser.is_open:
            command = "pstore;\n"
            self.ser.write(command.encode())
            self.write_log(f"📤 Gửi: {command.strip()}")

        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")        


         
    def read_serial_loop(self):
        if self.connected and self.ser and self.ser.is_open and self.reading:
            try:
                if not self.ser.is_open:
                    raise serial.SerialException("Mất kết nối với thiết bị.")
                
                if self.ser.in_waiting:
                    data = self.ser.readline().decode(errors='ignore').strip()
                    if data:
                        self.write_log(f"📥 Nhận: {data}")
            except (serial.SerialException, OSError) as e:
                self.write_log(f"❌ Thiết bị đã ngắt kết nối: {e}")
                self.handle_disconnection()
                           
            except Exception as e:
                self.write_log(f"❌ Lỗi đọc: {e}")
                self.reading = False
                return 
            self.after(10, self.read_serial_loop)  # tiếp tục vòng lặp       
    

    def write_log(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # "dark" hoặc "system"
    ctk.set_default_color_theme("green")  # hoặc "green", "dark-blue"
    app = SerialTool()
    app.mainloop()
