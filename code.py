import io
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer

CONFIG_FILE = "config_qr.json"


class QRCodeGeneratorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Tạo Mã QR Custom & Gắn Logo")
        self.root.geometry("520x680")
        self.root.minsize(450, 500)  # Cho phép co giãn thoải mái
        self.root.resizable(True, True)

        self.generated_qr_img = None
        self.qr_color = (0, 150, 160)  # RGB Xanh ngọc Teal

        # --- Tạo Canvas & Scrollbar để giao diện không bao giờ bị đè tràn ---
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.root, orient="vertical", command=self.main_canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            ),
        )

        self.canvas_window = self.main_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfig(
                self.canvas_window, width=e.width
            ),
        )

        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Đổ giao diện vào scrollable_frame
        self._build_ui()
        self._load_saved_logo()

    def _build_ui(self):
        # 1. Frame Nhập dữ liệu
        frame_inputs = tk.LabelFrame(
            self.scrollable_frame, text=" 1. Thông tin đầu vào ", padx=15, pady=10
        )
        frame_inputs.pack(fill="x", padx=15, pady=8)

        tk.Label(frame_inputs, text="Đường dẫn (Link / Text):").pack(anchor="w")
        self.entry_link = tk.Entry(frame_inputs, width=50)
        self.entry_link.pack(fill="x", pady=(2, 8))
        self.entry_link.insert(0, "https://example.com")

        tk.Label(
            frame_inputs, text="Chọn Logo (Sẽ tự động nhớ cho lần sau):"
        ).pack(anchor="w")
        frame_logo_select = tk.Frame(frame_inputs)
        frame_logo_select.pack(fill="x", pady=(2, 8))

        self.entry_logo = tk.Entry(frame_logo_select, width=35)
        self.entry_logo.pack(side="left", fill="x", expand=True)

        btn_browse = tk.Button(
            frame_logo_select, text="Chọn ảnh...", command=self.browse_logo
        )
        btn_browse.pack(side="right", padx=(5, 0))

        btn_generate = tk.Button(
            frame_inputs,
            text="TẠO MÃ QR",
            bg="#0096a0",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.generate_qr,
        )
        btn_generate.pack(fill="x", pady=(5, 0))

        # 2. Frame Hiển thị QR (Thu nhỏ xem trước vừa vặn)
        frame_preview = tk.LabelFrame(
            self.scrollable_frame, text=" 2. Xem trước mã QR ", padx=10, pady=10
        )
        frame_preview.pack(fill="x", padx=15, pady=5)

        self.lbl_preview = tk.Label(
            frame_preview, text="Chưa tạo QR", bg="#f0f0f0", height=10
        )
        self.lbl_preview.pack(fill="x", expand=True)

        # 3. Frame Xuất mã QR (Luôn hiển thị rõ ràng)
        frame_download = tk.LabelFrame(
            self.scrollable_frame, text=" 3. Xuất mã QR ", padx=15, pady=10
        )
        frame_download.pack(fill="x", padx=15, pady=8)

        frame_size = tk.Frame(frame_download)
        frame_size.pack(fill="x", pady=(0, 10))

        tk.Label(frame_size, text="Kích thước xuất (px):").pack(side="left")
        self.spin_size = tk.Spinbox(
            frame_size, from_=300, to=4000, increment=100, width=8
        )
        self.spin_size.pack(side="left", padx=10)
        self.spin_size.delete(0, "end")
        self.spin_size.insert(0, "800")

        # Khung 2 nút thao tác
        frame_btns = tk.Frame(frame_download)
        frame_btns.pack(fill="x")

        btn_copy = tk.Button(
            frame_btns,
            text="📋 COPY ẢNH",
            bg="#17a2b8",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.copy_qr_to_clipboard,
        )
        btn_copy.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_download = tk.Button(
            frame_btns,
            text="💾 TẢI XUỐNG",
            bg="#28a745",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.download_qr,
        )
        btn_download.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def browse_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if file_path:
            self.entry_logo.delete(0, tk.END)
            self.entry_logo.insert(0, file_path)
            self.save_logo_path(file_path)

    def save_logo_path(self, path):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"default_logo": path}, f, ensure_ascii=False, indent=4
                )
        except Exception as e:
            print("Không thể lưu cấu hình logo:", e)

    def _load_saved_logo(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saved_path = data.get("default_logo", "")
                    if saved_path and os.path.exists(saved_path):
                        self.entry_logo.delete(0, tk.END)
                        self.entry_logo.insert(0, saved_path)
            except Exception as e:
                print("Không thể nạp logo đã lưu:", e)

    def generate_qr(self):
        link = self.entry_link.get().strip()
        if not link:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập link!")
            return

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=3,
        )
        qr.add_data(link)
        qr.make(fit=True)

        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer(),
            color_mask=SolidFillColorMask(
                back_color=(255, 255, 255), front_color=self.qr_color
            ),
        ).convert("RGBA")

        logo_path = self.entry_logo.get().strip()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA")
                self.save_logo_path(logo_path)

                qr_w, qr_h = qr_img.size
                logo_max_size = int(qr_w * 0.30)
                logo.thumbnail(
                    (logo_max_size, logo_max_size), Image.Resampling.LANCZOS
                )

                logo_w, logo_h = logo.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

                qr_img.paste(logo, pos, mask=logo)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể chèn logo: {str(e)}")

        self.generated_qr_img = qr_img

        # Thu nhỏ ảnh preview lại gọn gàng (200x200)
        preview_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(preview_img)
        self.lbl_preview.config(image=tk_img, text="", height=210)
        self.lbl_preview.image = tk_img

    def copy_qr_to_clipboard(self):
        if self.generated_qr_img is None:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng bấm 'TẠO MÃ QR' trước khi copy!"
            )
            return

        try:
            target_size = int(self.spin_size.get())
            final_img = self.generated_qr_img.resize(
                (target_size, target_size), Image.Resampling.LANCZOS
            )

            if sys.platform == "win32":
                output = io.BytesIO()
                final_img.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()

                import win32clipboard

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                messagebox.showinfo(
                    "Thành công", "Đã copy ảnh QR vào bộ nhớ tạm (Clipboard)!"
                )
            else:
                messagebox.showwarning(
                    "Thông báo", "Tính năng Copy hỗ trợ tốt nhất trên Windows."
                )

        except Exception as e:
            messagebox.showerror(
                "Lỗi", f"Không thể copy ảnh (Thử chạy: pip install pywin32)\n{str(e)}"
            )

    def download_qr(self):
        if self.generated_qr_img is None:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng bấm 'TẠO MÃ QR' trước khi tải xuống!"
            )
            return

        try:
            target_size = int(self.spin_size.get())
        except ValueError:
            messagebox.showerror(
                "Lỗi", "Kích thước nhập vào phải là số nguyên!"
            )
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
            title="Chọn nơi lưu mã QR",
        )

        if save_path:
            final_img = self.generated_qr_img.resize(
                (target_size, target_size), Image.Resampling.LANCZOS
            )
            final_img.save(save_path)
            messagebox.showinfo("Thành công", f"Đã lưu mã QR tại:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()
