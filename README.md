<div align="center">

# 🚀 V2Ray Smart Collector v5

**سیستم هوشمند، خودکار و مهندسی‌شده جمع‌آوری، تست چندمرحله‌ای و انتشار کانفیگ‌های V2Ray**

[![V2Ray Collector v5](https://img.shields.io/badge/Status-Active%20&%20Stable-success?style=for-the-badge&logo=github)](https://github.com/alireza786786/v2ray-collector-v5)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20v5-orange?style=for-the-badge)

</div>

---

## ✨ ویژگی‌های کلیدی نسل پنجم (v5)

- **معماری کاملاً ماژولار**: تفکیک وظایف در پوشه‌ی اختصاصی `v2ray_collector` شامل پارسر، مدیریت دیتابیس، شبکه، تست و پایپ‌لاین[cite: 5, 12].
- **سیستم پورت‌های طلایی دو ردیفه (Golden Ports)**: اعمال بونس امتیازی ویژه برای پورت‌های امن و پرسرعت (T1 & T2).
- **فیلتر تخصصی SNI**: اعتبارسنجی دامنه و رزولوشن DNS پیش از انجام تست‌های زمان‌بر شبکه.
- **سیستم امتیازدهی EWMA (میانگین متحرک وزنی نمایی)**: ارزیابی پایداری نودها در طول زمان با استفاده از پایگاه داده محلی SQLite.
- **Dedup هوشمند**: حذف نودهای تکراری روی یک ترکیب `host:port` و نگهداری باارزش‌ترین پروتکل.
- **اتوماسیون کامل با GitHub Actions**: اجرا و به‌روزرسانی خودکار هر ۶ ساعت یک‌بار و ارسال مستقیم خروجی‌ها به تلگرام[cite: 3, 12].

---

## 📂 ساختار پروژه

```text
v2ray-collector-v5/
├── .github/
│   └── workflows/
│       └── run.yml          # اتوماسیون هر ۶ ساعت
├── v2ray_collector/         # هسته ماژولار برنامه
│   ├── __init__.py
│   ├── cli.py               # رابط خط فرمان
│   ├── config.py            # مدیریت تنظیمات YAML
│   ├── database.py          # مدیریت دیتابیس و EWMA
│   ├── net.py               # تست‌های شبکه و فیلتر SNI
│   ├── parser.py            # استخراج‌کننده پروتکل‌ها
│   ├── pipeline.py          # خط لوله اجرایی اصلی
│   ├── scorer.py            # الگوریتم امتیازدهی نودها
│   └── telegram.py          # ارسال خروجی به تلگرام
├── config.yaml              # تنظیمات پیشرفته
├── requirements.txt         # وابستگی‌های پایتون
└── v2ray_collector_v5.py    # لانچر اصلی اجرا
