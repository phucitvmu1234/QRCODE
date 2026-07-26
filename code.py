import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
from PIL import Image
import streamlit as st

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Tạo Mã QR Custom",
    page_icon="📱",
    layout="centered"
)

st.title("📱 Tạo Mã QR Custom & Gắn Logo")
st.write("Tạo mã QR nghệ thuật, chèn logo và tải xuống chất lượng cao.")

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

# Tùy chỉnh màu mã QR
col_color, col_size = st.columns(2)
with col_color:
    hex_color = st.color_picker("Chọn màu mã QR:", "#0096a0")
    # Chuyển HEX sang RGB
    hex_color_clean = hex_color.lstrip("#")
    qr_rgb = tuple(int(hex_color_clean[i:i+2], 16) for i in (0, 2, 4))

with col_size:
    download_size = st.number_input(
        "Kích thước tải về (px):", 
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
                
                # Giới hạn kích thước logo 25% QR để không bị lỗi quét
                logo_max_size = int(qr_w * 0.25)
                logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

                logo_w, logo_h = logo.size
                pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
                qr_img.paste(logo, pos, mask=logo)

            # Resize theo kích thước người dùng yêu cầu xuất file
            final_img = qr_img.resize((download_size, download_size), Image.Resampling.LANCZOS)

            # Chuyển ảnh sang dạng Bytes để Streamlit hiển thị & tải xuống
            img_byte_arr = io.BytesIO()
            final_img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            # Luân chuyển dữ liệu vào session_state để giữ trạng thái
            st.session_state['qr_bytes'] = img_bytes
            st.success("Tạo mã QR thành công!")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo QR: {str(e)}")

# --- 3. XUẤT KẾT QUẢ ---
if 'qr_bytes' in st.session_state:
    st.subheader("2. Xem trước & Tải xuống")
    
    col_preview, col_btn = st.columns([1, 1])
    
    with col_preview:
        st.image(st.session_state['qr_bytes'], caption="Mã QR của bạn", width=240)
        
    with col_btn:
        st.write("---")
        st.download_button(
            label="💾 TẢI MÃ QR XUỐNG (PNG)",
            data=st.session_state['qr_bytes'],
            file_name="custom_qrcode.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
