import base64
import io
from PIL import Image
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang
st.set_page_config(
    page_title="Tạo Mã QR Custom", page_icon="📱", layout="centered"
)

# CSS thu gọn giao diện, không cho ảnh phình to
CUSTOM_CSS = """
<style>
    /* Bóp nhỏ gọn toàn bộ trang */
    .block-container {
        max-width: 550px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    /* Khóa kích thước ảnh QR vừa vặn */
    [data-testid="stImage"] img {
        max-width: 220px !important;
        margin: 0 auto;
        display: block;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("📱 Tạo Mã QR Custom - Phúc Nguyễn")

# --- 1. NHẬP LIỆU ---
link = st.text_input(
    "Đường dẫn (Link / Text):",
    value="https://example.com",
    placeholder="Nhập link tại đây...",
)

uploaded_logo = st.file_uploader(
    "Chọn Logo (Tùy chọn):", type=["png", "jpg", "jpeg", "webp"]
)

col1, col2, col3 = st.columns([1, 1, 1.5])
with col1:
    hex_color = st.color_picker("Màu QR", "#0096a0")
with col2:
    bg_hex_color = st.color_picker("Màu nền", "#FFFFFF")
with col3:
    download_size = st.number_input(
        "Kích thước xuất (px)", min_value=300, max_value=4000, value=800
    )

# Chuyển Hex sang RGB
hex_clean = hex_color.lstrip("#")
qr_rgb = tuple(int(hex_clean[i : i + 2], 16) for i in (0, 2, 4))
bg_clean = bg_hex_color.lstrip("#")
bg_rgb = tuple(int(bg_clean[i : i + 2], 16) for i in (0, 2, 4))

st.write("")
btn_generate = st.button("✨ TẠO MÃ QR", type="primary", use_container_width=True)

# --- 2. XỬ LÝ VÀ HIỂN THỊ TẤT CẢ TRÊN 1 TRANG ---
if btn_generate or "qr_bytes" not in st.session_state:
    if link.strip():
        try:
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
                    back_color=bg_rgb, front_color=qr_rgb
                ),
            ).convert("RGBA")

            if uploaded_logo is not None:
                logo = Image.open(uploaded_logo).convert("RGBA")
                qr_w, qr_h = qr_img.size
                logo_max_size = int(qr_w * 0.25)
                logo.thumbnail(
                    (logo_max_size, logo_max_size), Image.Resampling.LANCZOS
                )
                logo_w, logo_h = logo.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
                qr_img.paste(logo, pos, mask=logo)

            final_img = qr_img.resize(
                (download_size, download_size), Image.Resampling.LANCZOS
            )

            img_byte_arr = io.BytesIO()
            final_img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            st.session_state["qr_bytes"] = img_bytes
            st.session_state["qr_b64"] = base64.b64encode(img_bytes).decode(
                "utf-8"
            )
        except Exception as e:
            st.error(f"Lỗi: {str(e)}")

# --- 3. KẾT QUẢ VÀ NÚT BẤM CÙNG 1 KHUNG ---
if "qr_bytes" in st.session_state:
    st.divider()

    # Hiển thị ảnh QR căn giữa, kích thước nhỏ gọn
    st.image(st.session_state["qr_bytes"])

    st.write("")

    # 2 Nút thao tác nằm ngang song song nhau
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        st.download_button(
            label="💾 TẢI MÃ QR XUỐNG",
            data=st.session_state["qr_bytes"],
            file_name="qrcode.png",
            mime="image/png",
            type="primary",
            use_container_width=True,
        )

    with btn_col2:
        b64_str = st.session_state["qr_b64"]
        copy_code_html = f"""
        <button id="copyBtn" onclick="copyImageToClipboard()" style="
            width: 100%;
            background-color: #17a2b8;
            color: white;
            padding: 9px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        ">📋 COPY ẢNH</button>
        <p id="msg" style="text-align:center; font-weight:bold; font-size:12px; margin-top:4px; color:green;"></p>

        <script>
        async function copyImageToClipboard() {{
            const msgEl = document.getElementById('msg');
            msgEl.innerText = "Đang copy...";
            try {{
                const response = await fetch('data:image/png;base64,{b64_str}');
                const blob = await response.blob();
                await navigator.clipboard.write([ new ClipboardItem({{ 'image/png': blob }}) ]);
                msgEl.innerText = "✅ Đã copy!";
                setTimeout(() => {{ msgEl.innerText = ""; }}, 2500);
            }} catch (err) {{
                msgEl.style.color = "red";
                msgEl.innerText = "❌ Không hỗ trợ copy!";
            }}
        }}
        </script>
        """
        components.html(copy_code_html, height=70)
