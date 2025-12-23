import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import webbrowser 
from PIL import Image

from image_core import ImageProcessor
from ui_components import (
    GalleryItem, HistoryRow, ModernMenuButton, 
    COLOR_BG, COLOR_SIDEBAR, COLOR_CARD, COLOR_ACCENT, COLOR_TEXT, COLOR_DANGER
)

# Set Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") 

class ProImageStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Logic ---
        self.processor = ImageProcessor()
        self.selected_files = [] 
        self.current_preview_path = None
        self.gallery_widgets = {} 
        self.nav_buttons = {} 
        
        # Default Settings
        self.settings = {
            'wm_enabled': False, 'wm_path': None, 'wm_pos': 'center', 
            'wm_x': 0.5, 'wm_y': 0.5, 'wm_opacity': 0.8, 'wm_scale': 0.3,
            'resize_enabled': False, 'resize_scale': 100,
            'format': 'JPG'
        }

        # --- Main Window ---
        self.title("Image Studio Pro")
        self.geometry("1400x900")
        self.configure(fg_color=COLOR_BG)

        # Layout Grid
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Viewport
        self.grid_columnconfigure(2, weight=0) # Controls
        self.grid_rowconfigure(0, weight=1)    # Main
        self.grid_rowconfigure(1, weight=0)    # Filmstrip

        # --- Init UI Sections ---
        self.setup_sidebar()
        self.setup_viewport()
        self.setup_controls_panel()
        self.setup_filmstrip()

        # Start
        self.change_view("home")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.pack_propagate(False)

        # Branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=(40, 40))
        ctk.CTkLabel(brand_frame, text="ISP", font=("Segoe UI Black", 36), text_color=COLOR_ACCENT).pack(side="left")
        ctk.CTkLabel(brand_frame, text="STUDIO", font=("Segoe UI", 36), text_color="white").pack(side="left", padx=5)

        # Navigation
        self.nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_container.pack(fill="x", padx=15)

        self.add_nav_item("home", "Library", "📂")
        self.add_nav_item("watermark", "Watermark", "💧")
        self.add_nav_item("resize", "Resizer", "📏")
        self.add_nav_item("convert", "Converter", "🔄")
        self.add_nav_item("history", "History", "📜")

        # Developer Signature
        dev_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        dev_frame.pack(side="bottom", pady=(10, 20))
        
        ctk.CTkLabel(dev_frame, text="Developed by Ahmed Samer", font=("Segoe UI", 11), text_color="gray").pack()
        
        github_btn = ctk.CTkButton(
            dev_frame, 
            text="github.com/Ahmed-Samer", 
            font=("Segoe UI", 10, "underline"), 
            text_color=COLOR_ACCENT, 
            fg_color="transparent", 
            hover_color=COLOR_BG,
            height=20,
            cursor="hand2",
            command=self.open_github
        )
        github_btn.pack()

        # Export Button
        self.btn_export = ctk.CTkButton(
            self.sidebar, 
            text="🚀  START EXPORT", 
            font=("Segoe UI", 14, "bold"), 
            height=55, 
            fg_color=COLOR_ACCENT, 
            hover_color="#3b5bdb", 
            corner_radius=12,
            command=lambda: self.change_view("export")
        )
        self.btn_export.pack(side="bottom", pady=(20, 10), padx=20, fill="x")

    def open_github(self):
        webbrowser.open("https://github.com/Ahmed-Samer")

    def add_nav_item(self, key, text, icon):
        btn = ModernMenuButton(self.nav_container, text, icon, lambda: self.change_view(key))
        btn.pack(pady=5, fill="x")
        self.nav_buttons[key] = btn

    def setup_viewport(self):
        self.viewport_container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.viewport_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.viewport = ctk.CTkFrame(self.viewport_container, fg_color=COLOR_BG, corner_radius=15, border_width=2, border_color=COLOR_CARD)
        self.viewport.pack(fill="both", expand=True)

        self.preview_label = ctk.CTkLabel(self.viewport, text="Select an image to start editing", font=("Segoe UI", 18), text_color="gray")
        self.preview_label.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.preview_label.bind("<Button-1>", self.on_preview_click)
        self.preview_label.bind("<B1-Motion>", self.on_preview_drag)

    def setup_controls_panel(self):
        self.controls = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.controls.grid(row=0, column=2, rowspan=2, sticky="nsew")
        self.controls.pack_propagate(False)

        self.lbl_panel_title = ctk.CTkLabel(self.controls, text="Controls", font=("Segoe UI", 22, "bold"), text_color="white", anchor="w")
        self.lbl_panel_title.pack(pady=(40, 20), padx=25, fill="x")

        ctk.CTkFrame(self.controls, height=2, fg_color=COLOR_CARD).pack(fill="x", padx=25, pady=(0, 20))

        self.tools_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        self.tools_frame.pack(fill="both", expand=True, padx=25)

    def setup_filmstrip(self):
        self.filmstrip_frame = ctk.CTkScrollableFrame(self, height=130, orientation="horizontal", label_text="", fg_color="transparent")
        self.filmstrip_frame.grid(row=1, column=1, sticky="ew", padx=20, pady=(0, 20))

    # ================= UI Logic =================

    def change_view(self, view_name):
        self.current_view = view_name
        
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == view_name)
        
        if view_name == "export":
            self.btn_export.configure(fg_color="white", text_color=COLOR_ACCENT)
        else:
            self.btn_export.configure(fg_color=COLOR_ACCENT, text_color="white")

        for widget in self.tools_frame.winfo_children(): widget.destroy()
        
        titles = {
            "home": "Library", "watermark": "Watermark", "resize": "Dimensions",
            "convert": "Format", "export": "Review & Export", "history": "History"
        }
        self.lbl_panel_title.configure(text=titles.get(view_name, "Settings"))

        if view_name == "home": self.build_home()
        elif view_name == "watermark": self.build_watermark()
        elif view_name == "resize": self.build_resize()
        elif view_name == "convert": self.build_convert()
        elif view_name == "export": self.build_export()
        elif view_name == "history": self.build_history()
        
        self.update_pipeline_preview()

    # ================= Tool Builders =================

    def section_header(self, text):
        return ctk.CTkLabel(self.tools_frame, text=text.upper(), font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT, anchor="w")

    def build_home(self):
        self.section_header("ACTIONS").pack(fill="x", pady=(0, 10))
        ctk.CTkButton(self.tools_frame, text="Import Images", command=self.import_images, height=50, fg_color=COLOR_CARD, hover_color=COLOR_ACCENT, corner_radius=10, font=("Segoe UI", 14)).pack(fill="x", pady=5)
        ctk.CTkButton(self.tools_frame, text="Clear Library", command=self.clear_library, height=40, fg_color="transparent", border_width=1, border_color=COLOR_DANGER, text_color=COLOR_DANGER, hover_color="#300000").pack(fill="x", pady=10)
        
        self.section_header("STATS").pack(fill="x", pady=(30, 10))
        stat_card = ctk.CTkFrame(self.tools_frame, fg_color=COLOR_CARD, corner_radius=10)
        stat_card.pack(fill="x", pady=5)
        ctk.CTkLabel(stat_card, text=f"{len(self.selected_files)}", font=("Segoe UI", 32, "bold"), text_color="white").pack(pady=(15, 0))
        ctk.CTkLabel(stat_card, text="Selected Files", font=("Segoe UI", 12), text_color="gray").pack(pady=(0, 15))

    def build_watermark(self):
        self.chk_wm = ctk.CTkSwitch(self.tools_frame, text="Enable Watermark", command=self.update_settings, progress_color=COLOR_ACCENT, font=("Segoe UI", 14))
        if self.settings['wm_enabled']: self.chk_wm.select()
        self.chk_wm.pack(pady=10, anchor="w")

        ctk.CTkFrame(self.tools_frame, height=2, fg_color=COLOR_CARD).pack(fill="x", pady=10)

        self.section_header("SOURCE").pack(fill="x", pady=(10, 5))
        self.btn_wm_up = ctk.CTkButton(self.tools_frame, text="Choose Logo...", command=self.upload_watermark, fg_color=COLOR_CARD, hover_color=COLOR_ACCENT, height=40)
        self.btn_wm_up.pack(fill="x")
        if self.settings['wm_path']: self.btn_wm_up.configure(text="Change Logo (Loaded)", fg_color="#1c4f2a")

        self.section_header("SETTINGS").pack(fill="x", pady=(20, 5))
        
        self.create_slider("Opacity", 0.1, 1.0, self.settings['wm_opacity'], self.slider_opacity_cb)
        self.create_slider("Scale", 0.1, 0.8, self.settings['wm_scale'], self.slider_scale_cb)

        self.section_header("PLACEMENT").pack(fill="x", pady=(20, 5))
        self.combo_pos = ctk.CTkComboBox(self.tools_frame, values=["center", "bottom_right", "top_left", "manual"], command=self.on_pos_change, fg_color=COLOR_CARD, border_color=COLOR_CARD, button_color=COLOR_ACCENT)
        self.combo_pos.set(self.settings.get('wm_pos', 'center'))
        self.combo_pos.pack(fill="x", pady=5)
        
        self.manual_ctrls = ctk.CTkFrame(self.tools_frame, fg_color="transparent")
        ctk.CTkLabel(self.manual_ctrls, text="Drag image to position!", text_color=COLOR_ACCENT, font=("Segoe UI", 11)).pack(pady=5)
        if self.settings['wm_pos'] == 'manual': self.manual_ctrls.pack(fill="x")

    def build_resize(self):
        self.chk_resize = ctk.CTkSwitch(self.tools_frame, text="Enable Resizing", command=self.update_settings, progress_color=COLOR_ACCENT, font=("Segoe UI", 14))
        if self.settings['resize_enabled']: self.chk_resize.select()
        self.chk_resize.pack(pady=10, anchor="w")
        
        ctk.CTkFrame(self.tools_frame, height=2, fg_color=COLOR_CARD).pack(fill="x", pady=10)

        self.lbl_resize_txt = ctk.CTkLabel(self.tools_frame, text=f"{int(self.settings['resize_scale'])}%", font=("Segoe UI", 48, "bold"), text_color="white")
        self.lbl_resize_txt.pack(pady=20)
        
        self.create_slider("Scale Percentage", 10, 200, self.settings['resize_scale'], self.slider_resize_cb)

    def build_convert(self):
        self.section_header("OUTPUT FORMAT").pack(fill="x", pady=(0, 10))
        self.combo_fmt = ctk.CTkSegmentedButton(self.tools_frame, values=["JPG", "PNG", "WEBP", "ICO"], command=self.update_settings, selected_color=COLOR_ACCENT, selected_hover_color=COLOR_ACCENT)
        self.combo_fmt.set(self.settings.get('format', 'JPG'))
        self.combo_fmt.pack(fill="x", pady=10)

    def build_export(self):
        card = ctk.CTkFrame(self.tools_frame, fg_color=COLOR_CARD, corner_radius=15)
        card.pack(fill="x", pady=10, ipadx=15, ipady=15)
        
        ctk.CTkLabel(card, text="Ready to Process", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(card, text=f"{len(self.selected_files)} Images queued", text_color="gray").pack(anchor="w", pady=(0, 10))
        
        self.summary_row(card, "Watermark", "ON" if self.settings['wm_enabled'] else "OFF")
        self.summary_row(card, "Resize", f"{int(self.settings['resize_scale'])}%" if self.settings['resize_enabled'] else "OFF")
        self.summary_row(card, "Format", self.settings['format'])

        ctk.CTkButton(self.tools_frame, text="Start Batch Processing", command=self.run_pipeline_export, height=60, fg_color=COLOR_ACCENT, hover_color="#3b5bdb", font=("Segoe UI", 16, "bold"), corner_radius=12).pack(fill="x", pady=20)

    def summary_row(self, master, label, value):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=label, text_color="gray").pack(side="left")
        ctk.CTkLabel(f, text=value, text_color="white", font=("Segoe UI", 12, "bold")).pack(side="right")

    def build_history(self):
        history = self.processor.history_mgr.get_history()
        scroll = ctk.CTkScrollableFrame(self.tools_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        if not history: ctk.CTkLabel(scroll, text="No history yet", text_color="gray").pack(pady=20)
        for entry in history: HistoryRow(scroll, entry)

    def create_slider(self, label, min_val, max_val, current, callback):
        ctk.CTkLabel(self.tools_frame, text=label, text_color="gray", font=("Segoe UI", 12)).pack(anchor="w", pady=(10,0))
        slider = ctk.CTkSlider(self.tools_frame, from_=min_val, to=max_val, command=callback, button_color=COLOR_ACCENT, progress_color=COLOR_ACCENT)
        slider.set(current)
        slider.pack(fill="x", pady=5)
        return slider

    # ================= Callbacks =================

    def slider_opacity_cb(self, val): 
        self.settings['wm_opacity'] = val
        self.update_pipeline_preview()
    
    def slider_scale_cb(self, val):
        self.settings['wm_scale'] = val
        self.update_pipeline_preview()

    def slider_resize_cb(self, val):
        self.settings['resize_scale'] = val
        self.lbl_resize_txt.configure(text=f"{int(val)}%")
        self.update_pipeline_preview()

    def update_settings(self, _=None):
        if self.current_view == "watermark":
            self.settings['wm_enabled'] = bool(self.chk_wm.get())
        elif self.current_view == "resize":
            self.settings['resize_enabled'] = bool(self.chk_resize.get())
        elif self.current_view == "convert":
            self.settings['format'] = self.combo_fmt.get()
        self.update_pipeline_preview()

    def update_pipeline_preview(self):
        if not self.current_preview_path: return
        base = self.processor.load_image(self.current_preview_path)
        if not base: return
        processed = self.processor.process_pipeline(base, self.settings)
        preview = self.processor.get_preview(processed, max_size=(900, 700))
        if preview:
            ctk_img = ctk.CTkImage(preview, size=preview.size)
            self.preview_label.configure(image=ctk_img, text="")

    # --- Mouse & Manual Pos ---
    def on_pos_change(self, choice):
        self.settings['wm_pos'] = choice
        if choice == "manual": self.manual_ctrls.pack(fill="x", pady=10)
        else: self.manual_ctrls.pack_forget()
        self.update_pipeline_preview()

    def on_preview_click(self, event): self.handle_drag(event)
    def on_preview_drag(self, event): self.handle_drag(event)

    def handle_drag(self, event):
        if self.current_view == "watermark" and self.settings['wm_enabled'] and self.settings['wm_pos'] == "manual":
            w, h = self.preview_label.winfo_width(), self.preview_label.winfo_height()
            self.settings['wm_x'] = max(0, min(1, event.x / w))
            self.settings['wm_y'] = max(0, min(1, event.y / h))
            self.update_pipeline_preview()

    # --- Library ---
    def import_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.png *.jpeg *.webp")])
        for path in paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.add_gallery_item(path)
        if self.selected_files and not self.current_preview_path: self.load_preview(self.selected_files[0])
        if self.current_view == "home": self.change_view("home") 

    def add_gallery_item(self, path):
        img = self.processor.load_image(path)
        if img:
            thumb = self.processor.get_thumbnail(img)
            ctk_thumb = ctk.CTkImage(thumb, size=thumb.size)
            item = GalleryItem(self.filmstrip_frame, path, ctk_thumb, self.load_preview, self.remove_image)
            item.pack(side="left", padx=5)
            self.gallery_widgets[path] = item

    def remove_image(self, widget, path):
        if path in self.selected_files: self.selected_files.remove(path)
        widget.destroy()
        del self.gallery_widgets[path]
        if path == self.current_preview_path:
            self.current_preview_path = None
            self.preview_label.configure(image=None, text="Image Removed")
            if self.selected_files: self.load_preview(self.selected_files[0])
        if self.current_view == "home": self.change_view("home")

    def load_preview(self, path):
        self.current_preview_path = path
        for p, w in self.gallery_widgets.items(): w.set_selected(p == path)
        self.update_pipeline_preview()

    def clear_library(self):
        for w in self.gallery_widgets.values(): w.destroy()
        self.gallery_widgets.clear()
        self.selected_files.clear()
        self.current_preview_path = None
        self.preview_label.configure(image=None, text="Library Cleared")
        self.change_view("home")

    def upload_watermark(self):
        path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if path:
            self.settings['wm_path'] = path
            self.settings['wm_enabled'] = True
            if self.current_view == "watermark": self.change_view("watermark")
            self.update_pipeline_preview()

    def run_pipeline_export(self):
        if not self.selected_files: return
        save_dir = filedialog.askdirectory()
        if save_dir:
            count = self.processor.run_full_export(self.selected_files, save_dir, self.settings)
            messagebox.showinfo("Done", f"Exported {count} images!")
            self.change_view("history")

if __name__ == "__main__":
    app = ProImageStudio()
    app.mainloop()