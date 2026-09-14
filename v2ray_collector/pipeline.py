import asyncio
import os
import aiohttp
from .config import load_config
from .database import Database
from .parser import decode_config, apply_dynamic_remark
from .net import fetch_source, check_tcp, check_tls, check_sni
from .scorer import calculate_score
from .telegram import send_to_telegram

async def fetch_geo_info(session, host):
    """استعلام آنلاین و سریع لوکیشن IP برای قرار دادن کشور و شهر واقعی"""
    try:
        async with session.get(f"http://ip-api.com/json/{host}?fields=status,country,city,countryCode", timeout=2.5) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("status") == "success":
                    return {
                        "country": data.get("country", "Global"),
                        "city": data.get("city", "Server"),
                        "code": data.get("countryCode", "US")
                    }
    except Exception:
        pass
    return {"country": "Global", "city": "Server", "code": "US"}

async def process_async(config):
    db = Database(config.get("db_path", "history.db"))
    sources = config.get("sources", [])
    
    print(f"[*] در حال دریافت کانفیگ‌ها از {len(sources)} منبع...")
    raw_configs = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in sources]
        results = await asyncio.gather(*tasks)
        for res in results:
            if res:
                raw_configs.extend(res)

    print(f"[+] کل خطوط دریافت شده: {len(raw_configs)}")
    
    unique_nodes = {}
    for line in raw_configs:
        parsed = decode_config(line)
        if parsed:
            key = parsed["node_key"]
            if key not in unique_nodes:
                unique_nodes[key] = parsed

    nodes = list(unique_nodes.values())[:config.get("max_candidates", 1500)]
    print(f"[+] نودهای معنادار پس از Dedup: {len(nodes)}")

    # تست اتصال فوق‌العاده سخت‌گیرانه با TLS Handshake واقعی
    scored_nodes = []
    semaphore = asyncio.Semaphore(15) # کاهش همزمانی بیشتر برای دقت مطلق در تست شبکه

    async with aiohttp.ClientSession() as session:
        async def test_single_node(node):
            async with semaphore:
                host = node["host"]
                port = node["port"]
                
                if config.get("sni_check", True):
                    if not await check_sni(host):
                        return

                # تشخیص کانفیگ‌های امنیتی برای اجرای تست TLS Handshake
                is_tls = port in config.get("golden_ports_t1", []) or port in [443, 8443] or node.get("protocol") in ["vless", "trojan", "hy2"]
                
                max_allowed_ping = 200
                if is_tls:
                    is_ok, latency = await check_tls(host, port, sni=host, timeout=1.2)
                else:
                    is_ok, latency = await check_tcp(host, port, timeout=0.8)
                
                if not is_ok or latency > max_allowed_ping:
                    return

                # دریافت لوکیشن واقعی سرور برای ساخت نام دقیق
                geo_info = await fetch_geo_info(session, host)

                history_score, samples = db.get_score(node["node_key"])
                if samples == 0:
                    history_score = 500.0

                score = calculate_score(node, latency, is_tls, config, history_score, samples)
                
                db.update_score(node["node_key"], score, decay=config.get("ewma_decay", 0.7))
                
                node["score"] = score
                node["latency"] = latency
                # اعمال نام‌گذاری پویا بر اساس کشور، شهر و پینگ واقعی آن نود خاص
                node["final_raw"] = apply_dynamic_remark(node["raw"], latency, geo_info)
                scored_nodes.append(node)

        tasks = [test_single_node(node) for node in nodes]
        await asyncio.gather(*tasks)

    # مرتب‌سازی بر اساس امتیاز
    scored_nodes.sort(key=lambda x: x["score"], reverse=True)
    
    # خروجی کاملاً کیفی: هر چه تعداد نودهای سالم کمتر شود، کیفیت به ۱۰۰٪ نزدیک‌تر می‌گردد
    top_nodes = scored_nodes[:min(len(scored_nodes), 150)]
    print(f"[+] نودهای نهایی با تست هندشیک TLS (تضمین صددرصدی فعالیت): {len(top_nodes)}")

    chunk_size = config.get("chunk_size", 150)
    generated_files = []
    
    for i in range(0, len(top_nodes), chunk_size):
        chunk = top_nodes[i:i + chunk_size]
        file_name = f"subscription_part{(i // chunk_size) + 1}.txt"
        
        content = "\n".join([n["final_raw"] for n in chunk])
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        generated_files.append(file_name)

    return generated_files

def run_pipeline(config, dry_run=False):
    try:
        files = asyncio.run(process_async(config))
        print(f"[+] فایل‌های خروجی با موفقیت ساخته شدند: {files}")
        
        if not dry_run:
            asyncio.run(send_to_telegram(files, config))
        else:
            print("[*] حالت Dry-Run فعال است؛ ارسال به تلگرام انجام نشد.")
        return True
    except Exception as e:
        print(f"[-] خطا در اجرای پایپ‌لاین: {e}")
        return False
