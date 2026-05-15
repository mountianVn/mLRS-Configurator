import customtkinter as ctk
import tkinter.messagebox as mbox
import platform, time, os, sys
from cli_manager import CLIManager

if platform.system() == "Windows":
    import winsound

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except AttributeError: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SerialToolGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cli = CLIManager()
        self.default_font = ("Arial", 14)
        
        self.title("mLRS Configurator_Version 0.4")
        self.geometry("800x700")
        self.resizable(False, False)
        try: self.iconbitmap(resource_path("mLRS.ico"))
        except: pass

        self.setup_ui()
        self.load_com_ports()

    def setup_ui(self):
        # --- ROW 1: Connection Bar (Giống hệt ảnh gốc) ---
        self.row1 = ctk.CTkFrame(self)
        self.row1.pack(pady=(15, 10), padx=20, fill="x")

        ctk.CTkLabel(self.row1, text="Baud", font=self.default_font).grid(row=0, column=0, padx=10)
        self.baud_menu = ctk.CTkComboBox(self.row1, values=["9600", "57600", "115200"], width=100)
        self.baud_menu.set("115200")
        self.baud_menu.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(self.row1, text="Com", font=self.default_font).grid(row=0, column=2, padx=10)
        self.com_menu = ctk.CTkComboBox(self.row1, values=[], width=100)
        self.com_menu.grid(row=0, column=3, padx=10)

        # Nút màu vàng đặc trưng #facc15
        self.btn_style = {"fg_color": "#facc15", "hover_color": "#4d7bc5", "text_color": "black", "font": self.default_font}

        ctk.CTkButton(self.row1, text="Refresh", width=20, command=self.load_com_ports, **self.btn_style).grid(row=0, column=4, padx=10)
        self.conn_btn = ctk.CTkButton(self.row1, text="🔌Connect", width=100, command=self.toggle_connection, **self.btn_style)
        self.conn_btn.grid(row=0, column=5, padx=10)
        ctk.CTkButton(self.row1, text="🧹Clear Log", width=20, command=lambda: self.log.delete("1.0", "end"), **self.btn_style).grid(row=0, column=6, padx=10)
        ctk.CTkButton(self.row1, text="🖊View", width=20, command=self.view_config, **self.btn_style).grid(row=0, column=7, padx=10)

        # --- MAIN PANEL ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cột trái: Controls
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        self.mode_switch = ctk.CTkSegmentedButton(self.left_panel, values=["💻TX CONFIG", "✈RX CONFIG"], command=self.switch_mode)
        self.mode_switch.pack(pady=(5, 10), padx=10)
        self.mode_switch.set("💻TX CONFIG")

        ctk.CTkLabel(self.left_panel, text="📦 Module Type", font=self.default_font).pack()
        self.mod_menu = ctk.CTkComboBox(self.left_panel, values=["2.4GHz", "868/915MHz", "433MHz"], command=self.on_mod_change)
        self.mod_menu.set("868/915MHz")
        self.mod_menu.pack(pady=(0, 10))

        # Khung chứa các dòng lệnh (TX và RX riêng biệt)
        self.tx_controls = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.rx_controls = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.tx_controls.pack()

        self.build_tx_ui()
        self.build_rx_ui()

        # Cột phải: Log & Info
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="left", fill="both", expand=True)
        
        self.info_box = ctk.CTkTextbox(self, height=80, width=300, font=self.default_font, state="disabled")
        self.info_box.pack(side="left", fill="y", padx=(20, 10), pady=10)

        self.log = ctk.CTkTextbox(self.right_panel, font=self.default_font)
        self.log.pack(fill="both", expand=True)

        # --- BOTTOM ROW ---
        self.bottom_row = ctk.CTkFrame(self)
        self.bottom_row.pack(side="bottom", fill="x", pady=10, padx=20)

        self.cli_entry = ctk.CTkEntry(self.bottom_row, height=50, placeholder_text="Nhập lệnh CLI...")
        self.cli_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cli_entry.bind("<Return>", lambda e: self.send_cli())

        ctk.CTkButton(self.bottom_row, text="📤Send", width=60, command=self.send_cli, **self.btn_style).pack(side="left", padx=5)
        ctk.CTkButton(self.bottom_row, text="🛠️Setup", width=60, command=self.run_setup, **self.btn_style).pack(side="left", padx=5)
        ctk.CTkButton(self.bottom_row, text="📝Save", width=60, command=self.save_pstore, **self.btn_style).pack(side="left", padx=5)

    def build_tx_ui(self):
        # Tái hiện các hàng y hệt v0.4
        tx_list = [
            ("⚙️ Power", "p tx_power", ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]),
            ("📡RF Band", "p rf_band", ["868mhz", "915mhz"]),
            ("⚙️CH Source", "p tx_ch_source", ["None", "Sbus", "CRSF", "mBridge"]),
            ("⚙️ Mode", "p mode", ["50hz", "31hz", "19hz", "FLRC", "FSK"]),
            ("🎮Ch Order", "p tx_ch_order", ["AETR", "TAER", "ETAR"]),
            ("⚙️Ser Dest", "p tx_ser_dest", ["Serial", "mBridge"]),
            ("⚙️RF Ortho", "p RF_Ortho", ["OFF", "1/3", "2/3", "3/3"]),
            ("⚙️Tx Power CH", "p tx_power_sw_ch", ["OFF", "CH12", "CH13", "CH14", "CH15"]),
            ("⚙️Tx Baudrate", "p tx_ser_baudrate", ["9600", "57600", "115200", "230400"]),
            ("⚙️Snd RadioStat", "tx_snd_radiostat", ["OFF", "1Hz"]),
            ("🕹Mav Component", "p TX_MAV_COMPONENT", ["OFF", "ENABLED"])
        ]
        self.tx_widgets = {}
        for label, cmd, vals in tx_list:
            self.tx_widgets[cmd] = self.create_control_row(self.tx_controls, label, cmd, vals)
        
        # Bind Phrase đặc biệt (Entry thay vì ComboBox)
        row = ctk.CTkFrame(self.tx_controls); row.pack(pady=2, anchor="w")
        ctk.CTkButton(row, text="🔑Bind Phrase", width=140, command=self.send_bind, **self.btn_style).grid(row=0, column=0, padx=(20, 10))
        self.bind_entry = ctk.CTkEntry(row, width=100); self.bind_entry.grid(row=0, column=1, padx=10)

    def build_rx_ui(self):
        rx_list = [
            ("⚙️RX_Power", "p rx_power", ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]),
            ("⚙️Out Mode", "p RX_OUT_MODE", ["Sbus", "CRSF", "Sbus INV"]),
            ("⚙️Ser Baudrate", "p rx_ser_baudrate", ["9600", "57600", "115200", "230400"]),
            ("⚙️Ser Link Mode", "p RX_SER_LINK_MODE", ["Transp", "MAVLINK", "MAVLINKX", "MSPX"]),
            ("⚙️Snd RadioStat", "p Rx_Snd_RadioStat", ["Off", "Ardu_1", "meth_b"]),
            ("⚙️Ser Port", "p Rx_Ser_Port", ["Serial", "Can"]),
            ("⚙️Snd RcChannel", "p RX_SND_RCCHANNEL", ["Off", "rc Override", "rc Channels"]),
            ("📡OUT RSSI CH", "p RX_OUT_RSSI_CH", ["Off", "CH 14", "CH 15", "CH 16"]),
            ("📶OUT LQ CH", "p RX_OUT_LQ_CH", ["Off", "CH 14", "CH 15", "CH 16"]),
            ("🎮Power Sw Ch", "p rx_power_sw_ch", ["Off", "CH12", "CH13", "CH14", "CH15"])
        ]
        self.rx_widgets = {}
        for label, cmd, vals in rx_list:
            self.rx_widgets[cmd] = self.create_control_row(self.rx_controls, label, cmd, vals)

    def create_control_row(self, parent, label, cmd_base, vals):
        row = ctk.CTkFrame(parent); row.pack(pady=2, anchor="w")
        btn = ctk.CTkButton(row, text=label, width=140, command=lambda: self.send_mapped(cmd_base), **self.btn_style)
        btn.grid(row=0, column=0, padx=(20, 10))
        combo = ctk.CTkComboBox(row, values=vals, width=100)
        combo.set(vals[0]); combo.grid(row=0, column=1, padx=10)
        return combo

    # --- LOGIC XỬ LÝ ---
    def load_com_ports(self):
        ports = self.cli.get_ports()
        self.com_menu.configure(values=ports)
        if ports: self.com_menu.set(ports[0])

    def toggle_connection(self):
        if not self.cli.connected:
            ok, msg = self.cli.connect(self.com_menu.get(), self.baud_menu.get())
            if ok:
                self.conn_btn.configure(text="🔌Disconnect", fg_color="red")
                self.write_log(msg)
                self.update_info_box()
                self.beep()
            else: self.write_log(msg)
        else:
            self.write_log(self.cli.disconnect())
            self.conn_btn.configure(text="🔌Connect", fg_color="#facc15")
            self.info_box.configure(state="normal"); self.info_box.delete("1.0", "end"); self.info_box.configure(state="disabled")

    def update_info_box(self):
        v = self.cli.get_version_info()
        self.info_box.configure(state="normal"); self.info_box.insert("1.0", v); self.info_box.configure(state="disabled")

    def switch_mode(self, val):
        if val == "💻TX CONFIG":
            self.rx_controls.pack_forget(); self.tx_controls.pack()
        else:
            self.tx_controls.pack_forget(); self.rx_controls.pack()
        self.beep()

    def send_mapped(self, cmd_base):
        # Lấy widget tương ứng (từ TX hoặc RX)
        is_rx = self.mode_switch.get() == "✈RX CONFIG"
        widgets = self.rx_widgets if is_rx else self.tx_widgets
        val = widgets[cmd_base].get()
        # Logic chuyển đổi text sang index giống v0.4
        idx = widgets[cmd_base].cget("values").index(val)
        self.write_log(self.cli.send_raw(f"{cmd_base}={idx}")[1])
        self.beep()

    def send_bind(self):
        phrase = self.bind_entry.get()
        if phrase: self.write_log(self.cli.send_raw(f"p bind_phrase={phrase}")[1]); self.beep()
        else: mbox.showwarning("Thiếu thông tin", "Vui lòng nhập Bind Phrase")

    def view_config(self):
        self.write_log(self.cli.send_raw("pl;")[1])

    def save_pstore(self):
        self.write_log(self.cli.send_raw("pstore")[1])
        mbox.showinfo("Save", "Đã lưu cấu hình!")

    def send_cli(self):
        cmd = self.cli_entry.get()
        if cmd: self.write_log(self.cli.send_raw(cmd)[1]); self.cli_entry.delete(0, 'end')

    def on_mod_change(self, val):
        # Logic đổi menu dựa theo module
        if val == "2.4GHz":
            self.tx_widgets["p rf_band"].configure(values=["2.4GHz"])
            self.tx_widgets["p mode"].configure(values=["50hz", "31hz", "111hz"])
        elif val == "868/915MHz":
            self.tx_widgets["p rf_band"].configure(values=["868mhz", "915mhz"])
            self.tx_widgets["p mode"].configure(values=["31hz", "19hz", "FSK"])
        self.write_log(f"🔄 Module: {val}")

    def run_setup(self):
        self.write_log("🛠️ Đang Setup tự động...")
        is_rx = self.mode_switch.get() == "✈RX CONFIG"
        widgets = self.rx_widgets if is_rx else self.tx_widgets
        for cmd in widgets:
            self.send_mapped(cmd)
            self.update(); time.sleep(0.2)
        self.write_log("✅ Hoàn tất!")

    def write_log(self, msg):
        self.log.insert("end", f"{msg}\n"); self.log.see("end")

    def beep(self):
        if platform.system() == "Windows": winsound.MessageBeep()
