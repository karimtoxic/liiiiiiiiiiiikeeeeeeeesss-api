from flask import Flask, request, jsonify
import threading
from datetime import datetime, timedelta
import json
from main import start_like
from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import threading
import time
from datetime import datetime
from byte import *
from main import *
app = Flask(__name__)

# الإعدادات
ID_FILE = 'idlikeapi.json'  # ملف تخزين الأيدي
ID_EXPIRATION_HOURS = 24   # الصلاحية بـ 24 ساعة

# تحميل الأيدي المحفوظة من الملف
def load_saved_ids():
    try:
        with open(ID_FILE, 'r') as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ الأيدي في الملف
def save_ids(data):
    with open(ID_FILE, 'w') as file:
        json.dump(data, file)

# إضافة أيدي جديد والتحقق من انتهاء الصلاحية
def save_and_clean_ids(uid):
    saved_ids = load_saved_ids()
    current_time = datetime.now()

    # إزالة الأيدي القديمة التي مضى على استخدامها 24 ساعة
    updated_ids = {uid: timestamp for uid, timestamp in saved_ids.items()
                   if datetime.fromisoformat(timestamp) > current_time - timedelta(hours=ID_EXPIRATION_HOURS)}

    # إضافة الأيدي الجديد إذا لم يكن موجوداً
    if uid not in updated_ids:
        updated_ids[uid] = current_time.isoformat()
        save_ids(updated_ids)
        return True  # تم حفظ الأيدي بنجاح
    else:
        return False  # الأيدي موجود بالفعل

# المسار الجديد
@app.route('/sendLikes', methods=['GET'])
def get_like():
    uid = request.args.get('uid')  # الحصول على UID من الرابط
    if not uid or not uid.isdigit():
        return jsonify({"error": "يرجى توفير UID صالح"}), 400

    # التحقق من الأيدي المحفوظة
    if not save_and_clean_ids(uid):
        return jsonify({
            "error": "🚫 تم إرسال اللايكات لهذا المستخدم بالفعل. يرجى المحاولة بعد 24 ساعة."
        }), 400

    # إرسال اللايكات في Thread منفصل
    threading.Thread(target=start_like, args=(uid,)).start()
    return jsonify({
        "message": "✅ تم إرسال 100 لايك بنجاح!"
    }), 200

# تشغيل الخادم
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

