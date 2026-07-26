import base64
import io
from PIL import Image
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
import streamlit as st
import streamlit.components.v1 as components

# 1. Cấu hình trang chuẩn Dashboard
st.set_page_config(
    page_title="QR Code Studio Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom CSS để làm đẹp giao diện
CUSTOM_CSS = """
<style>
    /* Gradient Title */
    .main-title {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #0096a0 0%, #0056b3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    /* Card Container */
    .custom-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    /* Style cho status text */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #e6f4ea;
        color: #137333;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SIDEBAR: CẤU HÌNH & THÔNG TIN ---
with st.sidebar:
    st.image(
        "https://cdn-icons-png.flaticon.com/512/714/714390.png", width=60
    )
    st.title("⚙️ Cấu hình QR")
    st.caption("Tùy chỉnh thông số mã QR của bạn")

    st.markdown("---")

    # Nhập đường dẫn
    link = st.text_input(
        "🔗 Nội dung / Link URL",
        value="https://example.com",
        placeholder="https://yourwebsite.com",
    )

    # Chọn Logo
    uploaded_logo = st.file_uploader(
        "🖼️ Logo chèn ở giữa (Tùy chọn)", type=["png", "jpg", "jpeg", "webp"]
    )

    # Tùy chỉnh màu sắc & Kích thước
    col_color, col_bg = st.columns(2)
    with col_color:
        hex_color = st.color_picker("🎨 Màu QR", "#0096a0")
    with col_bg:
        bg_hex_color = st.color_picker("🔲 Màu nền", "#FFFFFF")

    download_size = st.select_slider(
        "📐 Kích thước xuất file (px)",
        options=[300, 500, 800, 1000, 1200, 2000, 4000],
        value=800,
    )

    # Convert HEX sang RGB
    hex_clean = hex_color.lstrip("#")
    qr_rgb = tuple(int(hex_clean[i : i + 2], 16) for i in (0, 2, 4))

    bg_hex_clean = bg_hex_color.lstrip("#")
    bg_rgb = tuple(int(bg_hex_clean[i : i + 2], 16) for i in (0, 2, 4))

    st.markdown("---")
    btn_generate = st.button(
        "✨ TẠO MÃ QR NGAY", type="primary", use_container_width=True
    )


# --- MAIN CONTENT: HIỂN THỊ KẾT QUẢ ---
st.markdown(
    '<div class="main-title">QR Code Studio Pro</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Công cụ tạo mã QR nghệ thuật chất lượng cao, tích hợp logo thương hiệu</div>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1.2, 1], gap="large")

# Tự động tạo lần đầu hoặc khi bấm nút
if btn_generate or "qr_bytes" not in st.session_state:
    if not link.strip():
        st.warning("⚠️ Vui lòng nhập thông tin link/văn bản ở cột bên trái!")
    else:
        try:
            # Tạo QR Code
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

            # Xử lý chèn Logo
            if uploaded_logo is not None:
                logo = Image.open(uploaded_logo).convert("RGBA")
                qr_w, qr_h = qr_img.size

                logo_max_size = int(qr_w * 0.24)
                logo.thumbnail(
                    (logo_max_size, logo_max_size), Image.Resampling.LANCZOS
                )

                logo_w, logo_h = logo.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
                qr_img.paste(logo, pos, mask=logo)

            # Resize ảnh theo yêu cầu
            final_img = qr_img.resize(
                (download_size, download_size), Image.Resampling.LANCZOS
            )

            # Lưu vào bộ nhớ tạm
            img_byte_arr = io.BytesIO()
            final_img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            st.session_state["qr_bytes"] = img_bytes
            st.session_state["qr_b64"] = base64.b64encode(img_bytes).decode(
                "utf-8"
            )

        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo mã QR: {str(e)}")

# Khung hiển thị kết quả
with col_left:
    st.markdown("### 🖼️ Xem trước kết quả")
    if "qr_bytes" in st.session_state:
        st.image(
            st.session_state["qr_bytes"],
            use_container_width=True,
            caption=f"Kích thước xem trước ({download_size}x{download_size}px)",
        )

with col_right:
    st.markdown("### 🚀 Xuất file & Chia sẻ")
    st.markdown(
        '<span class="status-badge">✓ Sẵn sàng tải xuống</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    if "qr_bytes" in st.session_state:
        # 1. Nút Tải xuống
        st.download_button(
            label="💾 TẢI MÃ QR XUỐNG (PNG)",
            data=st.session_state["qr_bytes"],
            file_name="qr_code_studio.png",
            mime="image/png",
            type="primary",
            use_container_width=True,
        )

        st.write("")

        # 2. Nút Copy với Giao diện JS hiện đại
        b64_str = st.session_state["qr_b64"]
        copy_code_html = f"""
        <div style="font-family: sans-serif;">
            <button id="copyBtn" onclick="copyImageToClipboard()" style="
                width: 100%;
                background: linear-gradient(135deg, #17a2b8 0%, #117a8b 100%);
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 15px;
                box-shadow: 0 4px 10px rgba(23, 162, 184, 0.3);
                transition: all 0.2s ease;
            ">📋 COPY ẢNH VÀO CLIPBOARD</button>

            <p id="msg" style="
                text-align: center;
                font-weight: 600;
                font-size: 13px;
                margin-top: 8px;
                min-height: 20px;
            "></p>
        </div>

        <script>
        async function copyImageToClipboard() {{
            const msgEl = document.getElementById('msg');
            const btn = document.getElementById('copyBtn');
            msgEl.style.color = "#0096a0";
            msgEl.innerText = "⏳ Đang copy...";
            
            try {{
                const base64Data = 'data:image/png;base64,{b64_str}';
                const response = await fetch(base64Data);
                const blob = await response.blob();

                await navigator.clipboard.write([
                    new ClipboardItem({{ 'image/png': blob }})
                ]);

                msgEl.style.color = "#28a745";
                msgEl.innerText = "✅ Đã copy ảnh vào bộ nhớ tạm!";
                setTimeout(() => {{ msgEl.innerText = ""; }}, 3000);
            }} catch (err) {{
                console.error(err);
                msgEl.style.color = "#dc3545";
                msgEl.innerText = "❌ Trình duyệt chặn quyền copy tự động!";
            }}
        }}
        </script>
        """
        components.html(copy_code_html, height=100)

        # Khung thông tin kỹ thuật
        with st.expander("ℹ️ Thông số chi tiết"):
            st.write(f"• **Mức sửa lỗi:** High (30%)")
            st.write(f"• **Màu mắt QR:** `{hex_color}`")
            st.write(f"• **Định dạng xuất:** PNG Transparent Ready")
