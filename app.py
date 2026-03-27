import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px

# ==========================================
# 1. ตั้งค่ากุญแจ (API KEY)
# ไปเอาที่ https://aistudio.google.com/
# ==========================================
GOOGLE_API_KEY = "AIzaSyC0zbK1xA2zLY-g3-FeIVBgl7HcBv4rpBs" 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
# ==========================================
# 2. ตั้งค่าหน้าตาเว็บ (UI)
# ==========================================
st.set_page_config(page_title="Thai Data AI Assistant", layout="wide")
st.title("📊 AI ช่วยวิเคราะห์ข้อมูล (เวอร์ชันภาษาไทย)")
st.write("อัปโหลดไฟล์ Excel/CSV แล้วพิมพ์ถามสิ่งที่อยากรู้ได้เลยครับ")

# ส่วนอัปโหลดไฟล์
uploaded_file = st.sidebar.file_uploader("📂 อัปโหลดไฟล์ของคุณที่นี่", type=['csv', 'xlsx'])

if uploaded_file:
    # อ่านข้อมูล
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("### 📋 ตัวอย่างข้อมูล 5 แถวแรก")
    st.dataframe(df.head())

    # ส่วนแชทถามข้อมูล
    st.divider()
    user_query = st.text_input("💬 อยากรู้อะไรจากข้อมูลชุดนี้? (เช่น ยอดขายรวมแยกตามสาขา, กราฟสินค้าที่ขายดีที่สุด 5 อันดับ)")

    if user_query:
        with st.spinner('AI กำลังคิดคำนวณให้สักครู่...'):
            # สร้างคำสั่ง (Prompt) ส่งให้ AI
            columns_info = ", ".join(df.columns.tolist())
            prompt = f"""
            คุณคือ Python Data Analyst ที่เก่งเรื่อง Pandas และ Plotly
            ข้อมูลที่มี: DataFrame ชื่อ 'df' มีคอลัมน์คือ: {columns_info}
            คำถามจากผู้ใช้: "{user_query}"
            
            คำแนะนำ:
            1. เขียน Code Python (Pandas) เพื่อหาคำตอบ
            2. ถ้าคำถามต้องการเปรียบเทียบหรือดูแนวโน้ม ให้วาดกราฟด้วย Plotly Express โดยเก็บไว้ในตัวแปร 'fig'
            3. ตอบกลับเฉพาะ Python Code เท่านั้น ห้ามมีคำบรรยายอื่นนอกเหนือจาก Code
            """

            # ส่งไปถาม Gemini
            response = model.generate_content(prompt)
            clean_code = response.text.replace('```python', '').replace('```', '').strip()

            try:
                # รันโค้ดที่ AI เจนมา
                # สร้างพื้นที่ปลอดภัย (Local namespace) ให้ Code รัน
                local_vars = {'df': df, 'pd': pd, 'px': px}
                exec(clean_code, globals(), local_vars)
                
                # แสดงผลลัพธ์ที่เป็นตัวเลข/ตาราง
                if 'result' in local_vars:
                    st.write("### ✅ คำตอบ:")
                    st.write(local_vars['result'])
                
                # แสดงกราฟ (ถ้ามี)
                if 'fig' in local_vars:
                    st.write("### 📈 กราฟวิเคราะห์:")
                    st.plotly_chart(local_vars['fig'])
                
                # แสดง Code ที่ AI เขียน (เพื่อความโปร่งใส)
                with st.expander("ดู Code ที่ AI ใช้คำนวณ"):
                    st.code(clean_code)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการรัน Code: {e}")
                st.info("ลองเปลี่ยนคำถามให้ชัดเจนขึ้นดูครับ")

else:
    st.info("💡 กรุณาอัปโหลดไฟล์ทางซ้ายมือก่อนเริ่มใช้งานนะครับ")

# ส่วน Footer
st.sidebar.divider()
st.sidebar.caption("สร้างโดย: เด็กอายุ 27 ที่อยากมี Tool ขาย 🚀")
