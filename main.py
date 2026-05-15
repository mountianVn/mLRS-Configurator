import customtkinter as ctk
from gui_manager import SerialToolGUI
import sys

def main():
    try:
        # 1. Thiết lập giao diện (Dark/Light mode)
        ctk.set_appearance_mode("dark")  # Chế độ tối
        ctk.set_default_color_theme("blue") # Chủ đề màu xanh

        # 2. Khởi tạo ứng dụng từ file gui_manager
        print("--- Đang khởi động mLRS Configurator v0.4 ---")
        app = SerialToolGUI()
        
        # 3. Chạy vòng lặp chính
        app.mainloop()
        
    except Exception as e:
        print(f"❌ Lỗi khi khởi chạy ứng dụng: {e}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()