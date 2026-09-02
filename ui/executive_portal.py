# ui/executive_portal.py
import streamlit as st
import pandas as pd
from agents import run_all_agents

def render(session, user):
    st.markdown("## لوحة القيادة العليا - حوكمة البنية التحتية والمستشفيات")
    st.markdown("نظرة شاملة على كفاءة الأجهزة الطبية والتقنية، مؤشرات الاستقرار، والتقارير الاستراتيجية لدعم اتخاذ القرار.")
    st.divider()

    # محاكاة بيانات شاملة وموسعة لمستويات المستشفى
    infra_df = pd.DataFrame([
        {'device_name': 'خادم النظام الرئيسي - العناية المركزة', 'cpu_usage': 91.0, 'temperature': 82.0, 'status': 'Critical'},
        {'device_name': 'خادم سجلات المرضى الإلكترونية', 'cpu_usage': 64.0, 'temperature': 60.0, 'status': 'Normal'},
        {'device_name': 'شبكة اتصالات غرف العمليات', 'cpu_usage': 72.0, 'temperature': 68.0, 'status': 'Normal'}
    ])

    devices_df = pd.DataFrame([
        {'equipment_name': 'جهاز التنفس الصناعي - وحدة 1', 'battery_level': 15, 'status': 'Error'},
        {'equipment_name': 'جهاز تخطيط القلب الرقمي', 'battery_level': 90, 'status': 'Normal'},
        {'equipment_name': 'مضخة الأنسولين الذكية', 'battery_level': 45, 'status': 'Normal'}
    ])

    # تشغيل التحليلات والوكلاء الذكاء الاصطناعي
    results = run_all_agents(infra_df, devices_df)
    governance = results["governance"]
    tickets = results["tickets"]

    # مؤشرات الأداء العليا (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="إجمالي الأجهزة والأنظمة", value="142 نظام")
    with col2:
        st.metric(label="الأعطال الحرجة المكتشفة", value=str(len(results["alerts"])), delta="تطلب التدخل", delta_color="inverse")
    with col3:
        st.metric(label="معدل استقرار البنية التحتية", value="94.2%", delta="+1.5%")
    with col4:
        st.metric(label="حالة تدقيق البيانات وحوكمتها", value=governance["status"])

    st.divider()
    st.markdown("### التحليل الاستراتيجي لحالة الأجهزة الطبية والتقنية")

    tab1, tab2, tab3 = st.tabs(["مؤشرات الخوادم والبنية", "جاهزية الأجهزة الطبية", "التذاكر وحوكمة القرار"])

    with tab1:
        st.markdown("#### حالة خوادم وأنظمة التقنية الحرجة")
        st.dataframe(infra_df, use_container_width=True)

    with tab2:
        st.markdown("#### حالة الأجهزة الطبية الحيوية ومستوى البطاريات")
        st.dataframe(devices_df, use_container_width=True)

    with tab3:
        st.markdown("#### التذاكر التلقائية الصادرة عن الوكلاء الأذكياء")
        if tickets:
            tickets_df = pd.DataFrame(tickets)
            st.dataframe(tickets_df, use_container_width=True)
        else:
            st.info("لا توجد تذاكر مفتوحة حالياً، جميع العمليات تسير بشكل مستقر.")

    st.divider()
    st.markdown("### اتخاذ القرار الاستراتيجي واعتماد التقارير")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("تصدير تقرير الحوكمة الشامل (PDF)", width="stretch"):
            st.success("تم إعداد وتصدير تقرير الحوكمة الاستراتيجي للإدارة العليا بنجاح.")
    with col_b:
        if st.button("اعتماد خطة الصيانة الاستباقية المقترحة", width="stretch"):
            st.success("تم اعتماد خوارزميات الصيانة التنبؤية وإرسال التوجيه لفريق تقنية المعلومات والتشغيل.")
