import streamlit as st
from database import get_session, init_db
from models import User, UserRole
from security import hash_password, verify_password, encrypt_field

st.set_page_config(
    page_title="VisiPulse Healthcare Governance",
    layout="wide",
)

# تهيئة قاعدة البيانات وإنشاء الحسابات الثابتة تلقائياً للتجربة الفورية
init_db()
session = get_session()
default_users = [
    ("it_admin", "مدير تقنية المعلومات", UserRole.IT, "تقنية المعلومات", "Admin@123"),
    ("hospital_director", "مدير المستشفى", UserRole.EXECUTIVE, "الإدارة العليا", "Director@123"),
    ("employee1", "موظف تجريبي", UserRole.EMPLOYEE, "قسم الطوارئ", "Emp@123")
]

for uname, fname, role, dept, pwd in default_users:
    existing = session.query(User).filter(User.username == uname).first()
    if not existing:
        u = User(
            username=uname,
            full_name=fname,
            role=role,
            department=dept,
            password_hash=hash_password(pwd),
            must_change_password=False,
            email_enc=encrypt_field(f"{uname}@hospital.local"),
            phone_enc=encrypt_field("0500000000"),
        )
        session.add(u)
session.commit()

# تصميم الهيدر الاحترافي (Medical Enterprise UI)
st.markdown("""
    <style>
    .enterprise-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%);
        padding: 30px 40px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .brand-container {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .pulse-logo {
        width: 55px;
        height: 55px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .brand-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .brand-subtitle {
        font-size: 14px;
        color: #93c5fd;
        margin: 5px 0 0 0;
        font-weight: 400;
    }
    .credentials-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 20px;
        border-radius: 10px;
        margin-top: 25px;
        color: #0f172a;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .credentials-card h4 {
        margin-top: 0;
        color: #1e3a8a;
        font-size: 16px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    .credentials-card table {
        width: 100%;
        font-size: 14px;
        border-collapse: collapse;
    }
    .credentials-card th, .credentials-card td {
        padding: 8px;
        text-align: right;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
    
    <div class="enterprise-header">
        <div class="brand-container">
            <div class="pulse-logo">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
            </div>
            <div>
                <h1 class="brand-title">VisiPulse Healthcare Governance</h1>
                <p class="brand-subtitle">نظام حوكمة الرعاية الصحية المتقدم - إدارة الأصول والعمليات الطبية الذكية</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("تسجيل الدخول للنظام")
        
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول", use_container_width=True):
            user = session.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password_hash):
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        st.markdown("""
            <div class="credentials-card">
                <h4>بيانات الدخول التجريبية (للاختبار السريع):</h4>
                <table>
                    <tr>
                        <th>الدور</th>
                        <th>اسم المستخدم</th>
                        <th>كلمة المرور</th>
                    </tr>
                    <tr>
                        <td>مدير تقنية المعلومات</td>
                        <td><code>it_admin</code></td>
                        <td><code>Admin@123</code></td>
                    </tr>
                    <tr>
                        <td>مدير المستشفى</td>
                        <td><code>hospital_director</code></td>
                        <td><code>Director@123</code></td>
                    </tr>
                    <tr>
                        <td>موظف تجريبي</td>
                        <td><code>employee1</code></td>
                        <td><code>Emp@123</code></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
else:
    user = st.session_state.user
    st.sidebar.success(f"مرحباً بك، {user.full_name} ({user.role.value})")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    st.info("أهلاً بك في لوحة تحكم النظام الأساسية. يمكنك الانتقال عبر الأقسام الطبية المتاحة.")
