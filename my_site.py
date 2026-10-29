import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
import numpy as np
from scipy.interpolate import griddata

# Настройка страницы
st.set_page_config(page_title="Topos Server", page_icon="🏔️", layout="wide")

# Заголовок
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🏔️ Topos Server</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Загрузка файла → Обработка моделью → Результат распознавания</h4>", unsafe_allow_html=True)
st.write("---")

# Боковая панель для загрузки
with st.sidebar:
    st.header("Загрузка данных")
    uploaded_file = st.file_uploader("Загрузите картинку топосъемки (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    # Левая колонка: исходник
    with col1:
        st.subheader("📄 Загруженный файл")
        image = Image.open(uploaded_file)
        st.image(image, caption='Исходная топосъемка', width="stretch")
        
    # Правая колонка: кнопка обработки
    with col2:
        st.subheader("🧠 Обработка моделью")
        st.write("Нажмите кнопку, чтобы модель проанализировала рельеф.")
        
        if st.button("🚀 Запустить анализ"):
            # Имитация обработки моделью (генерация координат)
            data = {
                'X': [10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50],
                'Y': [10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 30, 30, 30, 30, 30],
                'Z': [150.5, 152.1, 153.8, 152.5, 150.2, 154.0, 155.5, 157.2, 153.2, 151.0, 149.5, 151.2, 154.8, 155.1, 150.5]
            }
            df = pd.DataFrame(data)
            
            min_z = df['Z'].min()
            max_z = df['Z'].max()
            mean_z = df['Z'].mean()
            diff_z = max_z - min_z

            # Построение карты
            xi = np.linspace(df['X'].min(), df['X'].max(), 100)
            yi = np.linspace(df['Y'].min(), df['Y'].max(), 100)
            Xi, Yi = np.meshgrid(xi, yi)
            Zi = griddata((df['X'], df['Y']), df['Z'], (Xi, Yi), method='cubic')

            fig, ax = plt.subplots(figsize=(8, 5))
            contour_filled = ax.contourf(Xi, Yi, Zi, levels=20, cmap='terrain')
            fig.colorbar(contour_filled, label='Высота, м')
            contour_lines = ax.contour(Xi, Yi, Zi, levels=12, colors='black', linewidths=0.5)
            ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%1.1f')
            ax.scatter(df['X'], df['Y'], c='red', s=20, zorder=5)
            
            plt.savefig('heatmap.png', dpi=150, bbox_inches='tight')
            plt.close(fig)

            st.success("✅ Модель успешно обработала данные!")
            st.image('heatmap.png', width="stretch")

    # Блок статистики (Результат распознавания)
    st.write("---")
    st.subheader("📊 Результат распознавания рельефа")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Макс. высота", f"{max_z:.2f} м")
    m2.metric("Мин. высота", f"{min_z:.2f} м")
    m3.metric("Перепад", f"{diff_z:.2f} м")
    m4.metric("Средняя", f"{mean_z:.2f} м")

    # Генерация PDF
    img_path = "uploaded_image.png"
    image.save(img_path)

    pdf = FPDF()
    pdf.add_font("DejaVu", style="", fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    
    pdf.add_page()
    pdf.set_font("DejaVu", size=20)
    pdf.cell(200, 20, txt="СПРАВКА ПО ТОПОСЪЕМКЕ", ln=True, align='C')
    
    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 10, txt=f"Максимальная высота: {max_z:.2f} м", ln=True)
    pdf.cell(200, 10, txt=f"Минимальная высота: {min_z:.2f} м", ln=True)
    pdf.cell(200, 10, txt=f"Перепад высот: {diff_z:.2f} м", ln=True)
    pdf.cell(200, 10, txt=f"Средняя высота: {mean_z:.2f} м", ln=True)
    
    pdf.image('heatmap.png', x=15, y=60, w=180)

    pdf.add_page()
    pdf.cell(200, 10, txt="Исходный материал:", ln=True, align='C')
    pdf.image(img_path, x=15, y=30, w=180)

    pdf.output("Topos_Report.pdf")
    with open("Topos_Report.pdf", "rb") as f:
        st.download_button(
            label="⬇️ Скачать PDF-отчет",
            data=f,
            file_name="Topos_Report.pdf",
            mime="application/pdf"
        )