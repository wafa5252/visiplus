# agents.py
import pandas as pd
from datetime import datetime

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def log_action(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.name}]: {message}"

class InfrastructureAgent(BaseAgent):
    """وكيل البنية التحتية: مسؤول عن الصيانة التنبؤية للشبكات والخوادم"""
    def __init__(self):
        super().__init__("Infrastructure Agent")

    def analyze_infrastructure(self, df_infra):
        alerts = []
        for index, row in df_infra.iterrows():
            if row.get('cpu_usage', 0) > 85 or row.get('temperature', 0) > 75:
                alerts.append({
                    "agent": self.name,
                    "target": row.get('device_name', 'Unknown Server'),
                    "issue": "High CPU or Temperature threshold exceeded - Risk of failure",
                    "severity": "High",
                    "timestamp": datetime.now()
                })
        return alerts

class MedicalSystemsAgent(BaseAgent):
    """وكيل الأنظمة الطبية: مسؤول عن موثوقية الأجهزة الطبية الحيوية"""
    def __init__(self):
        super().__init__("Medical Systems Agent")

    def analyze_devices(self, df_devices):
        alerts = []
        for index, row in df_devices.iterrows():
            if row.get('battery_level', 100) < 20 or row.get('status', '') == 'Error':
                alerts.append({
                    "agent": self.name,
                    "target": row.get('equipment_name', 'Medical Device'),
                    "issue": "Low battery or hardware error detected",
                    "severity": "Critical",
                    "timestamp": datetime.now()
                })
        return alerts

class ITHelpdeskAgent(BaseAgent):
    """وكيل الدعم الفني: مسؤول عن اكتشاف الحالات الشاذة وإدارة التذاكر التلقائية"""
    def __init__(self):
        super().__init__("IT Helpdesk Agent")

    def generate_ticket(self, alert_data):
        ticket = {
            "ticket_id": f"TICK-{datetime.now().strftime('%H%M%S')}",
            "assigned_agent": self.name,
            "issue": alert_data.get('issue'),
            "target": alert_data.get('target'),
            "priority": alert_data.get('severity'),
            "status": "Open",
            "created_at": datetime.now()
        }
        return ticket

class DataGovernanceAgent(BaseAgent):
    """وكيل حوكمة البيانات: مسؤول عن جودة التدفقات والتدقيق"""
    def __init__(self):
        super().__init__("Data Governance Agent")

    def audit_data_quality(self, df):
        missing_values = df.isnull().sum().sum()
        status = "Passed" if missing_values == 0 else "Warning"
        report = {
            "agent": self.name,
            "missing_entries": int(missing_values),
            "status": status,
            "audit_time": datetime.now()
        }
        return report

def run_all_agents(df_infra, df_devices):
    infra_agent = InfrastructureAgent()
    med_agent = MedicalSystemsAgent()
    helpdesk_agent = ITHelpdeskAgent()
    gov_agent = DataGovernanceAgent()

    infra_alerts = infra_agent.analyze_infrastructure(df_infra)
    med_alerts = med_agent.analyze_devices(df_devices)
    
    all_alerts = infra_alerts + med_alerts
    tickets = [helpdesk_agent.generate_ticket(alert) for alert in all_alerts]
    
    governance_report = gov_agent.audit_data_quality(df_infra)

    return {
        "alerts": all_alerts,
        "tickets": tickets,
        "governance": governance_report
    }