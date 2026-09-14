import asyncio
import aiohttp
import socket

async def fetch_source(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                text = await resp.text()
                # Handle Base64 if needed
                try:
                    if not "://" in text[:50]:
                        decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
                        return decoded.splitlines()
                except Exception:
                    pass
                return text.splitlines()
    except Exception:
        pass
    return []

async def check_tcp(host, port, timeout=1.5):
    start = asyncio.get_event_loop().time()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
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
