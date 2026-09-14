import asyncio
import aiohttp
import socket
import base64

async def fetch_source(session, url, timeout=15.0):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            if resp.status == 200:
                text = await resp.text()
                try:
                    if text and not "://" in text[:50]:
                        decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
                        return [line.strip() for line in decoded.splitlines() if line.strip()]
                except Exception:
                    pass
                return [line.strip() for line in text.splitlines() if line.strip()]
    except asyncio.TimeoutError:
        print(f"[-] تایم‌آوت (Timeout) در دریافت از منبع: {url}")
    except Exception as e:
        print(f"[-] خطا در دریافت منبع {url}: {e}")
    return []

async def check_tcp(host, port, timeout=1.0):
    """
    تست TCP بسیار سخت‌گیرانه با تایم‌آوت پایین (1 ثانیه) برای تضمین پایداری واقعی
    """
    start = asyncio.get_event_loop().time()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        # تست مضاعف خواندن/نوشتن برای اطمینان از برقراری کامل کانال
        writer.write(b"\x00")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        latency = (asyncio.get_event_loop().time() - start) * 1000
        return True, latency
    except Exception:
        return False, 0

async def check_sni(host):
    try:
        loop = asyncio.get_running_loop()
        await loop.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        return True
    except Exception:
        return False
