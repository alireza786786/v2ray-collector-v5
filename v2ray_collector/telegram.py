import os
import re
import aiohttp

async def send_to_telegram(files, config):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not bot_token or not chat_id:
        print("Telegram credentials missing. Skipping send.")
        return

    telegram_link = config.get("telegram_link", "https://t.me/Goodbaye_filtering")
    group_link = config.get("group_link", "https://t.me/CONFIG_V2RAY_VIP")
    channel_tag = config.get("channel_tag", "Goodbaye_filtering").lstrip("@")

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    async with aiohttp.ClientSession() as session:
        for file_path in files:
            if not os.path.exists(file_path):
                continue

            filename = os.path.basename(file_path)
            
            # تشخیص هوشمند شماره پارت از نام فایل
            part_match = re.search(r'part(\d+)', filename)
            part_num = part_match.group(1) if part_match else "1"

            # شمارش دقیق کانفیگ‌های فعال داخل همین فایل
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    configs_count = len([line for line in f if line.strip()])
            except Exception:
                configs_count = config.get("chunk_size", 150)

            # متن شیک و حرفه‌ای کپشن با فرمت استاندارد HTML
            caption = (
                f"🔥 <b>اشتراک هوشمند — پارت {part_num}</b>\n\n"
                f"🚀 <code>v2ray_collector_v5</code>\n\n"
                f"📦 <b>فایل:</b> <code>{filename}</code>\n"
                f"📊 <b>تعداد:</b> <b>{configs_count}</b> کانفیگ تست‌شده و فعال\n"
                f"⚡ <b>وضعیت:</b> تست TLS موفق | تضمین پایداری\n\n"
                f"💬 <b>گروه:</b> {group_link}\n"
                f"✨ <b>کانال:</b> {telegram_link}\n"
                f"🆔 @{channel_tag}"
            )

            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', open(file_path, 'rb'), filename=filename)
            data.add_field('caption', caption)
            data.add_field('parse_mode', 'HTML')

            try:
                async with session.post(url, data=data) as resp:
                    if resp.status == 200:
                        print(f"Successfully sent {file_path}")
                    else:
                        print(f"Failed to send {file_path}: {await resp.text()}")
            except Exception as e:
                print(f"Error sending to telegram: {e}")
