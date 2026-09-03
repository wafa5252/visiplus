import streamlit as st
from database import get_session, init_db
from models import User, UserRole
from security import hash_password, verify_password, encrypt_field

st.set_page_config(
    page_title="VisiPulse - Predictive Governance",
    layout="wide",
)

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
    else:
        existing.password_hash = hash_password(pwd)
        session.add(existing)
session.commit()

st.markdown("""
    <style>
    .enterprise-banner {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e3a8a 100%);
        padding: 25px 35px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4);
        margin-bottom: 30px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .logo-box {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
        flex-shrink: 0;
    }
    .banner-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .portal-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 20px;
        border-radius: 10px;
        margin-top: 25px;
        color: #0f172a;
    }
    .portal-card h4 {
        margin-top: 0;
        color: #1e3a8a;
        font-size: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    .portal-card table {
        width: 100%;
        font-size: 14px;
        border-collapse: collapse;
    }
    .portal-card th, .portal-card td {
        padding: 8px;
        text-align: right;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
    
    <div class="enterprise-banner">
        <div class="logo-box">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
        </div>
        <div>
            <h1 class="banner-title">VisiPulse</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("تسجيل الدخول للنظام الاستباقي")
        
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
            <div class="portal-card">
                <h4>بيانات الدخول التجريبية للاختبار الفوري:</h4>
                <table>
                    <tr>
                        <th>النطاق والدور</th>
                        <th>اسم المستخدم</th>
                        <th>كلمة المرور</th>
                    </tr>
                    <tr>
                        <td>قسم تقنية المعلومات ووكلاء الذكاء الاصطناعي</td>
                        <td><code>it_admin</code></td>
                        <td><code>Admin@123</code></td>
                    </tr>
                    <tr>
                        <td>الإدارة العليا ومؤشرات الأداء الرئيسية</td>
                        <td><code>hospital_director</code></td>
                        <td><code>Director@123</code></td>
                    </tr>
                    <tr>
                        <td>بوابة الموظف والكشف الاستباقي</td>
                        <td><code>employee1</code></td>
                        <td><code>Emp@123</code></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
else:
    user = st.session_state.user
    st.sidebar.markdown(f"**المستخدم:** {user.full_name} ({user.role.value})")
    
    if user.role == UserRole.EMPLOYEE:
        st.markdown("### بوابة الموظف الاستباقية")
        st.info("رصد وكيل الذكاء الاصطناعي تنبيهاً استباقياً على الأجهزة والأصول المادية المرتبطة بك: (احتمالية ارتفاع حرارة الوحدة الطرفية / تراجع تدريجي في أداء النظام). تم توثيق التيكت وإرساله تلقائياً إلى قسم الدعم الفني.")
    elif user.role == UserRole.IT:
        st.markdown("### لوحة تحكم تقنية المعلومات والدعم الفني")
        st.write("إدارة البنية التحتية، أنظمة التطبيقات، ومتابعة البلاغات الواردة من وكلاء الذكاء الاصطناعي الاستباقيين.")
        
        st.markdown("---")
        st.subheader("إدارة التيكتات والصيانة الميدانية")
        selected_contractor = st.selectbox(
            "شركة المقاولات المسؤولة عن الصيانة الميدانية (مقترح آلياً حسب التعاقد):",
            ["شركة الأصول الطبية المتقدمة", "مؤسسة التقنية السريعة للصيانة", "شركة التوريدات الرقمية الصحية"]
        )
        st.text_area("تقرير معالجة البلاغ الفني:", value=f"تم إسناد التيكت إلى {selected_contractor} لمباشرة الصيانة الاستباقية.")
        if st.button("اعتماد وإرسال بلاغ الصيانة"):
            st.success("تم إرسال البلاغ لشركة المقاولة المعتمدة بنجاح.")
            
    elif user.role == UserRole.EXECUTIVE:
        st.markdown("### لوحة مؤشرات الأداء الرئيسية واتخاذ القرار")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("الأعطال الاستباقية المتلافاة", "18 عطل", "-4 مقارنة بالفترة السابقة")
        col_m2.metric("كفاءة البنية التحتية", "98.4%", "+1.2%")
        col_m3.metric("معدل استجابة شركات المقاولة", "24 دقيقة", "مستوى معتمد")
        
        st.markdown("---")
        st.markdown("#### التحليلات الاستراتيجية لحوكمة البيانات")
        st.write("تقارير وكلاء الذكاء الاصطناعي تدعم الإدارة العليا في اتخاذ قرارات الميزانية، توجيه عقود الصيانة، ومراقبة مؤشرات جودة الخدمات الصحية الرقمية.")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
