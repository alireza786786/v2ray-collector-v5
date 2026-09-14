import base64
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

TARGET_REMARK = "👉🆔@Goodbaye_filtering📡🇩🇪®️Germany©️Nuremberg🅿️ping"

def decode_config(raw_line):
    raw_line = raw_line.strip()
    if not raw_line or raw_line.startswith("#"):
        return None
    
    if any(raw_line.startswith(p) for p in ["vless://", "trojan://", "ss://", "vmess://", "hy2://", "hysteria2://"]):
        return parse_uri(raw_line)
    return None

def apply_custom_remark(uri, latency_ms):
    """
    اعمال الگوی نام‌گذاری اجباری روی هر کانفیگ با پینگ واقعی اندازه گیری شده
    """
    ping_val = int(round(latency_ms))
    new_remark = f"{TARGET_REMARK}:{ping_val}ms"
    
    try:
        parsed = urlparse(uri)
        # حذف فاقدنام قبلی و جایگزینی با نام جدید در انتهای لینک (fragment)
        # برای لینک‌های مختلف ساختار متفاوت است، اما استاندارد URI از # استفاده می‌کند
        clean_url = parsed._replace(fragment=new_remark)
        return urlunparse(clean_url)
    except Exception:
        # روش جایگزین در صورت خطای ساختاری
        if "#" in uri:
            uri = uri.split("#")[0]
        return f"{uri}#{new_remark}"

def parse_uri(uri):
    try:
        # جدا کردن بخش انفرادی پایتون
        base_uri = uri.split("#")[0]
        parsed = urlparse(base_uri)
        protocol = parsed.scheme.lower()
        if protocol == "hysteria2":
            protocol = "hy2"
            
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None
            
        node_key = f"{host}:{port}"
        return {
            "raw": base_uri, # نسخه خام بدون نام قبلی
            "protocol": protocol,
            "host": host,
            "port": port,
            "node_key": node_key,
            "original_uri": uri
        }
    except Exception:
        return None
