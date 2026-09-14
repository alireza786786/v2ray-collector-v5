import base64
import re
from urllib.parse import urlparse, parse_qs

def decode_config(raw_line):
    raw_line = raw_line.strip()
    if not raw_line or raw_line.startswith("#"):
        return None
    
    if raw_line.startswith("vless://") or raw_line.startswith("trojan://") or raw_line.startswith("ss://") or raw_line.startswith("vmess://") or raw_line.startswith("hy2://") or raw_line.startswith("hysteria2://"):
        return parse_uri(raw_line)
    return None

def parse_uri(uri):
    try:
        parsed = urlparse(uri)
        protocol = parsed.scheme.lower()
        if protocol == "hysteria2":
            protocol = "hy2"
            
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None
            
        node_key = f"{host}:{port}"
        return {
            "raw": uri,
            "protocol": protocol,
            "host": host,
            "port": port,
            "node_key": node_key,
            "name": parsed.fragment or "Config"
        }
    except Exception:
        return None
