import io
import json
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
from PIL import Image
import streamlit as st

# File cấu hình để ghi nhớ logo trên server
CONFIG_FILE = "config_qr.json"
SAVED_LOGO_PATH = "saved_logo.png"

st.set_page_config(
    page_title="Tạo Mã QR Custom & Gắn Logo", page_icon="📱", layout="centered"
)


# --- HÀM HỖ TRỢ LƯU / ĐỌC LOGO ---
def load_saved_logo():
    """Đọc logo đã lưu từ lần trước nếu có"""
    if os.path.exists(CONFIG_FILE) and os.path.exists(SAVED_LOGO_PATH):
        try:
            return Image.open(SAVED_LOGO_PATH).convert("RGBA")
        except Exception:
            return None
    return None


def save_logo_to_disk(uploaded_file):
    """Lưu file logo mới tải lên vào ổ đĩa server"""
    try:
        image = Image.open(uploaded_file).convert("RGBA")
        image.save(SAVED_LOGO_PATH, format="PNG")
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"default_logo": SAVED_LOGO_PATH},
                f,
                ensure_ascii=False,
                indent=4,
            )
        return image
    except Exception as e:
        st.error(f"Không thể lưu logo: {e}")
        return None


# --- GIAO DIỆN CHÍNH ---
st.title("📱 Tạo Mã QR Custom & Gắn Logo")
st.write("Ứng dụng tạo mã QR nghệ thuật với chấm tròn, màu sắc và logo custom.")

st.markdown("---")

# Section 1: Thông tin đầu vào
st.subheader("1. Thông tin đầu vào")

link_input = st.text_input(
    "Đường dẫn (Link / Text):",
    value="https://example.com",
    placeholder="Nhập link hoặc văn bản cần tạo QR...",
)

# Xử lý upload và lưu trữ Logo
uploaded_logo = st.file_uploader(
    "Chọn Logo (Tự động ghi nhớ cho lần sau):",
    type=["png", "jpg", "jpeg", "webp"],
)

logo_img = None
if uploaded_logo is not None:
    # Nếu người dùng upload file mới, lưu lại vào server
    logo_img = save_logo_to_disk(uploaded_logo)
    st.success("Đã nạp và ghi nhớ logo mới!")
else:
    # Nếu không upload file mới, thử nạp lại logo đã nhớ từ trước
    logo_img = load_saved_logo()
    if logo_img:
        st.info("Đã tự động tải logo từ lần sử dụng trước.")

# Cấu hình kích thước tải về
target_size = st.number_input(
    "Kích thước mã QR xuất ra (px):",
    min_value=300,
    max_value=4000,
    value=800,
    step=100,
)

st.markdown("---")

# Section 2 & 3: Tạo và Tải xuống
st.subheader("2. Xem trước & Tải xuống")

# Khởi tạo màu QR (Màu xanh ngọc Teal: RGB 0, 150, 160)
qr_color = (0, 150, 160)

if st.button("TẠO MÃ QR", type="primary", use_container_width=True):
    if not link_input.strip():
        st.warning("Vui lòng nhập đường dẫn/văn bản!")
    else:
        try:
            # Tạo QR Code cơ bản
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=3,
            )
            qr.add_data(link_input.strip())
            qr.make(fit=True)

            # Vẽ style chấm tròn + màu xanh Teal
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=(255, 255, 255), front_color=qr_color
                ),
            ).convert("RGBA")

            # Ghép logo ở giữa nếu có
            if logo_img:
                qr_w, qr_h = qr_img.size
                logo_max_size = int(qr_w * 0.22)

                # Copy logo để tránh làm biến dạng bản gốc
                logo_temp = logo_img.copy()
                logo_temp.thumbnail(
                    (logo_max_size, logo_max_size), Image.Resampling.LANCZOS
                )

                logo_w, logo_h = logo_temp.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

                qr_img.paste(logo_temp, pos, mask=logo_temp)

            # Resize ảnh theo kích thước người dùng yêu cầu
            final_img = qr_img.resize(
                (int(target_size), int(target_size)), Image.Resampling.LANCZOS
            )

            # Đưa ảnh vào bộ nhớ tạm để hiển thị và tạo nút download
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Hiển thị xem trước
            st.image(
                byte_im, caption=f"Mã QR ({target_size}x{target_size} px)"
            )

            # Nút Tải xuống
            st.download_button(
                label="💾 LƯU / TẢI MÃ QR XUỐNG",
                data=byte_im,
                file_name="qrcode_custom.png",
                mime="image/png",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo mã QR: {e}")
