import customtkinter as ctk
from PIL import Image
import os  # لفتح الفولدرات
from tkinter import messagebox

# --- Color Palette ---
COLOR_BG = "#1a1b1e"           
COLOR_SIDEBAR = "#25262b"      
COLOR_CARD = "#2c2e33"         
COLOR_ACCENT = "#4c6ef5"       
COLOR_HOVER = "#3b5bdb"        
COLOR_TEXT = "#e9ecef"         
COLOR_TEXT_DIM = "#868e96"     
COLOR_DANGER = "#fa5252"       
COLOR_SUCCESS = "#2CC985"      

class ModernMenuButton(ctk.CTkButton):
    def __init__(self, master, text, icon, command, is_active=False):
        self.cmd = command
        super().__init__(
            master, 
            text=f"  {icon}   {text}", 
            font=("Segoe UI", 15, "bold"), 
            anchor="w", 
            height=50, 
            fg_color="transparent", 
            text_color=COLOR_TEXT_DIM,
            hover_color=COLOR_CARD,
            corner_radius=8,
            command=self.on_click
        )
        self.is_active = is_active
        if is_active:
            self.set_active(True)

    def on_click(self):
        if self.cmd: self.cmd()

    def set_active(self, active):
        if active:
            self.configure(fg_color=COLOR_CARD, text_color=COLOR_ACCENT)
        else:
            self.configure(fg_color="transparent", text_color=COLOR_TEXT_DIM)

class GalleryItem(ctk.CTkFrame):
    def __init__(self, master, file_path, thumb_image, select_command, delete_command):
        super().__init__(master, width=110, height=110, fg_color="transparent")
        self.file_path = file_path
        self.pack_propagate(False)

        self.image_btn = ctk.CTkButton(
            self, 
            text="", 
            image=thumb_image, 
            fg_color=COLOR_CARD, 
            corner_radius=10,
            border_width=0,
            hover_color=COLOR_ACCENT,
            command=lambda: select_command(file_path)
        )
        self.image_btn.pack(fill="both", expand=True, padx=3, pady=3)

        self.del_btn = ctk.CTkButton(
            self,
            text="×",
            width=22,
            height=22,
            fg_color=COLOR_DANGER,
            hover_color="#c92a2a",
            text_color="white",
            font=("Arial", 14, "bold"),
            corner_radius=11,
            command=lambda: delete_command(self, file_path)
        )
        self.del_btn.place(relx=0.85, rely=0.05, anchor="n")

    def set_selected(self, selected):
        if selected:
            self.image_btn.configure(border_width=2, border_color=COLOR_ACCENT)
        else:
            self.image_btn.configure(border_width=0)

class HistoryRow(ctk.CTkFrame):
    """
    Advanced History Row: Shows Op, Date, Path, and Open Button.
    """
    def __init__(self, master, entry):
        super().__init__(master, fg_color=COLOR_BG, corner_radius=8, border_width=1, border_color=COLOR_CARD)
        self.pack(fill="x", pady=4, padx=5)
        
        self.folder_path = entry.get('location', '')
        
        # --- الترتيب هنا مهم جداً عشان الزرار يظهر ---
        
        # 1. الزرار الأخضر (نحطه الأول على اليمين عشان يحجز مكانه)
        self.btn_open = ctk.CTkButton(
            self, 
            text="📂 Open Folder", 
            width=100, 
            height=30, 
            fg_color=COLOR_SUCCESS, 
            hover_color="#229965",
            font=("Segoe UI", 11, "bold"),
            command=self.open_folder_safely
        )
        self.btn_open.pack(side="right", padx=10, pady=10)

        # 2. العداد (على اليمين برضه جنب الزرار)
        ctk.CTkLabel(self, text=f"{entry.get('count', 0)} Files", font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT).pack(side="right", padx=10)

        # 3. الأيقونة (على الشمال)
        icon = "📝"
        op = entry.get('operation', 'Unknown')
        if op == 'watermark': icon = "💧"
        elif op == 'resize': icon = "📏"
        elif op == 'convert': icon = "🔄"
        elif op == 'Batch Export': icon = "🚀"

        ctk.CTkLabel(self, text=icon, font=("Segoe UI", 18)).pack(side="left", padx=15)
        
        # 4. المعلومات والمسار (ياخدوا باقي المساحة في النص)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(content_frame, text=op.title(), font=("Segoe UI", 13, "bold"), text_color="white", anchor="w").pack(fill="x")
        
        # تجهيز عرض المسار بشكل شيك
        display_path = self.folder_path if self.folder_path else "Unknown Location"
        if len(display_path) > 60: display_path = "..." + display_path[-55:]
        
        ctk.CTkLabel(content_frame, text=f"Saved to: {display_path}", font=("Consolas", 11), text_color=COLOR_TEXT_DIM, anchor="w").pack(fill="x")


    def open_folder_safely(self):
        """
        يحاول يفتح الفولدر، ولو مش موجود يطلع رسالة خطأ
        """
        if self.folder_path and os.path.exists(self.folder_path):
            try:
                os.startfile(self.folder_path)
            except Exception as e:
                messagebox.showerror("System Error", f"Could not open folder.\n{e}")
        else:
            # رسالة احترافية في حالة عدم وجود الملف
            messagebox.showwarning(
                "Folder Not Found", 
                "⚠️ المسار غير موجود!\n\nيبدو أن المجلد تم حذفه أو نقله من مكانه الأصلي."
            )