# ui/employee_portal.py
import streamlit as st
import pandas as pd
from agents import run_all_agents

def render(session, user):
    st.markdown("## بوابة الموظف - متابعة الأجهزة والإنذارات الاستباقية")
    st.markdown(f"مرحباً بك، {user.full_name}. يمكنك أدناه متابعة حالة الأجهزة المخصصة لبيئة عملك والإنذارات المبكرة.")
    st.divider()

    # محاكاة بيانات الأجهزة الخاصة بقسم الموظف أو عهدته
    # في النظام الفعلي يتم جلبها من قاعدة البيانات المرتبطة بالمستخدم
    sample_infra = pd.DataFrame([{
        'device_name': f'جهاز محطة العمل - {user.department or "عام"}',
        'cpu_usage': 88.5,
        'temperature': 78.0,
        'status': 'Warning'
    }])
    
    sample_devices = pd.DataFrame([{
        'equipment_name': 'شاشة المتابعة الحيوية الميدانية',
        'battery_level': 85,
        'status': 'Normal'
    }])

    # تشغيل وكلاء الذكاء الاصطناعي لفحص حالة أجهزة الموظف
    agent_results = run_all_agents(sample_infra, sample_devices)
    alerts = agent_results["alerts"]

    st.markdown("### حالة أجهزة العهدة والإنذارات المبكرة")
    
    if alerts:
        for alert in alerts:
            st.error(
                f"تنبيه استباقي من وكيل ({alert['agent']}): "
                f"الجهاز المستهدف ({alert['target']}) يعاني من مشكلة ({alert['issue']}). "
                f"مستوى الخطورة: {alert['severity']}. يرجى رفع تذكرة دعم فني."
            )
    else:
        st.success("جميع الأجهزة والأنظمة المرتبطة بعهدتك تعمل بكفاءة عالية ولا توجد أعطال استباقية مسجلة.")

    st.divider()
    st.markdown("### الإجراءات السريعة")
    with st.form("employee_ticket_form"):
        st.markdown("**طلب دعم فني عاجل**")
        issue_desc = st.text_area("وصف المشكلة التقنية أو الملاحظة على الجهاز")
        submitted = st.form_submit_button("إرسال التذكرة لقسم تقنية المعلومات")
        if submitted and issue_desc:
            st.success("تم إرسال تذكرتك بنجاح وتسجيلها في النظام لتتم معالجتها من قبل فريق الدعم الفني.")
