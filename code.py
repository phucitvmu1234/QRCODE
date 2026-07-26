import io
import json
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Tạo Mã QR Custom", page_icon="📱")

st.title("📱 Tạo Mã QR Custom & Gắn Logo")

# 1. Nhập liệu
link = st.text_input("Đường dẫn (Link / Text):", "https://example.com")
uploaded_logo = st.file_uploader(
    "Chọn Logo (PNG, JPG, WEBP):", type=["png", "jpg", "jpeg", "webp"]
)

qr_color = (0, 150, 160)  # Teal

if st.button("TẠO MÃ QR", type="primary"):
    if not link.strip():
        st.warning("Vui lòng nhập link!")
    else:
        # Tạo QR
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=3,
        )
        qr.add_data(link.strip())
        qr.make(fit=True)

        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer(),
            color_mask=SolidFillColorMask(
                back_color=(255, 255, 255), front_color=qr_color
            ),
        ).convert("RGBA")

        # Chèn logo nếu có upload
        if uploaded_logo is not None:
            logo = Image.open(uploaded_logo).convert("RGBA")
            qr_w, qr_h = qr_img.size
            logo_max_size = int(qr_w * 0.30)
            logo.thumbnail(
                (logo_max_size, logo_max_size), Image.Resampling.LANCZOS
            )

            logo_w, logo_h = logo.size
            pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
            qr_img.paste(logo, pos, mask=logo)

        # Lưu ảnh vào bộ nhớ tạm để hiển thị & cho tải xuống
        img_byte_arr = io.BytesIO()
        qr_img.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()

        st.subheader("Xem trước mã QR:")
        st.image(img_bytes, width=250)

        # Nút Tải xuống trên web
        st.download_button(
            label="💾 TẢI MÃ QR XUỐNG",
            data=img_bytes,
            file_name="qrcode.png",
            mime="image/png",
        )
