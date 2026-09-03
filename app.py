import streamlit as st
from database import get_session
from models import User
from security import verify_password

st.set_page_config(
    page_title="VisiPulse - نظام الرعاية الصحية الذكي",
    layout="wide",
)

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .cred-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        color: #1e293b;
    }
    </style>
    <div class="main-header">
        <h1>VisiPulse Healthcare Governance</h1>
        <p>نظام الرعاية الصحية والحوكمة الذكية - لوحة التحكم والتحكم بالأصول</p>
    </div>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

session = get_session()

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("تسجيل الدخول للنظام")
        
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول", use_container_width=True):
            user = session.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password_hash):
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("تم تسجيل الدخول بنجاح")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        st.markdown("""
            <div class="cred-box">
                <h4>بيانات الدخول التجريبية:</h4>
                <ul>
                    <li><b>مدير تقنية المعلومات:</b> <code>it_admin</code></li>
                    <li><b>مدير المستشفى:</b> <code>hospital_director</code></li>
                    <li><b>موظف تجريبي:</b> <code>employee1</code></li>
                </ul>
                <p><i>ملاحظة: تأكدي من تنفيذ سكربت التهيئة أو توليد كلمات المرور للتمكن من الدخول.</i></p>
            </div>
        """, unsafe_allow_html=True)
else:
    user = st.session_state.user
    st.sidebar.success(f"مرحباً بك، {user.full_name} ({user.role.value})")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    st.info("أهلاً بك في لوحة تحكم النظام الأساسية.")
