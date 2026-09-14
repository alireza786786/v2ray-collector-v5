import asyncio
import aiohttp
import socket
import base64
import ssl

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
    start = asyncio.get_event_loop().time()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        latency = (asyncio.get_event_loop().time() - start) * 1000
        return True, latency
    except Exception:
        return False, 0

async def check_tls(host, port, sni=None, timeout=1.5):
    """
    تست فوق‌العاده سخت‌گیرانه TLS Handshake برای تضمین زنده بودن سرویس‌های امن
    """
    start = asyncio.get_event_loop().time()
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=ssl_context, server_hostname=sni or host),
            timeout=timeout
        )
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
