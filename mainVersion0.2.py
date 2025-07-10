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

        self.title("mLRS Configurator_Version 0.2")
        self.geometry("800x660")
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
        self.pow_button = ctk.CTkButton(self.row2, text="🔋Power", command=self.send_pow_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.pow_button.grid(row=0, column=0, padx=(20, 10,))
        
        
        self.pow_menu = ctk.CTkComboBox(self.row2, values=["Level 0","Level 1", "Level 2", "Level 3", "Level 4","Level 5"], width=100,font=self.default_font)
        self.pow_menu.set("Level 0")
        self.pow_menu.grid(row=0, column=1, padx=10)
        
        # Dòng thứ 3: RF
        self.row3 = ctk.CTkFrame(self.tx_controls)
        self.row3.pack(pady=5, anchor="w")
        
        self.style_button = ctk.CTkButton(self.row3, text="📡RF Band", command=self.send_rf_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.style_button.grid(row=0, column=0, padx=(20, 10,))

        self.style_menu = ctk.CTkComboBox(self.row3, values=["868mhz", "915mhz"], width=100,font=self.default_font)
        self.style_menu.set("868mhz")
        self.style_menu.grid(row=0, column=1, padx=10)
        # Dòng thứ 4: tín hiệu đầu vào 
        self.row4 = ctk.CTkFrame(self.tx_controls)
        self.row4.pack(pady=5, anchor="w")

        self.rc_button = ctk.CTkButton(self.row4, text="📲CH Source", command=self.send_rc_protocol,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
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

        # dòng thứ 7:order 
        
        self.row7 = ctk.CTkFrame(self.tx_controls)
        self.row7.pack(pady=5, anchor="w")

        self.order_button = ctk.CTkButton(self.row7, text="🎮Order ", command=self.send_order_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.order_button.grid(row=0, column=0, padx=(20, 10,))

        self.order_menu = ctk.CTkComboBox(self.row7, values=["AETR", "TAER", "ETAR"], width=100,font=self.default_font)
        self.order_menu.set("AETR")
        self.order_menu.grid(row=0, column=1, padx=10)


        # dòng thứ 8:dest đích đến 
        
        self.row8 = ctk.CTkFrame(self.tx_controls)
        self.row8.pack(pady=5, anchor="w")

        self.dest_button = ctk.CTkButton(self.row8, text="🛰Dest ", command=self.send_dest_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.dest_button.grid(row=0, column=0, padx=(20, 10,))

        self.dest_menu = ctk.CTkComboBox(self.row8, values=["Serial", "mBridge"], width=100,font=self.default_font)
        self.dest_menu.set("Serial")
        self.dest_menu.grid(row=0, column=1, padx=10)

        #self.rx_controls = ctk.CTkFrame(self.left_panel)

        # dòng thứthứ9:RF RF_ORTHO đích đến 
        self.row9 = ctk.CTkFrame(self.tx_controls)
        self.row9.pack(pady=5, anchor="w")

        self.ortho_button = ctk.CTkButton(self.row9, text="🎚RF Ortho ", command=self.send_ortho_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.ortho_button.grid(row=0, column=0, padx=(20, 10,))

        self.ortho_menu = ctk.CTkComboBox(self.row9, values=["OFF", "1/3", "2/3", "3/3"], width=100,font=self.default_font)
        self.ortho_menu.set("OFF")
        self.ortho_menu.grid(row=0, column=1, padx=10)

         # dòng thứthứ 10 :Tx Power Sw Ch
        self.row10 = ctk.CTkFrame(self.tx_controls)
        self.row10.pack(pady=5, anchor="w")

        self.power_CH_button = ctk.CTkButton(self.row10, text="📡Tx Power CH", command=self.send_power_CH_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.power_CH_button.grid(row=0, column=0, padx=(20, 10,))

        self.power_CH_menu = ctk.CTkComboBox(self.row10, values=[  "OFF","CH12","CH13", "CH14", "CH15"], width=100,font=self.default_font)
        self.power_CH_menu.set("OFF")
        self.power_CH_menu.grid(row=0, column=1, padx=10)
         # dòng thứthứ 11 :Tx baudrate
        self.row11 = ctk.CTkFrame(self.tx_controls)
        self.row11.pack(pady=5, anchor="w")

        self.baudrate_button = ctk.CTkButton(self.row11, text="🎮Tx Baudrate", command=self.send_baudrate_command,font=self.default_font,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.baudrate_button.grid(row=0, column=0, padx=(20, 10,))

        self.baudrate_menu = ctk.CTkComboBox(self.row11, values=[  "9600","19200","38400", "57600", "115200","230400"], width=100,font=self.default_font)
        self.baudrate_menu.set("115200")
        self.baudrate_menu.grid(row=0, column=1, padx=10)
          # dòng thứ 12 :RADIOSTAT
        self.row12 = ctk.CTkFrame(self.tx_controls)
        self.row12.pack(pady=5, anchor="w")

        self.radiostat_button = ctk.CTkButton(self.row12, text="📲Radiostat",font=self.default_font, command=self.send_radiostat_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.radiostat_button.grid(row=0, column=0, padx=(20, 10,))

        self.radiostat_menu = ctk.CTkComboBox(self.row12,font=self.default_font, values=[  "OFF","1Hz"], width=100)
        self.radiostat_menu.set("1Hz")
        self.radiostat_menu.grid(row=0, column=1, padx=10)

         # dòng thứ 13 :COMPONENT
        self.row13 = ctk.CTkFrame(self.tx_controls)
        self.row13.pack(pady=5, anchor="w")

        self.COMPONENT_button = ctk.CTkButton(self.row13, text="🕹Component",font=self.default_font, command=self.send_COMPONENT_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
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

        self.rxpow_button = ctk.CTkButton(self.rx_row2, text="🔋RX_Power",font=self.default_font, command=self.send_rxpow_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxpow_button.grid(row=0, column=0, padx=(20, 10,))
        self.rxpow_menu = ctk.CTkComboBox(self.rx_row2,font=self.default_font, values=["Level 0","Level 1", "Level 2", "Level 3", "Level 4","Level 5"], width=100)
        self.rxpow_menu.set("Level 0")
        self.rxpow_menu.grid(row=0, column=1, padx=10)

# Dòng thứ 3: rx_mode
        self.rx_row3 = ctk.CTkFrame(self.rx_controls)
        self.rx_row3.pack(pady=5, anchor="w")
        self.rxmode_button = ctk.CTkButton(self.rx_row3,font=self.default_font, text="⚙️ RX OUT MODE", command=self.send_rxmode_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxmode_button.grid(row=0, column=0, padx=(20, 10))
        self.rxmode_menu = ctk.CTkComboBox(self.rx_row3,font=self.default_font, values=["Sbus", "CRSF", "Sbus INV"], width=100)
        self.rxmode_menu.set("CRSF")
        self.rxmode_menu.grid(row=0, column=1, padx=10)

# Dòng thứ 4:Rx Ser Baudrate
        self.rx_row4 = ctk.CTkFrame(self.rx_controls)
        self.rx_row4.pack(pady=5, anchor="w")
        self.Baudrate_button = ctk.CTkButton(self.rx_row4,font=self.default_font, text="🔭Rx Baudrate", command=self.send_Baudrate_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.Baudrate_button.grid(row=0, column=0, padx=(20, 10))
        self.Baudrate_menu = ctk.CTkComboBox(self.rx_row4,font=self.default_font, values=["9600","19200","38400", "57600", "115200","230400"], width=100)
        self.Baudrate_menu.set("57600")
        self.Baudrate_menu.grid(row=0, column=1, padx=10)
# Dòng thứ 5:Rx MAVLINK Mode
        self.rx_row5 = ctk.CTkFrame(self.rx_controls)
        self.rx_row5.pack(pady=5, anchor="w")
        self.RXMAVLINK_button = ctk.CTkButton(self.rx_row5,font=self.default_font, text="🛰Rx LNK Mode", command=self.send_RXMAVLINK_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.RXMAVLINK_button.grid(row=0, column=0, padx=(20, 10))
        self.RXMAVLINK_menu = ctk.CTkComboBox(self.rx_row5,font=self.default_font, values=["MAVLINK", "MAVLINKX", "MSPX"], width=100)
        self.RXMAVLINK_menu.set("MAVLINK")
        self.RXMAVLINK_menu.grid(row=0, column=1, padx=10)
# Dòng thứ 6:Rx Snd RadioStat
        self.rx_row6 = ctk.CTkFrame(self.rx_controls)
        self.rx_row6.pack(pady=5, anchor="w")
        self.RadioStat_button = ctk.CTkButton(self.rx_row6,font=self.default_font, text="🚀Rx RadioStat", command=self.send_RadioStat_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.RadioStat_button.grid(row=0, column=0, padx=(20, 10))
        self.RadioStat_menu = ctk.CTkComboBox(self.rx_row6,font=self.default_font, values=["Off", "Ardu_1", "meth_b"], width=100)
        self.RadioStat_menu.set("Ardu_1")
        self.RadioStat_menu.grid(row=0, column=1, padx=10) 
# Dòng thứ 7  :Rx Ser Port
        self.rx_row7 = ctk.CTkFrame(self.rx_controls)
        self.rx_row7.pack(pady=5, anchor="w")
        self.rxPort_button = ctk.CTkButton(self.rx_row7,font=self.default_font, text="🖥Rx Ser Port", command=self.send_rxPort_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.rxPort_button.grid(row=0, column=0, padx=(20, 10))
        self.rxPort_menu = ctk.CTkComboBox(self.rx_row7,font=self.default_font, values=["Serial", "Can"], width=100)
        self.rxPort_menu.set("Serial")
        self.rxPort_menu.grid(row=0, column=1, padx=10)               
# Dòng thứ 8  :RX_SND_RCCHANNEL
        self.rx_row8 = ctk.CTkFrame(self.rx_controls)
        self.rx_row8.pack(pady=5, anchor="w")
        self.SND_RCCHANNEL_button = ctk.CTkButton(self.rx_row8,font=self.default_font, text="🌐SND RC CH", command=self.send_SND_RCCHANNEL_command, fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
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

   # dòng thứthứ 11 :rx Power Sw Ch
        self.rx_row11 = ctk.CTkFrame(self.rx_controls)
        self.rx_row11.pack(pady=5, anchor="w")

        self.RXpower_CH_button = ctk.CTkButton(self.rx_row11, text="🎮Rx Power CH", command=self.send_RXpower_CH_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black",font=self.default_font)
        self.RXpower_CH_button.grid(row=0, column=0, padx=(20, 10,))

        self.RXpower_CH_menu = ctk.CTkComboBox(self.rx_row11, values=[  "Off","CH12","CH13", "CH14", "CH15"], width=100,font=self.default_font)
        self.RXpower_CH_menu.set("Off")
        self.RXpower_CH_menu.grid(row=0, column=1, padx=10)        
        
    #thông tin phiên bản
        self.info_box = ctk.CTkTextbox(self, height=70, width=290,font=self.default_font, state="disabled")#self.info_box = ctk.CTkTextbox(self, height=40, width=290)
        self.info_box.pack(side="left", fill="y", padx=(20, 10))#pack(pady=(0, 5), padx=10, side = "left")
        
        self.bottom_row = ctk.CTkFrame(self)
        self.bottom_row.pack(side="bottom", fill="x", pady=10, padx=10)
     # cli entry  
        self.cli_entry = ctk.CTkEntry(self.bottom_row, height=50, width=200, placeholder_text="Nhập lệnh CLI...")
        self.cli_entry.grid(row=0, column=0, padx=5)
    # Nút gửi lệnh thủ công
        self.cli_send_button = ctk.CTkButton(self.bottom_row, text="📤Send", command=self.send_cli_command)
        self.cli_send_button.grid(row=0, column=1, padx=5)

       #nút lưu
        self.save_button = ctk.CTkButton(self.bottom_row, text="📝Save",font=self.default_font, height=20, width=10,command=self.send_save_command,fg_color="#facc15",hover_color="#4d7bc5",text_color="black")
        self.save_button.grid(row=0, column=2, padx=5)#self.save_button.pack(side="right", fill="y", padx=(0,20))#pack(pady=(0, 5), padx=10, side = "right")   
        
      # Text log bên phải
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="left", fill="both", expand=True)
        self.log = ctk.CTkTextbox(self.right_panel,font=self.default_font, height=50)
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

    def clear_log(self):
        self.log.delete("1.0", "end")
        self.beep_success()               
    
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


#phần này của nút TX_POWER
    def send_pow_command(self):
        try:
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
                    self.beep_success()
                else:
                    self.write_log(f"⚠️ Không xác định công suất: {pow_val}")
                    self.beep_success()
                    self.show_info("⚠️","Không xác định công suất")
            else:
                self.write_log("⚠️ Chưa kết nối thiết bị!")
        except Exception as ex:
            print(ex)

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
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định kiểu truyền: {rf_val}")
                self.beep_success()
                self.show_info("⚠️","Không xác định kiểu truyền")
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
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định kiểu tốc độ: {mode_val}")
                self.beep_success()
                self.show_info("⚠️","Không xác định kiểu tốc độ")
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
                self.beep_success()
                
            else:
                self.write_log(f"⚠️ Không xác định kiểu order: {order_val}")
                self.beep_success()
                self.show_info("⚠️","Không xác định kiểu Order")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")       

    #đây là view module 
    def send_view_command(self):
        if self.ser and self.ser.is_open:
            command = "pl;\n"
            self.ser.write(command.encode())
            self.write_log(f"📤 Gửi: {command.strip()}")
            self.beep_success()
                

        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
            self.beep_success()
                        
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
               self.beep_success()
            
            else:
               self.write_log(f"⚠️ Không xác định RC Protocol: {protocol_val}")
               self.beep_success()
               self.show_info("⚠️","Không xác định RC Protocol")
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
                self.beep_success()
                
            else:
                self.write_log(f"⚠️ Không xác định kiểu đích đến: {dest_val}")
                self.beep_success()
                self.show_info("⚠️","Không xác định")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
    

    #đây là của MÃ KHÓA     
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
        if self.ser and self.ser.is_open:
            ortho_val = self.ortho_menu.get()
            
            ortho_command_map = {
                "OFF": "rf_ortho = 0",
                "1/3": "rf_ortho = 1",
                "2/3": "rf_ortho = 2",
                "3/3": "rf_ortho = 3"                 
            }
            if ortho_val in ortho_command_map:
                command = f"p {ortho_command_map[ortho_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
                
            else:
                self.write_log(f"⚠️ Không xác định ortho: {ortho_val}")
                self.beep_success()
                self.show_info("⚠️","Tần số này không thể sử dụng chức năng này")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")

    def send_power_CH_command(self):
        if self.ser and self.ser.is_open:
            power_CH_val = self.power_CH_menu.get()
            
            power_CH_command_map = {
                "OFF": "tx_power_sw_ch= 0",
                "CH12": "tx_power_sw_ch= 8",
                "CH13": "tx_power_sw_ch= 9",
                "CH14": "tx_power_sw_ch= 10",
                "CH15": "tx_power_sw_ch= 11"                 
            }
            if power_CH_val in power_CH_command_map:
                command = f"p {power_CH_command_map[power_CH_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định ortho: {power_CH_val}")
                self.beep_success()
                
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
   #phần này cho baudrate
    def send_baudrate_command(self):
        if self.ser and self.ser.is_open:
            baudrate_val = self.baudrate_menu.get()
            
            baudrate_command_map = {
                "9600": "tx_ser_baudrate = 0",
                "19200": "tx_ser_baudrate = 1",
                "38400": "tx_ser_baudrate = 2",
                "57600": "tx_ser_baudrate = 3",
                "115200": "tx_ser_baudrate = 4",
                "230400": "tx_ser_baudrate = 5"                 
            }
            if baudrate_val in baudrate_command_map:
                command = f"p {baudrate_command_map[baudrate_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định baudrate: {baudrate_val}")
                self.beep_success()
                
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
    
    #phần này cho radiostat
    def send_radiostat_command(self):
        if self.ser and self.ser.is_open:
            radiostat_val = self.radiostat_menu.get()
            
            radiostat_command_map = {
                "OFF": "tx_snd_radiostat = 0",
                "1Hz": "tx_snd_radiostat = 1"
                                 
            }
            if radiostat_val in radiostat_command_map:
                command = f"p {radiostat_command_map[radiostat_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định radiostat: {radiostat_val}")
                self.beep_success()
                
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")  
    #phần này cho COMPONENT
    def send_COMPONENT_command(self):
        if self.ser and self.ser.is_open:
            COMPONENT_val = self.COMPONENT_menu.get()
            
            COMPONENT_command_map = {
                "OFF": "TX_MAV_COMPONENT = 0",
                "ENABLED": "TX_MAV_COMPONENT = 1"
                                 
            }
            if COMPONENT_val in COMPONENT_command_map:
                command = f"p {COMPONENT_command_map[COMPONENT_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định COMPONENT: {COMPONENT_val}")
                self.beep_success()
                
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")                 

    
    #PHẦN NÀY CHO RX

    #PHẦN NÈ CHO NÚT RX_POWER
    def send_rxpow_command(self):
        if self.ser and self.ser.is_open:
            rxpow_val = self.rxpow_menu.get()
            
            rxpow_command_map = {
                "Level 0": "rx_power=0",
                "Level 1": "rx_power=1",
                "Level 2": "rx_power=2",
                "Level 3": "rx_power=3",
                "Level 4": "rx_power=4",
                "Level 5": "rx_power=5"
                
            }
            if rxpow_val in rxpow_command_map:
                command = f"p {rxpow_command_map[rxpow_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
               
            else:
                self.write_log(f"⚠️ Không xác định công suất: {rxpow_val}")
                self.beep_success()
                self.show_info("⚠️","Không xác định công suất")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
     
            
    #PHẦN NÈ CHO NÚT RX_OUT MODE

    # cho nút rxmode
    def send_rxmode_command(self):
        if self.ser and self.ser.is_open:
            rxmode_val = self.rxmode_menu.get()
            
            rxmode_command_map = {
                "Sbus": "RX_OUT_MODE = 0",
                "CRSF": "RX_OUT_MODE = 1",
                "Sbus INV": "RX_OUT_MODE = 2"                
            }
            if rxmode_val in rxmode_command_map:
                command = f"p {rxmode_command_map[rxmode_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định công suất: {rxmode_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
     
    # cho nút Rx Ser Baudrate
    def send_Baudrate_command(self):
        if self.ser and self.ser.is_open:
            Baudrate_val = self.Baudrate_menu.get()
            
            Baudrate_command_map = {
                "9600": "rx_ser_baudrate = 0",
                "19200": "rx_ser_baudrate = 1",
                "38400": "rx_ser_baudrate = 2",
                "57600": "rx_ser_baudrate = 3",
                "115200": "rx_ser_baudrate = 4",
                "230400": "rx_ser_baudrate = 5"                 
            }
            if Baudrate_val in Baudrate_command_map:
                command = f"p {Baudrate_command_map[Baudrate_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định Baudrate: {Baudrate_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")

    # cho nút Rx LNK 
    def send_RXMAVLINK_command(self):
        if self.ser and self.ser.is_open:
            RXMAVLINK_val = self.RXMAVLINK_menu.get()
            
            RXMAVLINK_command_map = {
                "MAVLINK": "RX_SER_LNK_MODE = 0",
                "MAVLINKX": "RX_SER_LNK_MODE = 1",
                "MSPX": "RX_SER_LNK_MODE = 2",
                  
            }
            if RXMAVLINK_val in RXMAVLINK_command_map:
                command = f"p {RXMAVLINK_command_map[RXMAVLINK_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định lnk mode : {RXMAVLINK_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")        
     # cho nút Rx Snd RadioStat 
    def send_RadioStat_command(self):
        if self.ser and self.ser.is_open:
            RadioStat_val = self.RadioStat_menu.get()
            
            RadioStat_command_map = {
                "Off": "RX_SND_RADIOSTAT = 0",
                "Ardu_1": "RX_SND_RADIOSTAT = 1",
                "meth_b": "RX_SND_RADIOSTAT = 2"
                  
            }
            if RadioStat_val in RadioStat_command_map:
                command = f"p {RadioStat_command_map[RadioStat_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định Snd RadioStat  : {RadioStat_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")
      # cho nút Rx Ser Port
    def send_rxPort_command(self):
        if self.ser and self.ser.is_open:
            rxPort_val = self.rxPort_menu.get()
            
            rxPort_command_map = {
                "Serial": "RX_SER_PORT = 0",
                "Can": "RX_SER_PORT = 1",                 
            }
            if rxPort_val in rxPort_command_map:
                command = f"p {rxPort_command_map[rxPort_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định Ser Port  : {rxPort_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")        

  # cho nút RX_SND_RCCHANNEL
    def send_SND_RCCHANNEL_command(self):
        if self.ser and self.ser.is_open:
            SND_RCCHANNEL_val = self.SND_RCCHANNEL_menu.get()
            
            SND_RCCHANNEL_command_map = {
                "Off": "RX_SND_RCCHANNEL = 0",
                "rc Override": "RX_SND_RCCHANNEL = 1", 
                "rc Channels": "RX_SND_RCCHANNEL= 2"                
            }
            if SND_RCCHANNEL_val in SND_RCCHANNEL_command_map:
                command = f"p {SND_RCCHANNEL_command_map[SND_RCCHANNEL_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định RCCHANNEL : {SND_RCCHANNEL_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!") 

 # cho nút RX_OUT_RSSI_CH
    def send_RSSI_CH_command(self):
        if self.ser and self.ser.is_open:
            RSSI_CH_val = self.RSSI_CH_menu.get()
            
            RSSI_CH_command_map = {
                "Off": "RX_OUT_RSSI_CH = 0",
                "CH 14": "RX_OUT_RSSI_CH = 10", 
                "CH 15": "RX_OUT_RSSI_CH = 11" ,
                "CH 16": "RX_OUT_RSSI_CH= 12"                
            }
            if RSSI_CH_val in RSSI_CH_command_map:
                command = f"p {RSSI_CH_command_map[RSSI_CH_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định OUT RSSI_CH: {RSSI_CH_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!") 
# cho nút RX_LQ_RSSI_CH
    def send_LQ_CH_command(self):
        if self.ser and self.ser.is_open:
            LQ_CH_val = self.LQ_CH_menu.get()
            
            LQ_CH_command_map = {
                "Off": "RX_OUT_LQ_CH = 0",
                "CH 14": "RX_OUT_LQ_CH = 10", 
                "CH 15": "RX_OUT_LQ_CH = 11" ,
                "CH 16": "RX_OUT_LQ_CH= 12"                
            }
            if LQ_CH_val in LQ_CH_command_map:
                command = f"p {LQ_CH_command_map[LQ_CH_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
            else:
                self.write_log(f"⚠️ Không xác định OUT RSSI_CH: {LQ_CH_val}")
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!") 
#rx Power Sw Ch
    def send_RXpower_CH_command(self):
        if self.ser and self.ser.is_open:
            RXpower_CH_val = self.RXpower_CH_menu.get()
            
            RXpower_CH_command_map = {
                "Off": "rx_power_sw_ch= 0",
                "CH12": "rx_power_sw_ch= 8",
                "CH13": "rx_power_sw_ch= 9",
                "CH14": "rx_power_sw_ch= 10",
                "CH15": "rx_power_sw_ch= 11"                 
            }
            if RXpower_CH_val in RXpower_CH_command_map:
                command = f"p {RXpower_CH_command_map[RXpower_CH_val]};\n"
                self.ser.write(command.encode())
                self.write_log(f"📤 Gửi: {command.strip()}")
                self.beep_success()
            else:
                self.write_log(f"⚠️ Không xác định SW Ch: {RXpower_CH_val}")
                self.beep_success()
                
        else:
            self.write_log("⚠️ Chưa kết nối thiết bị!")   


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
    # Phát âm thanh
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
