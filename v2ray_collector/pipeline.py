import asyncio
import os
import aiohttp
from .config import load_config
from .database import Database
from .parser import decode_config, apply_custom_remark
from .net import fetch_source, check_tcp, check_sni
from .scorer import calculate_score
from .telegram import send_to_telegram

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
    
    # پارس و Dedup هوشمند
    unique_nodes = {}
    for line in raw_configs:
        parsed = decode_config(line)
        if parsed:
            key = parsed["node_key"]
            if key not in unique_nodes:
                unique_nodes[key] = parsed

    nodes = list(unique_nodes.values())[:config.get("max_candidates", 1500)]
    print(f"[+] نودهای معنادار پس از Dedup: {len(nodes)}")

    # تست TCP و SNI با سخت‌گیری بسیار بالا
    scored_nodes = []
    semaphore = asyncio.Semaphore(config.get("max_workers", 30)) # کاهش همزمانی برای دقت بیشتر تست

    async def test_single_node(node):
        async with semaphore:
            host = node["host"]
            port = node["port"]
            
            if config.get("sni_check", True):
                if not await check_sni(host):
                    return

            # اعمال حد پینگ سخت‌گیرانه (حداکثر 250 میلی‌ثانیه برای کیفیت بالا)
            max_allowed_ping = config.get("max_ping_ms", 250)
            is_ok, latency = await check_tcp(host, port, timeout=config.get("tcp_timeout", 1.0))
            
            if not is_ok or latency > max_allowed_ping:
                return

            history_score, samples = db.get_score(node["node_key"])
            if samples == 0:
                history_score = 500.0

            is_tls = port in config.get("golden_ports_t1", []) or port in [443, 8443]
            score = calculate_score(node, latency, is_tls, config, history_score, samples)
            
            # آپدیت پایگاه داده EWMA
            db.update_score(node["node_key"], score, decay=config.get("ewma_decay", 0.7))
            
            node["score"] = score
            node["latency"] = latency
            # اعمال ساختار نام‌گذاری سفارشی شما همراه با پینگ واقعی
            node["final_raw"] = apply_custom_remark(node["raw"], latency)
            scored_nodes.append(node)

    tasks = [test_single_node(node) for node in nodes]
    await asyncio.gather(*tasks)

    # مرتب‌سازی بر اساس امتیاز نهایی
    scored_nodes.sort(key=lambda x: x["score"], reverse=True)
    
    # محدود کردن به تعداد نودهای کاملاً باکیفیت و برتر (حتی اگر تعداد کمتر از 500 باشد)
    top_limit = min(len(scored_nodes), config.get("top_n_final", 300))
    top_nodes = scored_nodes[:top_limit]
    print(f"[+] نودهای نهایی 100% فعال و تایید شده: {len(top_nodes)}")

    # ساخت فایل‌های اشتراک (Subscription parts)
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
