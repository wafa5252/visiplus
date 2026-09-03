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
</style>
"""
st.markdown(_RTL_CSS, unsafe_allow_html=True)

ROLE_LABELS = {"it": "تقنية المعلومات", "executive": "الإدارة العليا", "employee": "موظف"}

VISIPULSE_LOGO_SVG = """
<svg viewBox="0 0 700 220" xmlns="http://www.w3.org/2000/svg" style="background: transparent; width: 100%; height: auto;">
  <defs>
    <linearGradient id="streamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1E40AF" />
      <stop offset="50%" stop-color="#0284C7" />
      <stop offset="100%" stop-color="#06B6D4" />
    </linearGradient>
    <linearGradient id="pulseGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06B6D4" />
      <stop offset="100%" stop-color="#10B981" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <rect width="100%" height="100%" rx="16" fill="#0F172A" opacity="0.95" />
  <path d="M 50 110 C 180 40, 320 180, 650 90" fill="none" stroke="url(#streamGrad)" stroke-width="4" stroke-linecap="round" opacity="0.4" />
  <path d="M 70 135 C 200 65, 340 205, 630 115" fill="none" stroke="url(#streamGrad)" stroke-width="2" stroke-linecap="round" opacity="0.25" />
  <path d="M 40 120 L 110 120 L 125 90 L 140 150 L 160 100 L 175 130 L 190 120 L 230 120" 
        fill="none" stroke="url(#pulseGrad)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
  <text x="250" y="115" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="58" font-weight="800" letter-spacing="1.5">
    <tspan fill="#F8FAFC">Visi</tspan><tspan fill="#38BDF8">Pulse</tspan>
  </text>
  <text x="254" y="150" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="500" fill="#94A3B8" letter-spacing="4">
    THE FLOW OF SMART HEALTHCARE
  </text>
  <circle cx="615" cy="98" r="5" fill="#34D399" filter="url(#glow)" />
</svg>
"""


@st.cache_resource
def _bootstrap_db():
    init_db()
    return True


_bootstrap_db()


def _login_screen(session):
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown(VISIPULSE_LOGO_SVG, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

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
        st.markdown(VISIPULSE_LOGO_SVG, unsafe_allow_html=True)
        st.markdown(f"### {user.full_name}")
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
