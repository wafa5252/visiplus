"""
VisiPulse - نظام الإنذار المبكر وحوكمة البنية التحتية للمنشآت الصحية
نقطة تشغيل التطبيق الرئيسية (Entry Point)

التشغيل:
    streamlit run app.py
"""
from datetime import datetime

import streamlit as st

from database import init_db, get_session
from models import User, UserRole, PasswordHistory
from security import (
    verify_password, hash_password, validate_password_policy,
    PASSWORD_HISTORY_COUNT, SESSION_IDLE_MINUTES,
)
from auth import attempt_login, check_session_timeout, touch_session, logout
from audit import log_action

# استدعاء وكلاء الذكاء الاصطناعي (AI Agents) لتفعيل التحليل التنبؤي والتشخيص الذكي
import agents 

from ui import it_portal, executive_portal, employee_portal


st.set_page_config(
    page_title="VisiPulse | نظام الإنذار المبكر وحوكمة البنية التحتية",
    page_icon="H",
    layout="wide",
)

_RTL_CSS = """
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
}
.stButton>button { direction: rtl; }
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] { direction: ltr; }
section[data-testid="stSidebar"] { direction: rtl; text-align: right; }
div[data-testid="stForm"] { direction: rtl; text-align: right; }

/* إزالة الحشو العلوي الافتراضي في ستريمليت لدمج الهيدر باحترافية */
.block-container {
    padding-top: 1.5rem !important;
}
</style>
"""
st.markdown(_RTL_CSS, unsafe_allow_html=True)

ROLE_LABELS = {"it": "تقنية المعلومات", "executive": "الإدارة العليا", "employee": "موظف"}

# تصميم الهيدر العلوي الممتد (مثل أنظمة المستشفيات الطبية الكبرى مثل +Oasis)
VISIPULSE_TOP_HEADER = """
<div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 16px 28px; border-radius: 12px; border-bottom: 3px solid #0284C7; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25); display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; direction: ltr;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <svg width="42" height="28" viewBox="0 0 100 50" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0 25 L 22 25 L 32 8 L 42 42 L 52 14 L 62 32 L 72 25 L 100 25" stroke="#10B981" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div style="font-size: 32px; font-weight: 800; font-family: system-ui, sans-serif; letter-spacing: 1px; line-height: 1;">
            <span style="color: #F8FAFC;">Visi</span><span style="color: #38BDF8;">Pulse</span>
        </div>
        <div style="width: 8px; height: 8px; background-color: #34D399; border-radius: 50%; box-shadow: 0 0 10px #34D399; margin-top: -14px;"></div>
    </div>
    <div style="font-size: 11px; font-weight: 600; color: #94A3B8; letter-spacing: 3px; text-transform: uppercase;">
        THE FLOW OF SMART HEALTHCARE
    </div>
</div>
"""


@st.cache_resource
def _bootstrap_db():
    init_db()
    return True


_bootstrap_db()


def _login_screen(session):
    # عرض الهيدر العلوي البارز في صفحة الدخول
    st.markdown(VISIPULSE_TOP_HEADER, unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<h3 style='text-align: center; color: #334155; margin-bottom: 20px;'>تسجيل الدخول للنظام</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submitted = st.form_submit_button("تسجيل الدخول", width="stretch")

        if submitted:
            user, result = attempt_login(session, username, password)
            if user is None:
                st.error(result)
            else:
                st.session_state.authenticated = True
                st.session_state.username = user.username
                st.session_state.user_id = user.id
                st.session_state.role = user.role.value
                st.session_state.must_change_password = bool(user.must_change_password or result == "expired")
                touch_session()
                st.rerun()


def _force_password_change_screen(session):
    st.warning("يجب تغيير كلمة المرور قبل المتابعة (سياسة أمنية: أول تسجيل دخول أو انتهاء صلاحية دورية)")
    user = session.query(User).filter(User.id == st.session_state.get("user_id")).first()
    if not user:
        logout(session)
        st.rerun()
        return

    with st.form("change_password_form"):
        current_pwd = st.text_input("كلمة المرور الحالية", type="password")
        new_pwd = st.text_input("كلمة المرور الجديدة", type="password")
        confirm_pwd = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
        submitted = st.form_submit_button("تحديث كلمة المرور")

    if not submitted:
        return

    if not verify_password(current_pwd, user.password_hash):
        st.error("كلمة المرور الحالية غير صحيحة")
        return
    if new_pwd != confirm_pwd:
        st.error("كلمتا المرور الجديدتان غير متطابقتين")
        return

    errors = validate_password_policy(new_pwd, user.username)
    if errors:
        for e in errors:
            st.error(e)
        return

    recent = (session.query(PasswordHistory)
              .filter(PasswordHistory.user_id == user.id)
              .order_by(PasswordHistory.created_at.desc())
              .limit(PASSWORD_HISTORY_COUNT).all())
    if verify_password(new_pwd, user.password_hash) or any(verify_password(new_pwd, h.password_hash) for h in recent):
        st.error(f"لا يمكن إعادة استخدام آخر {PASSWORD_HISTORY_COUNT} كلمات مرور مستخدمة سابقاً")
        return

    session.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))
    user.password_hash = hash_password(new_pwd)
    user.password_changed_at = datetime.utcnow()
    user.must_change_password = False
    session.commit()
    log_action(session, user.username, user.role.value, "تغيير كلمة المرور", "-", category="أمن")

    st.session_state.must_change_password = False
    st.success("تم تحديث كلمة المرور بنجاح")
    st.rerun()


def _sidebar(session, user):
    with st.sidebar:
        st.markdown("### 🏥 VisiPulse")
        st.markdown(f"**المستخدم:** {user.full_name}")
        st.caption(f"الدور: {ROLE_LABELS.get(user.role.value, user.role.value)}")
        st.caption(f"القسم: {user.department or '-'}")
        if user.last_login:
            st.caption(f"آخر دخول سابق: {user.last_login:%Y-%m-%d %H:%M}")
        st.divider()
        st.caption(f"مهلة خمول الجلسة: {SESSION_IDLE_MINUTES} دقيقة")
        if st.button("تسجيل الخروج", width="stretch"):
            logout(session, user.username, user.role.value, "تسجيل خروج يدوي")
            st.rerun()


def main():
    session = get_session()

    if not st.session_state.get("authenticated"):
        _login_screen(session)
        return

    if check_session_timeout():
        stale_username = st.session_state.get("username")
        stale_role = st.session_state.get("role")
        logout(session, stale_username, stale_role, "انتهاء مهلة خمول الجلسة")
        st.warning("انتهت الجلسة بسبب الخمول. الرجاء تسجيل الدخول مجدداً.")
        st.rerun()
        return

    touch_session()

    user = session.query(User).filter(User.id == st.session_state.get("user_id")).first()
    if not user or not user.is_active:
        logout(session)
        st.error("الحساب غير متاح حالياً. الرجاء التواصل مع إدارة تقنية المعلومات.")
        st.rerun()
        return

    # عرض الهيدر العلوي حتى بعد تسجيل الدخول في الواجهات الرئيسية
    st.markdown(VISIPULSE_TOP_HEADER, unsafe_allow_html=True)

    _sidebar(session, user)

    if st.session_state.get("must_change_password"):
        _force_password_change_screen(session)
        return

    if user.role == UserRole.IT:
        it_portal.render(session, user)
    elif user.role == UserRole.EXECUTIVE:
        executive_portal.render(session, user)
    elif user.role == UserRole.EMPLOYEE:
        employee_portal.render(session, user)
    else:
        st.error("دور مستخدم غير معروف.")


if __name__ == "__main__":
    main()
