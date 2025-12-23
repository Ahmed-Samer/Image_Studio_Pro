from PIL import Image, ImageEnhance
import os
import json
from datetime import datetime

class HistoryManager:
    def __init__(self, log_file="history.json"):
        self.log_file = log_file
        self.load_history()

    def load_history(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def add_entry(self, operation, count, save_path):
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "count": count,
            "location": save_path
        }
        self.history.insert(0, entry)
        self.save_history()

    def save_history(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.history, f, indent=4)
            
    def get_history(self):
        return self.history

class ImageProcessor:
    def __init__(self):
        self.history_mgr = HistoryManager()

    def load_image(self, file_path):
        try:
            return Image.open(file_path)
        except:
            return None

    def get_thumbnail(self, pil_image, size=(100, 100)):
        try:
            thumb = pil_image.copy()
            thumb.thumbnail(size)
            return thumb
        except:
            return None

    def get_preview(self, pil_image, max_size=(800, 600)):
        try:
            preview = pil_image.copy()
            preview.thumbnail(max_size, Image.Resampling.LANCZOS)
            return preview
        except:
            return None

    # --- Core Operations (Stateless) ---

    def _apply_watermark(self, img, wm_path, pos_type, x_pct, y_pct, opacity, scale):
        try:
            watermark = Image.open(wm_path).convert("RGBA")
            base_w, base_h = img.size
            
            # Resize WM
            wm_w, wm_h = watermark.size
            aspect = wm_w / wm_h
            new_wm_w = int(base_w * scale)
            new_wm_h = int(new_wm_w / aspect)
            watermark = watermark.resize((new_wm_w, new_wm_h), Image.Resampling.LANCZOS)
            
            # Opacity
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            watermark.putalpha(alpha)

            # Position
            if pos_type == "manual":
                final_x = int((base_w * x_pct) - (new_wm_w / 2))
                final_y = int((base_h * y_pct) - (new_wm_h / 2))
            else:
                padding = int(base_w * 0.05)
                if pos_type == "center":
                    final_x, final_y = (base_w - new_wm_w)//2, (base_h - new_wm_h)//2
                elif pos_type == "top_left":
                    final_x, final_y = padding, padding
                elif pos_type == "top_right":
                    final_x, final_y = base_w - new_wm_w - padding, padding
                elif pos_type == "bottom_left":
                    final_x, final_y = padding, base_h - new_wm_h - padding
                elif pos_type == "bottom_right":
                    final_x, final_y = base_w - new_wm_w - padding, base_h - new_wm_h - padding
                else:
                    final_x, final_y = 0, 0

            final_img = img.convert("RGBA")
            final_img.paste(watermark, (final_x, final_y), watermark)
            return final_img.convert("RGB")
        except:
            return img

    def _resize(self, img, scale_percent):
        try:
            w, h = img.size
            new_w = int(w * (scale_percent / 100))
            new_h = int(h * (scale_percent / 100))
            return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        except:
            return img

    # --- Pipeline Processor (Combines everything) ---

    def process_pipeline(self, img, settings):
        """
        Applies all enabled effects in order: Watermark -> Resize
        Note: Conversion happens at save time.
        """
        processed_img = img
        
        # 1. Apply Watermark
        if settings.get('wm_enabled', False) and settings.get('wm_path'):
            processed_img = self._apply_watermark(
                processed_img,
                settings['wm_path'],
                settings.get('wm_pos', 'center'),
                settings.get('wm_x', 0.5),
                settings.get('wm_y', 0.5),
                settings.get('wm_opacity', 0.8),
                settings.get('wm_scale', 0.3)
            )
            
        # 2. Apply Resize
        if settings.get('resize_enabled', False):
            processed_img = self._resize(processed_img, settings.get('resize_scale', 100))
            
        return processed_img

    def run_full_export(self, files, save_dir, settings):
        count = 0
        for path in files:
            try:
                img = self.load_image(path)
                if not img: continue
                
                # Run Pipeline
                final_img = self.process_pipeline(img, settings)
                
                # 3. Apply Format Conversion (Logic is handled by save params)
                target_fmt = settings.get('format', 'JPG')
                
                # Determine Filename
                fname = os.path.basename(path)
                name_no_ext = os.path.splitext(fname)[0]
                out_name = f"Processed_{name_no_ext}.{target_fmt.lower()}"
                
                # Save
                save_path = os.path.join(save_dir, out_name)
                
                if target_fmt == "JPG" or target_fmt == "JPEG":
                    if final_img.mode == "RGBA":
                        final_img = final_img.convert("RGB")
                
                final_img.save(save_path, quality=95)
                count += 1
            except Exception as e:
                print(f"Error saving {path}: {e}")
                pass
        
        self.history_mgr.add_entry("Batch Export", count, save_dir)
        return count