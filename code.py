import base64
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Tạo Mã QR Custom",
    page_icon="📱",
    layout="centered"
)

st.title("📱 Tạo Mã QR Custom & Gắn Logo")
st.write("Tạo mã QR nghệ thuật, chèn logo, copy hoặc tải xuống chất lượng cao.")

st.divider()

# --- 1. THÔNG TIN ĐẦU VÀO ---
st.subheader("1. Thông tin đầu vào")

link = st.text_input(
    "Đường dẫn (Link / Text):", 
    value="https://example.com",
    placeholder="Nhập URL hoặc văn bản tại đây..."
)

uploaded_logo = st.file_uploader(
    "Chọn Logo chèn vào giữa (tùy chọn):", 
    type=["png", "jpg", "jpeg", "webp"]
)

# Tùy chỉnh màu mã QR và Kích thước
col_color, col_size = st.columns(2)
with col_color:
    hex_color = st.color_picker("Chọn màu mã QR:", "#0096a0")
    hex_color_clean = hex_color.lstrip("#")
    qr_rgb = tuple(int(hex_color_clean[i:i+2], 16) for i in (0, 2, 4))

with col_size:
    download_size = st.number_input(
        "Kích thước xuất file (px):", 
        min_value=300, 
        max_value=4000, 
        value=800, 
        step=100
    )

st.divider()

# --- 2. XỬ LÝ & HIỂN THỊ ---
if st.button("✨ TẠO MÃ QR", type="primary", use_container_width=True):
    if not link.strip():
        st.warning("⚠️ Vui lòng nhập thông tin đường dẫn/văn bản!")
    else:
        try:
            # Khởi tạo QR với mức sửa lỗi cao (ERROR_CORRECT_H)
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=3,
            )
            qr.add_data(link.strip())
            qr.make(fit=True)

            # Tạo hình ảnh QR với mắt tròn và màu tùy chỉnh
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=(255, 255, 255), 
                    front_color=qr_rgb
                ),
            ).convert("RGBA")

            # Nếu có upload logo thì chèn vào
            if uploaded_logo is not None:
                logo = Image.open(uploaded_logo).convert("RGBA")
                qr_w, qr_h = qr_img.size
                
                # Giới hạn kích thước logo 25% QR
                logo_max_size = int(qr_w * 0.25)
                logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

                logo_w, logo_h = logo.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
                qr_img.paste(logo, pos, mask=logo)

            # Resize theo kích thước yêu cầu
            final_img = qr_img.resize((download_size, download_size), Image.Resampling.LANCZOS)

            # Chuyển ảnh sang dạng Bytes
            img_byte_arr = io.BytesIO()
            final_img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            # Lưu vào session_state
            st.session_state['qr_bytes'] = img_bytes
            # Tạo chuỗi Base64 để truyền vào JavaScript Copy
            st.session_state['qr_b64'] = base64.b64encode(img_bytes).decode('utf-8')
            
            st.success("Tạo mã QR thành công!")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo QR: {str(e)}")

# --- 3. XUẤT KẾT QUẢ & CÁC NÚT THAO TÁC ---
if 'qr_bytes' in st.session_state:
    st.subheader("2. Xem trước & Xuất file")
    
    col_preview, col_btn = st.columns([1, 1])
    
    with col_preview:
        st.image(st.session_state['qr_bytes'], caption="Mã QR của bạn", width=220)
        
    with col_btn:
        st.write("### Tùy chọn:")
        
        # 1. Nút Tải xuống
        st.download_button(
            label="💾 TẢI MÃ QR XUỐNG",
            data=st.session_state['qr_bytes'],
            file_name="custom_qrcode.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
        
        # 2. Nút Copy bằng JavaScript (Chạy mượt trên Web/Trình duyệt)
        b64_str = st.session_state['qr_b64']
        copy_code_html = f"""
        <button id="copyBtn" onclick="copyImageToClipboard()" style="
            width: 100%;
            background-color: #17a2b8;
            color: white;
            padding: 10px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 5px;
        ">📋 COPY ẢNH VÀO CLIPBOARD</button>

        <p id="msg" style="color: green; font-weight: bold; font-size: 13px; margin-top: 5px;"></p>

        <script>
        async function copyImageToClipboard() {{
            const msgEl = document.getElementById('msg');
            msgEl.innerText = "Đang copy...";
            try {{
                const base64Data = 'data:image/png;base64,{b64_str}';
                const response = await fetch(base64Data);
                const blob = await response.blob();

                await navigator.clipboard.write([
                    new ClipboardItem({{ 'image/png': blob }})
                ]);

                msgEl.innerText = "✅ Đã copy ảnh QR thành công!";
                setTimeout(() => {{ msgEl.innerText = ""; }}, 3000);
            }} catch (err) {{
                console.error(err);
                msgEl.style.color = "red";
                msgEl.innerText = "❌ Trình duyệt không cho phép copy tự động!";
            }}
        }}
        </script>
        """
        components.html(copy_code_html, height=90)
