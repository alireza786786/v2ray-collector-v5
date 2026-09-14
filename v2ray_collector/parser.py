import base64
import re
from urllib.parse import urlparse, urlunparse

TARGET_BASE_TAG = "👉🆔@Goodbaye_filtering"

def country_code_to_flag(code):
    """تبدیل کد دو حرفی کشور به ایموجی پرچم"""
    if not code or len(code) != 2:
        return "🌐"
    return "".join(chr(ord(c.upper()) + 127397) for c in code)

def decode_config(raw_line):
    raw_line = raw_line.strip()
    if not raw_line or raw_line.startswith("#"):
        return None
    
    if any(raw_line.startswith(p) for p in ["vless://", "trojan://", "ss://", "vmess://", "hy2://", "hysteria2://"]):
        return parse_uri(raw_line)
    return None

def apply_dynamic_remark(uri, latency_ms, geo_info=None):
    """
    ساخت نام پویا بر اساس پرچم، کشور، شهر واقعی و پینگ تست‌شده
    الگو: 👉🆔@Goodbaye_filtering📡[Flag]®️[Country]©️[City]🅿️ping:[val]ms
    """
    ping_val = int(round(latency_ms))
    
    if not geo_info:
        geo_info = {"country": "Unknown", "city": "Unknown", "code": "XX"}
    
    country = geo_info.get("country", "Unknown")
    city = geo_info.get("city", "Unknown")
    code = geo_info.get("code", "XX")
    flag = country_code_to_flag(code)
    
    new_remark = f"{TARGET_BASE_TAG}📡{flag}®️{country}©️{city}🅿️ping:{ping_val}ms"
    
    try:
        parsed = urlparse(uri)
        clean_url = parsed._replace(fragment=new_remark)
        return urlunparse(clean_url)
    except Exception:
        if "#" in uri:
            uri = uri.split("#")[0]
        return f"{uri}#{new_remark}"

def parse_uri(uri):
    try:
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
            "raw": base_uri,
            "protocol": protocol,
            "host": host,
            "port": port,
            "node_key": node_key,
            "original_uri": uri
        }
    except Exception:
        return None
