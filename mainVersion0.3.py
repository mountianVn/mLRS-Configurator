import customtkinter as ctk
import serial
import serial.tools.list_ports
import tkinter.messagebox as mbox
import time
import os
import sys
import platform
def resource_path(relative_path):
    #Trả về đường dẫn thực tế khi chạy file exe hoặc file py"""
        try:
            base_path = sys._MEIPASS  # PyInstaller sẽ tạo thư mục tạm khi chạy
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path) 
if platform.system() == "Windows":
    import winsound
class SerialTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.default_font = ("Arial", 14)
        self.reading = False
        self.iconbitmap(resource_path("mlrs.ico"))
        self.title("mLRS Configurator_Version 0.3")
        self.geometry("850x660")
        self.resizable(False, False)  
        # Khởi tạo biến serial
        self.ser = None
        self.connected = False
        
        # Dòng đầu tiên: Baudrate - COM - CONNECT
        self.row1 = ctk.CTkFrame(self)
        self.row1.pack(pady=(15, 10))
                
        self.baud_label = ctk.CTkLabel(self.row1,font=self.default_font, text="Baud")
        self.baud_label.grid(row=0, column=0, padx=10)
        
        self.baud_menu = ctk.CTkComboBox(self.row1, values=["9600", "19200", "38400", "57600", "115200"], width=100)
        self.baud_menu.set("115200")
        self.baud_menu.grid(row=0, column=1, padx=10)

        self.com_label = ctk.CTkLabel(self.row1,font=self.default_font, text="Com")
        self.com_label.grid(row=0, column=2, padx=10)

        self.com_menu = ctk.CTkComboBox(self.row1, values=[], width=100)
        self.com_menu.grid(row=0, column=3, padx=10)

        self.connect_button = ctk.CTkButton(self.row1,font=self.default_font, text="🔌Connect", command=self.toggle_connection, width=100,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.connect_button.grid(row=0, column=5, padx=10)

        self.refresh_button = ctk.CTkButton(self.row1, text="Refresh",font=self.default_font, width=20, command=self.load_com_ports,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.refresh_button.grid(row=0, column=4, padx=(10,5))

        self.clear_button = ctk.CTkButton(self.row1, text="🧹Clear Log",width=20,font=self.default_font, command=self.clear_log,fg_color="#facc15",hover_color="#3b82f6",text_color="black")
        self.clear_button.grid(row=0, column=6, padx=(10,5))

        self.view_button = ctk.CTkButton(self.row1, text="🖊View",width=20,font=self.default_font,command=self.send_view_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.view_button.grid(row=0, column=7, padx=(10,5))

        # panel chính chia trái-phải
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Khung bên trái: các nút điều khiển
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.mode_switch = ctk.CTkSegmentedButton(self.left_panel, values=["💻TX CONFIG", "✈RX CONFIG"], command=self.switch_mode)
        self.mode_switch.pack(pady=(5, 10), padx=10)
        self.mode_switch.set("💻TX CONFIG")  # Mặc định

        # Dòng thứ 2: POW
        self.tx_controls = ctk.CTkFrame(self.left_panel)
        self.tx_controls.pack()

        self.row2 = ctk.CTkFrame(self.tx_controls)
        self.row2.pack(pady=5,  anchor="w")
        self.pow_button = ctk.CTkButton(self.row2, text="⚙️ Power", command=self.send_pow_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.pow_button.grid(row=0, column=0, padx=(20, 10,))
        
        
        self.pow_menu = ctk.CTkComboBox(self.row2, values=["Level 0","Level 1", "Level 2", "Level 3", "Level 4","Level 5"], width=100,font=self.default_font)
        self.pow_menu.set("Level 0")
        self.pow_menu.grid(row=0, column=1, padx=10)
        
        # Dòng thứ 3: RF
        self.row3 = ctk.CTkFrame(self.tx_controls)
        self.row3.pack(pady=5, anchor="w")
        
        self.rf_button = ctk.CTkButton(self.row3, text="📡RF Band", command=self.send_rf_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.rf_button.grid(row=0, column=0, padx=(20, 10,))

        self.rf_menu = ctk.CTkComboBox(self.row3, values=["868mhz", "915mhz"], width=100,font=self.default_font)
        self.rf_menu.set("868mhz")
        self.rf_menu.grid(row=0, column=1, padx=10)
        # Dòng thứ 4: tín hiệu đầu vào 
        self.row4 = ctk.CTkFrame(self.tx_controls)
        self.row4.pack(pady=5, anchor="w")

        self.rc_button = ctk.CTkButton(self.row4, text="⚙️CH Source", command=self.send_rc_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.rc_button.grid(row=0, column=0, padx=(20, 10,))

        self.rc_menu = ctk.CTkComboBox(self.row4, values=["None","Sbus","CRSF","mBridge"], width=100,font=self.default_font)
        self.rc_menu.set("CRSF")
        self.rc_menu.grid(row=0, column=1, padx=10)

        # dòng thứ 5:Bind Phrase 
        self.row5 = ctk.CTkFrame(self.tx_controls)
        self.row5.pack(pady=5, anchor="w")    
        self.bind_button = ctk.CTkButton(self.row5,text="🔑Bind Phrase",command=self.send_bind_phrase,fg_color="#facc15",hover_color="#B0C0D3",text_color="black",font=self.default_font)
        self.bind_button.grid(row=0, column=0, padx=(20, 10,))
        self.bind_entry = ctk.CTkEntry(self.row5, width=100,font=self.default_font,placeholder_text="Nhập Phrase")
        self.bind_entry.grid(row=0, column=1, padx=10)


        # dòng thứ 6:Mode 
        
        self.row6 = ctk.CTkFrame(self.tx_controls)
        self.row6.pack(pady=5, anchor="w")
        self.mode_button = ctk.CTkButton(self.row6, text="⚙️ Mode ", command=self.send_mode_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.mode_button.grid(row=0, column=0, padx=(20, 10,))
        self.mode_menu = ctk.CTkComboBox(self.row6, values=["50hz", "31hz", "19hz", "FLRC", "FSK"], width=100,font=self.default_font)
        self.mode_menu.set("31hz")
        self.mode_menu.grid(row=0, column=1, padx=10)

        # dòng thứ 7:ch order 
        
        self.row7 = ctk.CTkFrame(self.tx_controls)
        self.row7.pack(pady=5, anchor="w")
        self.order_button = ctk.CTkButton(self.row7, text="🎮Ch Order ", command=self.send_order_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.order_button.grid(row=0, column=0, padx=(20, 10,))
        self.order_menu = ctk.CTkComboBox(self.row7, values=["AETR", "TAER", "ETAR"], width=100,font=self.default_font)
        self.order_menu.set("AETR")
        self.order_menu.grid(row=0, column=1, padx=10)


        # dòng thứ 8:dest đích đến 
        
        self.row8 = ctk.CTkFrame(self.tx_controls)
        self.row8.pack(pady=5, anchor="w")
        self.dest_button = ctk.CTkButton(self.row8, text="⚙️Ser Dest", command=self.send_dest_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.dest_button.grid(row=0, column=0, padx=(20, 10,))
        self.dest_menu = ctk.CTkComboBox(self.row8, values=["Serial", "mBridge"], width=100,font=self.default_font)
        self.dest_menu.set("Serial")
        self.dest_menu.grid(row=0, column=1, padx=10)

        

        # dòng thứthứ9:RF RF_ORTHO đích đến 
        self.row9 = ctk.CTkFrame(self.tx_controls)
        self.row9.pack(pady=5, anchor="w")
        self.ortho_button = ctk.CTkButton(self.row9, text="⚙️RF Ortho", command=self.send_ortho_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.ortho_button.grid(row=0, column=0, padx=(20, 10,))
        self.ortho_menu = ctk.CTkComboBox(self.row9, values=["OFF", "1/3", "2/3", "3/3"], width=100,font=self.default_font)
        self.ortho_menu.set("OFF")
        self.ortho_menu.grid(row=0, column=1, padx=10)

         # dòng thứthứ 10 :Tx Power Sw Ch
        self.row10 = ctk.CTkFrame(self.tx_controls)
        self.row10.pack(pady=5, anchor="w")
        self.power_CH_button = ctk.CTkButton(self.row10, text="⚙️Tx Power CH", command=self.send_power_CH_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.power_CH_button.grid(row=0, column=0, padx=(20, 10,))
        self.power_CH_menu = ctk.CTkComboBox(self.row10, values=[  "OFF","CH12","CH13", "CH14", "CH15"], width=100,font=self.default_font)
        self.power_CH_menu.set("OFF")
        self.power_CH_menu.grid(row=0, column=1, padx=10)
         # dòng thứthứ 11 :Tx baudrate
        self.row11 = ctk.CTkFrame(self.tx_controls)
        self.row11.pack(pady=5, anchor="w")
        self.baudrate_button = ctk.CTkButton(self.row11, text="⚙️Tx Baudrate", command=self.send_baudrate_command,font=self.default_font,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.baudrate_button.grid(row=0, column=0, padx=(20, 10,))
        self.baudrate_menu = ctk.CTkComboBox(self.row11, values=[  "9600","19200","38400", "57600", "115200","230400"], width=100,font=self.default_font)
        self.baudrate_menu.set("115200")
        self.baudrate_menu.grid(row=0, column=1, padx=10)
          # dòng thứ 12 :RADIOSTAT
        self.row12 = ctk.CTkFrame(self.tx_controls)
        self.row12.pack(pady=5, anchor="w")
        self.radiostat_button = ctk.CTkButton(self.row12, text="⚙️Snd RadioStat",font=self.default_font, command=self.send_radiostat_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.radiostat_button.grid(row=0, column=0, padx=(20, 10,))
        self.radiostat_menu = ctk.CTkComboBox(self.row12,font=self.default_font, values=[  "OFF","1Hz"], width=100)
        self.radiostat_menu.set("1Hz")
        self.radiostat_menu.grid(row=0, column=1, padx=10)

         # dòng thứ 13 :Mav Component
        self.row13 = ctk.CTkFrame(self.tx_controls)
        self.row13.pack(pady=5, anchor="w")
        self.COMPONENT_button = ctk.CTkButton(self.row13, text="🕹Mav Component",font=self.default_font, command=self.send_COMPONENT_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.COMPONENT_button.grid(row=0, column=0, padx=(20, 10,))
        self.COMPONENT_menu = ctk.CTkComboBox(self.row13,font=self.default_font, values=[  "OFF","ENABLED"], width=100)
        self.COMPONENT_menu.set("OFF")
        self.COMPONENT_menu.grid(row=0, column=1, padx=10)

        

# Tạo nút bên tap RX_config 
              
        self.rx_controls = ctk.CTkFrame(self.left_panel)
        #self.rx_controls.pack()
# Dòng thứ 2: rx_POWer
        self.rx_row2 = ctk.CTkFrame(self.rx_controls)
        self.rx_row2.pack(pady=5,  anchor="w")
        self.rxpow_button = ctk.CTkButton(self.rx_row2, text="⚙️RX_Power",font=self.default_font, command=self.send_rxpow_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxpow_button.grid(row=0, column=0, padx=(20, 10,))
        self.rxpow_menu = ctk.CTkComboBox(self.rx_row2,font=self.default_font, values=["Level 0","Level 1", "Level 2", "Level 3", "Level 4","Level 5"], width=100)
        self.rxpow_menu.set("Level 0")
        self.rxpow_menu.grid(row=0, column=1, padx=10)

# Dòng thứ 3: rx_mode
        self.rx_row3 = ctk.CTkFrame(self.rx_controls)
        self.rx_row3.pack(pady=5, anchor="w")
        self.rxmode_button = ctk.CTkButton(self.rx_row3,font=self.default_font, text="⚙️Out Mode", command=self.send_rxmode_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxmode_button.grid(row=0, column=0, padx=(20, 10))
        self.rxmode_menu = ctk.CTkComboBox(self.rx_row3,font=self.default_font, values=["Sbus", "CRSF", "Sbus INV"], width=100)
        self.rxmode_menu.set("CRSF")
        self.rxmode_menu.grid(row=0, column=1, padx=10)

# Dòng thứ 4:Rx Ser Baudrate
        self.rx_row4 = ctk.CTkFrame(self.rx_controls)
        self.rx_row4.pack(pady=5, anchor="w")
        self.Baudrate_button = ctk.CTkButton(self.rx_row4,font=self.default_font, text="⚙️Ser Baudrate", command=self.send_Baudrate_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.Baudrate_button.grid(row=0, column=0, padx=(20, 10))
        self.Baudrate_menu = ctk.CTkComboBox(self.rx_row4,font=self.default_font, values=["9600","19200","38400", "57600", "115200","230400"], width=100)
        self.Baudrate_menu.set("57600")
        self.Baudrate_menu.grid(row=0, column=1, padx=10)
# Dòng thứ 5:Rx MAVLINK Mode
        self.rx_row5 = ctk.CTkFrame(self.rx_controls)
        self.rx_row5.pack(pady=5, anchor="w")
        self.RXMAVLINK_button = ctk.CTkButton(self.rx_row5,font=self.default_font, text="⚙️Ser Link Mode", command=self.send_RXMAVLINK_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.RXMAVLINK_button.grid(row=0, column=0, padx=(20, 10))
        self.RXMAVLINK_menu = ctk.CTkComboBox(self.rx_row5,font=self.default_font, values=["Transp","MAVLINK", "MAVLINKX", "MSPX"], width=100)
        self.RXMAVLINK_menu.set("MAVLINK")
        self.RXMAVLINK_menu.grid(row=0, column=1, padx=10)
# Dòng thứ 6:Rx Snd RadioStat
        self.rx_row6 = ctk.CTkFrame(self.rx_controls)
        self.rx_row6.pack(pady=5, anchor="w")
        self.RadioStat_button = ctk.CTkButton(self.rx_row6,font=self.default_font, text="⚙️Snd RadioStat", command=self.send_RadioStat_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.RadioStat_button.grid(row=0, column=0, padx=(20, 10))
        self.RadioStat_menu = ctk.CTkComboBox(self.rx_row6,font=self.default_font, values=["Off", "Ardu_1", "meth_b"], width=100)
        self.RadioStat_menu.set("Ardu_1")
        self.RadioStat_menu.grid(row=0, column=1, padx=10) 
# Dòng thứ 7  :Rx Ser Port
        self.rx_row7 = ctk.CTkFrame(self.rx_controls)
        self.rx_row7.pack(pady=5, anchor="w")
        self.rxPort_button = ctk.CTkButton(self.rx_row7,font=self.default_font, text="⚙️Ser Port", command=self.send_rxPort_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxPort_button.grid(row=0, column=0, padx=(20, 10))
        self.rxPort_menu = ctk.CTkComboBox(self.rx_row7,font=self.default_font, values=["Serial", "Can"], width=100)
        self.rxPort_menu.set("Serial")
        self.rxPort_menu.grid(row=0, column=1, padx=10)               
# Dòng thứ 8  :RX_SND_RCCHANNEL
        self.rx_row8 = ctk.CTkFrame(self.rx_controls)
        self.rx_row8.pack(pady=5, anchor="w")
        self.SND_RCCHANNEL_button = ctk.CTkButton(self.rx_row8,font=self.default_font, text="⚙️Snd RcChannel", command=self.send_SND_RCCHANNEL_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.SND_RCCHANNEL_button.grid(row=0, column=0, padx=(20, 10))
        self.SND_RCCHANNEL_menu = ctk.CTkComboBox(self.rx_row8,font=self.default_font, values=["Off", "rc Override","rc Channels"], width=100)
        self.SND_RCCHANNEL_menu.set("rc Override")
        self.SND_RCCHANNEL_menu.grid(row=0, column=1, padx=10)  
# Dòng thứ 9   :RX_OUT_RSSI_CH
        self.rx_row9 = ctk.CTkFrame(self.rx_controls)
        self.rx_row9.pack(pady=5, anchor="w")
        self.RSSI_CH_button = ctk.CTkButton(self.rx_row9,font=self.default_font, text="📡OUT RSSI CH", command=self.send_RSSI_CH_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.RSSI_CH_button.grid(row=0, column=0, padx=(20, 10))
        self.RSSI_CH_menu = ctk.CTkComboBox(self.rx_row9,font=self.default_font, values=["Off", "CH 14","CH 15","CH 16"], width=100)
        self.RSSI_CH_menu.set("Off")
        self.RSSI_CH_menu.grid(row=0, column=1, padx=10) 

# Dòng thứ 10  :RX_OUT_LQ_CH
        self.rx_row10 = ctk.CTkFrame(self.rx_controls)
        self.rx_row10.pack(pady=5, anchor="w")
        self.LQ_CH_button = ctk.CTkButton(self.rx_row10,font=self.default_font, text="📶OUT LQ CH", command=self.send_LQ_CH_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.LQ_CH_button.grid(row=0, column=0, padx=(20, 10))
        self.LQ_CH_menu = ctk.CTkComboBox(self.rx_row10,font=self.default_font, values=["Off", "CH 14","CH 15","CH 16"], width=100)
        self.LQ_CH_menu.set("Off")
        self.LQ_CH_menu.grid(row=0, column=1, padx=10)

# Dòng thứ 10  :rx Power Sw Ch
        self.rx_row11 = ctk.CTkFrame(self.rx_controls)
        self.rx_row11.pack(pady=5, anchor="w")
        self.RXpower_CH_button = ctk.CTkButton(self.rx_row11, text="🎮Power Sw Ch", command=self.send_RXpower_CH_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.RXpower_CH_button.grid(row=0, column=0, padx=(20, 10,))
        self.RXpower_CH_menu = ctk.CTkComboBox(self.rx_row11, values=[  "Off","CH12","CH13", "CH14", "CH15"], width=100,font=self.default_font)
        self.RXpower_CH_menu.set("Off")
        self.RXpower_CH_menu.grid(row=0, column=1, padx=10)        
        
    #thông tin phiên bản
        self.info_box = ctk.CTkTextbox(self, height=80, width=300,font=self.default_font, state="disabled")#self.info_box = ctk.CTkTextbox(self, height=40, width=290)
        self.info_box.pack(side="left", fill="y", padx=(20, 10))#pack(pady=(0, 5), padx=10, side = "left")       
        self.bottom_row = ctk.CTkFrame(self)
        self.bottom_row.pack(side="bottom", fill="x", pady=10, padx=10)
    # cli entry  
        self.cli_entry = ctk.CTkEntry(self.bottom_row, height=50, width=200, placeholder_text="Nhập lệnh CLI...")
        self.cli_entry.grid(row=0, column=0, padx=5)
        self.cli_entry.bind("<Return>", lambda event: self.send_cli_command())  # 👈 xử lý nhấn Enter
    # Nút gửi lệnh thủ công
        self.cli_send_button = ctk.CTkButton(self.bottom_row, text="📤Send", command=self.send_cli_command)
        self.cli_send_button.grid(row=0, column=1, padx=5)
    #nút lưu
        self.save_button = ctk.CTkButton(self.bottom_row, text="📝Save",font=self.default_font, height=30, width=10,command=self.send_save_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.save_button.grid(row=0, column=2, padx=60)#self.save_button.pack(side="right", fill="y", padx=(0,20))#pack(pady=(0, 5), padx=10, side = "right")          
    # Text log bên phải
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="left", fill="both", expand=True)
        self.log = ctk.CTkTextbox(self.right_panel,font=self.default_font, height=50)
        self.log.pack(fill="both", expand=True)
        # Tải danh sách cổng COM
        self.load_com_ports()





#hàm cho cổng serial
    def load_com_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.com_menu.configure(values=port_list)
        if port_list:
            self.com_menu.set(port_list[0])
        else:
            self.com_menu.set("")
    #chỗ này cho phần kết nối cổng com
    def toggle_connection(self):
        if not self.connected:
            try:
                port = self.com_menu.get()
                baud = int(self.baud_menu.get())
                self.ser = serial.Serial(port, baud, timeout=1)
                self.connected = True
                self.reading = True
                self.connect_button.configure(text="🔌Disconnect")
                self.write_log(f"✅ Đã kết nối {port} ({baud} baud)")
                self.after(100, self.read_serial_loop)  # bắt đầu đọc dữ liệu
                self.beep_success()
                self.show_info("⚠️","Đã Kết Nối")
            except Exception as e:
                self.write_log(f"❌ Lỗi: {e}")
                return
             # Gửi lệnh v; và xử lý hiển thị
            self.after(200, self.query_version_info)
        else:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.connected = False
            self.reading = False
            self.connect_button.configure(text="🔌Connect")
            self.write_log("⚠️ Đã ngắt kết nối")
            self.beep_success()
            # Xóa thông tin phiên bản
            self.info_box.configure(state="normal")
            self.info_box.delete("1.0", "end")
            self.info_box.configure(state="disabled")
     
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
        self.connect_button.configure(text="Connect")
        self.write_log("⚠️ Kết nối đã bị mất. Đã ngắt kết nối.")
        self.load_com_ports()
        self.beep_success()        
        self.show_info("⚠️","Mất Kết Nối")   

    #Cái này dể cho nút clear'tôi cũng éo nhớ có phải vậy không"
    def clear_log(self):
        self.log.delete("1.0", "end")
        self.beep_success()               

    #gửi lệnh hiển thị thông tin phiên bản
    def query_version_info(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.reset_input_buffer()
                self.ser.write(b"v;\n")
                self.write_log("📤 Gửi: v;")
                time.sleep(0.2)
                lines = []
                while self.ser.in_waiting:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    if line:
                        lines.append(line)
                version_text = "\n".join(lines)
                self.info_box.configure(state="normal")
                self.info_box.delete("1.0", "end")
                self.info_box.insert("1.0", version_text)
                self.info_box.configure(state="disabled") 
            except Exception as e:
                self.write_log(f"❌ Lỗi đọc version: {e}")
#CÁI NÀY CHO PHẦN GỬI LỆNH 

    def send_command_from_menu(self, menu_widget, command_map, label):
        if self.ser and self.ser.is_open:
           val = menu_widget.get()
           if val in command_map:
               command = f"{command_map[val]};\n"
               self.ser.write(command.encode())
               self.write_log(f"📤 Gửi: {command.strip()}")
               self.beep_success()
           else:
                self.write_log(f"⚠️ Không xác định {label}: {val}")
                self.show_info("⚠️", f"Không xác định {label}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")

#phần này của nút TX_POWER
    def send_pow_command(self):
        self.send_command_from_menu(
             menu_widget=self.pow_menu,
             command_map={
                  "Level 0": "p tx_power=0",
                  "Level 1": "p tx_power=1",
                  "Level 2": "p tx_power=2",
                  "Level 3": "p tx_power=3",
                  "Level 4": "p tx_power=4",
                  "Level 5": "p tx_power=5",
            
             },
             label="TX Power"
        )        
    
    #đây là cài đặt tần số 
    def send_rf_command(self):
        self.send_command_from_menu(
             menu_widget=self.rf_menu,
             command_map={
                  "868mhz": "p RF_BAND = 2",
                  "915mhz": "p rf_band = 1"
            
             },
             label="RF Band"
        )   
    #đây là cài đặt mode ví dụ 50hz 

    def send_mode_command(self):
        self.send_command_from_menu(
             menu_widget=self.mode_menu,
             command_map={
               "50hz": "p mode = 0",
               "31hz": "p mode = 1",
               "19hz": "p mode = 2",
               "FLRC":"p mode = 3",
               "FSK":  "p mode = 4"            
             },
             label=" Mode"
        )

    #cái này cho nút cài đặt order ví dụ aetr 
    def send_order_command(self):
        self.send_command_from_menu(
             menu_widget=self.order_menu,
             command_map={
               "AETR": "p tx_ch_order = 0",
               "TAER": "p tx_ch_order = 1",
               "ETAR": "p tx_ch_order = 2"            
             },
             label="Ch Order"
        )
    
    #cái này cho nút view module 
    def send_view_command(self):
        if not self.ser or not self.ser.is_open:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
            self.beep_error()
            return
        try:
            self.ser.reset_input_buffer()
            self.ser.write(b"pl;\n")
            self.write_log("📤 Gửi: pl;")
            time.sleep(0.3)
            raw_data = ""
            while self.ser.in_waiting:
                raw_data += self.ser.readline().decode(errors="ignore")

            self.write_log(f"📥 Nhận: \n{raw_data.strip()}")
            self.apply_config_to_ui(raw_data)
            self.show_info("✅", "Đã cập nhật giao diện theo thiết bị!")
            self.beep_success()
        except Exception as e: 
              self.write_log(f"❌ Lỗi khi đọc cấu hình: {e}")
              self.beep_error()   

    #auto update cau hinh
    def apply_config_to_ui(self, text):
        import re
    # ánh xạ từ tên cấu hình trả về sang các widget và mapping
        config_map = {
           # TX
           "Tx Power": (self.pow_menu, {
            "0": "Level 0", "1": "Level 1", "2": "Level 2", "3": "Level 3", "4": "Level 4", "5": "Level 5"}),
            "Tx Ch Order": (self.order_menu, {"0": "AETR", "1": "TAER", "2": "ETAR"}),
            "Tx Ch Source": (self.rc_menu, {"0": "None", "1": "CRSF", "2": "Sbus", "3": "mBridge"}),
            "Tx Ser Baudrate": (self.baudrate_menu, {
            "0": "9600", "1": "19200", "2": "38400", "3": "57600", "4": "115200", "5": "230400"}),
            "RF Band": (self.rf_menu, {"1": "915mhz", "2": "868mhz"}),
            "Mode": (self.mode_menu, {"0": "50hz", "1": "31hz", "2": "19hz", "3": "FLRC", "4": "FSK"}),
            "Bind Phrase": (self.bind_entry, None),
            "Tx Ser Dest": (self.dest_menu, {"0": "Serial", "2": "mBridge"}),
            "Tx Mav Component": (self.COMPONENT_menu, {"0": "OFF", "1": "ENABLED"}),
            "Tx Snd RadioStat": (self.radiostat_menu, {"0": "OFF", "1": "1Hz"}),
            "RF Ortho": (self.ortho_menu, {"0": "OFF", "1": "1/3", "2": "2/3", "3": "3/3"}),
            "Tx Power Sw Ch": (self.power_CH_menu, {
            "0": "OFF", "8": "CH12", "9": "CH13", "10": "CH14", "11": "CH15"}),

        # RX
            "Rx Power": (self.rxpow_menu, {
            "0": "Level 0", "1": "Level 1", "2": "Level 2", "3": "Level 3", "4": "Level 4", "5": "Level 5"}),
            "Rx Out Mode": (self.rxmode_menu, {"0": "Sbus", "1": "CRSF", "2": "Sbus INV"}),
            "Rx Ser Baudrate": (self.Baudrate_menu, {
            "0": "9600", "1": "19200", "2": "38400", "3": "57600", "4": "115200", "5": "230400"}),
            "Ser Link Mode": (self.RXMAVLINK_menu, {
            "0": "Transp", "1": "MAVLINK", "2": "MAVLINKX", "3": "MSPX"}),
            "Rx Snd RadioStat": (self.RadioStat_menu, {"0": "Off", "1": "Ardu_1", "2": "meth_b"}),
            "Rx Ser Port": (self.rxPort_menu, {"0": "Serial", "1": "Can"}),
            "Rx Snd RcChannel": (self.SND_RCCHANNEL_menu, {
            "0": "Off", "1": "rc Override", "2": "rc Channels"}),
            "Rx Out Rssi Ch": (self.RSSI_CH_menu, {"0": "Off", "10": "CH 14", "11": "CH 15", "12": "CH 16"}),
            "Rx Out LQ Ch": (self.LQ_CH_menu, {"0": "Off", "10": "CH 14", "11": "CH 15", "12": "CH 16"}),
            "Rx Power Sw Ch": (self.RXpower_CH_menu, {
            "0": "Off", "8": "CH12", "9": "CH13", "10": "CH14", "11": "CH15"}),

         }
        
# Map giá trị thực tế → index nếu thiết bị trả về không chuẩn
        special_reverse_map = {
        "Tx Power Sw Ch": {"12": "8", "13": "9", "14": "10", "15": "11"},
        "Tx Ser Baudrate": {"9600": "0", "19200": "1", "38400": "2", "57600": "3", "115200": "4", "230400": "5"},
         
         # RX ✅ thêm vào đây
        "Rx Ser Baudrate": {"9600": "0", "19200": "1", "38400": "2", "57600": "3", "115200": "4", "230400": "5"},
        "Rx Power Sw Ch": {"12": "8", "13": "9", "14": "10", "15": "11"},
        "Rx Out Rssi Ch": {"14": "10", "15": "11", "16": "12"},
        "Rx Out LQ Ch": {"14": "10", "15": "11", "16": "12"},
        }
         
        lines = text.strip().splitlines()
        for line in lines:
            self.write_log(f"[DEBUG] Xử lý dòng: {line}")
            if "=" in line:
                name_value = line.split("=")
                if len(name_value) >= 2:
                    name = name_value[0].strip().replace("Nhận:", "").strip()
                    value_raw = name_value[1].strip()
                    # Nếu unavailable → gán OFF
                    if "unavailable" in value_raw.lower():
                        self.write_log(f"⏭️ {name} = unavailable → set OFF nếu có")
                        if name in config_map:
                            widget, value_map = config_map[name]
                            if value_map and "0" in value_map:
                                widget.set(value_map["0"])  # OFF thường là index 0
                        continue
                    # Bắt các dạng: = số [bất kỳ]
                    match_number_bracket = re.search(r"= *(\d+)\s*\[\s*([^\]]*)\]", line)
                    if match_number_bracket:
                        index = match_number_bracket.group(1)
                        value = index
                    else:
                          # Trường hợp chuẩn có [n]
                        match = re.search(r"(.*?)\s*\[(\d+)\]", value_raw)
                        if match:
                            value, index = match.groups()
                        else:
                            value, index = value_raw, None
                    # Chuyển giá trị thực → index nếu cần
                    if name in special_reverse_map and value in special_reverse_map[name]:
                        old = value
                        index = special_reverse_map[name][value]
                        self.write_log(f"🔄 Mapping đặc biệt cho {name}: {old} → {index}")       
                        # Gán vào UI
                    if name in config_map:
                        widget, value_map = config_map[name]
                        if value_map:
                            if index and index in value_map:
                                widget.set(value_map[index])
                                self.write_log(f"✅ Gán {name} = {value_map[index]} (index = {index})")
                            elif value in value_map:
                                 widget.set(value_map[value])
                                 self.write_log(f"✅ Fallback theo value cho {name} = {value}")
                            
                            else:
                                self.write_log(f"⚠️ Không tìm thấy mapping cho {name} với index {index}")
                        else:
                             # Không có value_map → xử lý kiểu Entry
                            widget.delete(0, 'end')
                            widget.insert(0, value.strip())

    #cái này cho nút CH source
    def send_rc_command(self):
        self.send_command_from_menu(
             menu_widget=self.rc_menu,
             command_map={
               "None": "p tx_ch_source = 0",
               "Sbus": "p tx_ch_source = 2",
               "CRSF": "p tx_ch_source = 1",
               "mBridge": "p tx_ch_source = 3"           
             },
             label="CH Source"
        )

    #cái này cho nút dest   
    def send_dest_command(self):
        self.send_command_from_menu(
             menu_widget=self.dest_menu,
             command_map={
               "Serial": "p tx_ser_dest = 0",
               "mBridge": "p tx_ser_dest = 2"           
             },
             label="Ser Dest"
        ) 

    #cái này cho nút MÃ KHÓA     
    def send_bind_phrase(self):
        if self.ser and self.ser.is_open:
            phrase = self.bind_entry.get().strip()
            if phrase:
                command = f"p bind_phrase = {phrase};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()               
            else:
                self.write_log("⚠️ Vui lòng nhập nội dung bind_phrase!")
                self.beep_success()
                self.show_info("⚠️","Vui lòng nhập MÃ KHÓA")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!") 

    #CÁI NÀY CHO NÚT  save 
    def send_save_command(self):
        if self.ser and self.ser.is_open:
            command = "pstore;\n"
            self.ser.write(command.encode())
            self.write_log(f"📤 Gửi: {command.strip()}")
            self.beep_success()
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")        


    #kiểm tra kết nối serial      
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

    #đây là ortho
    def send_ortho_command(self):
        self.send_command_from_menu(
             menu_widget=self.ortho_menu,
             command_map={
               "OFF": "p RF_Ortho = 0",
                "1/3": "p RF_Ortho = 1",
                "2/3": "p RF_Ortho = 2",
                "3/3": "p RF_Ortho = 3"         
             },
             label="RF Ortho"
        ) 

    #cái này cho Tx Power Sw Ch
    
    def send_power_CH_command(self):
        self.send_command_from_menu(
             menu_widget=self.power_CH_menu,
             command_map={
                "OFF":  "p tx_power_sw_ch= 0",
                "CH12": "p tx_power_sw_ch= 8",
                "CH13": "p tx_power_sw_ch= 9",
                "CH14": "p tx_power_sw_ch= 10",
                "CH15": "p tx_power_sw_ch= 11"          
             },
             label="Tx Power CH"
        ) 

    #phần này cho baudrate
    def send_baudrate_command(self):
        self.send_command_from_menu(
             menu_widget=self.baudrate_menu,
             command_map={
                "9600": "p tx_ser_baudrate = 0",
                "19200": "p tx_ser_baudrate = 1",
                "38400": "p tx_ser_baudrate = 2",
                "57600": "p tx_ser_baudrate = 3",
                "115200": "p tx_ser_baudrate = 4",
                "230400": "p tx_ser_baudrate = 5"          
             },
             label="Baudrate"
        )  
    
    #phần này cho radiostat
    def send_radiostat_command(self):
        self.send_command_from_menu(
             menu_widget=self.radiostat_menu,
             command_map={
                "OFF": "tx_snd_radiostat = 0",
                "1Hz": "tx_snd_radiostat = 1"          
             },
             label="Snd RadioStat"
        ) 
     
    #phần này cho COMPONENT
    def send_COMPONENT_command(self):
        self.send_command_from_menu(
             menu_widget=self.COMPONENT_menu,
             command_map={
                "OFF": "p TX_MAV_COMPONENT = 0",
                "ENABLED": "p TX_MAV_COMPONENT = 1"       
             },
             label="Mav Component"
        )
      
  #PHẦN NÀY CHO RX

    #PHẦN NÈ CHO NÚT RX_POWER
    def send_rxpow_command(self):
        self.send_command_from_menu(
             menu_widget=self.rxpow_menu,
             command_map={
                "Level 0": "p rx_power=0",
                "Level 1": "p rx_power=1",
                "Level 2": "p rx_power=2",
                "Level 3": "p rx_power=3",
                "Level 4": "p rx_power=4",
                "Level 5": "p rx_power=5"      
             },
             label="RX_Power"
        )
              
    # cái này cho nút rxmode nà
    def send_rxmode_command(self):
        self.send_command_from_menu(
             menu_widget=self.rxmode_menu,
             command_map={
                "Sbus": "p RX_OUT_MODE = 0",
                "CRSF": "p RX_OUT_MODE = 1",
                "Sbus INV": "p RX_OUT_MODE = 2"     
             },
             label="Out Mode"
        )
 
    # cái này cho nút Rx Ser Baudrate
    def send_Baudrate_command(self):
        self.send_command_from_menu(
             menu_widget=self.Baudrate_menu,
             command_map={
                "9600": "p rx_ser_baudrate = 0",
                "19200": "p rx_ser_baudrate = 1",
                "38400": "p rx_ser_baudrate = 2",
                "57600": "p rx_ser_baudrate = 3",
                "115200": "p rx_ser_baudrate = 4",
                "230400": "p rx_ser_baudrate = 5"     
             },
             label="Ser Baudrate"
        )
    
    # cái này cho nút Rx LNK 
    def send_RXMAVLINK_command(self):
        self.send_command_from_menu(
             menu_widget=self.RXMAVLINK_menu,
             command_map={
                "Transp" : "p RX_SER_LINK_MODE = 0",
                "MAVLINK": "p RX_SER_LINK_MODE = 1",
                "MAVLINKX": "p RX_SER_LINK_MODE = 2",
                "MSPX": "p RX_SER_LINK_MODE = 3",     
             },
             label="Ser Link Mode"
        )        
    
    # cái này cho nút Rx Snd RadioStat 
    def send_RadioStat_command(self):
        self.send_command_from_menu(
             menu_widget=self.RadioStat_menu,
             command_map={
                "Off":    "p Rx_Snd_RadioStat = 0",
                "Ardu_1": "p Rx_Snd_RadioStat = 1",
                "meth_b": "p Rx_Snd_RadioStat = 2"     
             },
             label="Snd RadioStat"
        )
    # cái này cho nút Rx Ser Port
    def send_rxPort_command(self):
        self.send_command_from_menu(
             menu_widget=self.rxPort_menu,
             command_map={
                "Serial": "p Rx_Ser_Port = 0",
                "Can":    "p Rx_Ser_Port = 1"     
             },
             label="Ser Port"
        )
           
    # cái này cho nút RX_SND_RCCHANNEL
    def send_SND_RCCHANNEL_command(self):
        self.send_command_from_menu(
             menu_widget=self.SND_RCCHANNEL_menu,
             command_map={
                "Off": "p RX_SND_RCCHANNEL = 0",
                "rc Override": "p RX_SND_RCCHANNEL = 1", 
                "rc Channels": "p RX_SND_RCCHANNEL= 2"      
             },
             label="Snd RcChannel"
        )
          
   

    # cái này cho nút RX_OUT_RSSI_CH
    def send_RSSI_CH_command(self):
        self.send_command_from_menu(
             menu_widget=self.RSSI_CH_menu,
             command_map={
                "Off": "p RX_OUT_RSSI_CH = 0",
                "CH 14": "p RX_OUT_RSSI_CH = 10", 
                "CH 15": "p RX_OUT_RSSI_CH = 11" ,
                "CH 16": "p RX_OUT_RSSI_CH= 12"      
             },
             label="OUT RSSI CH"
        ) 

    # cái này cho nút RX_LQ_RSSI_CH
    def send_LQ_CH_command(self):
        self.send_command_from_menu(
             menu_widget=self.LQ_CH_menu,
             command_map={
                "Off": "p RX_OUT_LQ_CH = 0",
                "CH 14": "p RX_OUT_LQ_CH = 10", 
                "CH 15": "p RX_OUT_LQ_CH = 11" ,
                "CH 16": "p RX_OUT_LQ_CH= 12"     
             },
             label="OUT LQ CH"
        ) 

    #cái này cho nút rx Power Sw Ch
    def send_RXpower_CH_command(self):
        self.send_command_from_menu(
             menu_widget=self.RXpower_CH_menu,
             command_map={
                "Off": "p rx_power_sw_ch= 0",
                "CH12": "p rx_power_sw_ch= 8",
                "CH13": "p rx_power_sw_ch= 9",
                "CH14": "p rx_power_sw_ch= 10",
                "CH15": "p rx_power_sw_ch= 11"      
             },
             label="Power Sw Ch"
        ) 

    #cái này cho phần nhập lệnh cli thủ công
    def send_cli_command(self):
        if not self.connected or not self.ser:
            self.write_log("⚠️ Chưa kết nối!")
            return

        command = self.cli_entry.get().strip()
        if command:
           try:
               if not command.endswith(";"):
                   command += ";"  # tự thêm dấu ; nếu thiếu
               self.ser.write((command + "\n").encode())
               self.write_log(f"📤 Gửi (CLI): {command}")
           except Exception as e:
               self.write_log(f"❌ Lỗi gửi CLI: {e}")
        else:
            self.write_log("⚠️ Vui lòng nhập lệnh trước khi gửi.")  
            return
        self.cli_entry.delete(0, 'end')               

    #CÁI NÀY CHO NÚT CHUYỂN TX_CONFIG VÀ RX_CONFIG
    
    def switch_mode(self, value):
        if value == "💻TX CONFIG":
         self.rx_controls.pack_forget()
         self.tx_controls.pack()
        # Phát âm thanh & thông báo
         self.beep_success()
         self.show_info("Chuyển chế độ", "Đang ở chế độ cấu hình TX")
        elif value == "✈RX CONFIG":
         self.tx_controls.pack_forget()
         self.rx_controls.pack()
        # Phát âm thanh & thông báo
         self.beep_success()
         self.show_info("Chuyển chế độ", "Đang ở chế độ cấu hình RX")

    #cái này cho Nút RX-CONFIG
    def send_rx_mode(self):
     val = self.rx_mode_menu.get()
     if self.ser and self.ser.is_open:
          self.ser.write(f"rx_mode={val};\n".encode())
          self.write_log(f"📤 Gửi: rx_mode={val}")
     else:
          self.write_log("⚠️ Chưa kết nối thiết bị!")      
    
    
    def write_log(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")
    def show_info(self, title="Thông báo", message="Thành công!"):
         mbox.showinfo(title, message)
    def show_error(self, title="Lỗi", message="Đã xảy ra lỗi!"):
        mbox.showerror(title, message)

    


    # cái này cho Phát âm thanh
    def beep_success(self):
        if platform.system() == "Windows":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            print("\a")  # Tiếng bíp trên Linux/macOS
    def beep_error(self):
        if platform.system() == "Windows":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            print("\a")
           

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # "dark" hoặc "system"
    ctk.set_default_color_theme("green")  # hoặc "green", "dark-blue"   
    app = SerialTool()
    app.mainloop()
