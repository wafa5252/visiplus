import os
os.environ["VISIPULSE_ENCRYPTION_KEY"] = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

from database import get_session
from models import User

session = get_session()
users = session.query(User).all()

print("=" * 60)
print("حسابات المستخدمين الموجودة في قاعدة البيانات:")
print("=" * 60)
for u in users:
    print(f"اسم المستخدم: {u.username} | الدور: {u.role.value}")
print("=" * 60)
print("ملاحظة: كلمات المرور المؤقتة يتم توليدها عشوائياً عند أول تشغيل لـ seed.py،")
print("إذا كنتِ تبغين تعيدين تعيين كلمة مرور جديدة لأي حساب بسهولة، قومي بحذف ملف visipulse.db")
print("وتعديل طريقة حقن المفتاح أو تشغيل السكربت بالشكل الصحيح.")