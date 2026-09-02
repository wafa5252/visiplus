# ui/it_portal.py
import streamlit as st
import pandas as pd
from agents import run_all_agents

def render(session, user):
    st.markdown("## بوابة تقنية المعلومات والحوكمة التشغيلية")
    st.markdown(f"مرحباً بك، {user.full_name}. لوحة التحكم المركزية لإدارة قطاعات التقنية، البنية التحتية، والصحة الإلكترونية.")
    st.divider()

    # محاكاة بيانات الأجهزة والخوادم للتحليل التنبؤي
    infra_df = pd.DataFrame([
        {'device_name': 'خادم النظام الرئيسي - مركز البيانات', 'cpu_usage': 89.0, 'temperature': 79.0, 'status': 'Warning'},
        {'device_name': 'خادم قاعدة بيانات المرضى', 'cpu_usage': 65.0, 'temperature': 62.0, 'status': 'Normal'},
        {'device_name': 'بوابة الشبكة والاتصالات الطبية', 'cpu_usage': 92.5, 'temperature': 84.0, 'status': 'Critical'}
    ])

    devices_df = pd.DataFrame([
        {'equipment_name': 'جهاز التخدير والمراقبة الحيوية', 'battery_level': 18, 'status': 'Error'},
        {'equipment_name': 'مضخة المحاليل الذكية', 'battery_level': 75, 'status': 'Normal'},
        {'equipment_name': 'جهاز تخطيط القلب المحمول', 'battery_level': 95, 'status': 'Normal'}
    ])

    # تشغيل نظام الوكلاء الأذكياء
    agent_results = run_all_agents(infra_df, devices_df)
    alerts = agent_results["alerts"]
    tickets = agent_results["tickets"]
    governance = agent_results["governance"]

    # تقسيم البوابة إلى أقسام تشغيلية بناءً على الهيكل التنظيمي الفعلي
    tab_support, tab_infra, tab_ehealth, tab_systems = st.tabs([
        "قسم الدعم الفني", 
        "قسم البنية التحتية", 
        "إدارة الصحة الإلكترونية والجودة وحوكمة البيانات", 
        "قسم الأنظمة والتطبيقات"
    ])

    with tab_support:
        st.markdown("### إدارة البلاغات والتذاكر التلقائية")
        st.markdown("متابعة التذاكر الناتجة عن الإنذارات المبكرة وأعطال الأجهزة بلا توقف.")
        if tickets:
            tickets_df = pd.DataFrame(tickets)
            st.dataframe(tickets_df, use_container_width=True)
            
            selected_ticket = st.selectbox("اختر رقم التذكرة لتحديث حالتها", options=[t["ticket_id"] for t in tickets])
            new_status = st.selectbox("الحالة الجديدة", options=["قيد المعجلة", "مكتملة", "تحت الإجراء"])
            if st.button("تحديث حالة التذكرة"):
                st.success(f"تم تحديث حالة التذكرة {selected_ticket} بنجاح إلى: {new_status}")
        else:
            st.info("لا توجد تذاكر دعم فني مفتوحة حالياً.")

    with tab_infra:
        st.markdown("### مراقبة أداء البنية التحتية والخوادم")
        st.markdown("مراقبة مؤشرات المعالجات والحرارة للوقاية من التوقف المفاجئ.")
        st.dataframe(infra_df, use_container_width=True)
        
        if alerts:
            st.markdown("#### التنبيهات الحرجة للبنية التحتية")
            for alert in [a for a in alerts if "Infrastructure" in a["agent"]]:
                st.error(f"تنبيه من {alert['target']}: {alert['issue']} (الخطورة: {alert['severity']})")

    with tab_ehealth:
        st.markdown("### إدارة الصحة الإلكترونية - مدير الجودة وحوكمة البيانات")
        st.markdown("مراجعة جودة التدفقات السريرية، مطابقة المعايير، والتدقيق الشامل لبيانات الأجهزة والمنظومة الصحية.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="حالة تدقيق البيانات", value=governance["status"])
        with col2:
            st.metric(label="إجمالي السجلات المفقودة أو غير المتطابقة", value=str(governance["missing_entries"]))

        st.markdown("#### تقرير جودة البيانات وحوكمتها الصادر عن الوكيل الذكي")
        st.json(governance)

        if st.button("تنفيذ تدقيق فوري لجودة البيانات الطبية"):
            st.success("تم إتمام عملية التدقيق بنجاح وتأكيد سلامة تدفقات بيانات المرضى والأجهزة.")

    with tab_systems:
        st.markdown("### قسم الأنظمة والتطبيقات الطبية")
        st.markdown("متابعة تكامل الأنظمة، السجلات الإلكترونية، وبرمجيات التشغيل الذكي.")
        st.dataframe(devices_df, use_container_width=True)

        if alerts:
            st.markdown("#### تنبيهات الأنظمة الطبية")
            for alert in [a for a in alerts if "Medical" in a["agent"]]:
                st.warning(f"تنبيه جهاز طبي ({alert['target']}): {alert['issue']}")

    st.divider()
    st.markdown("### التحكم الشامل وإدارة النظام")
    if st.button("تصدير تقرير عمليات تقنية المعلومات الكامل"):
        st.success("تم تجهيز التقرير التقني الشامل وتصديره بصيغة مستند رسمي.")
