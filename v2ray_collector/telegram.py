import os
import aiohttp

async def send_to_telegram(files, config):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not bot_token or not chat_id:
        print("Telegram credentials missing. Skipping send.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    async with aiohttp.ClientSession() as session:
        for file_path in files:
            if not os.path.exists(file_path):
                continue
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            data.add_field('document', open(file_path, 'rb'), filename=os.path.basename(file_path))
            data.add_field('caption', f"✨ کانفیگ‌های به‌روزرسانی شده — {config.get('channel_tag', 'V2Ray')}")
            
            try:
                async with session.post(url, data=data) as resp:
                    if resp.status == 200:
                        print(f"Successfully sent {file_path}")
                    else:
                        print(f"Failed to send {file_path}: {await resp.text()}")
            except Exception as e:
                print(f"Error sending to telegram: {e}")
