import os
import yaml

DEFAULT_CONFIG = {
    "channel_tag": "Goodbaye_filtering",
    "telegram_link": "https://t.me/Goodbaye_filtering",
    "group_link": "https://t.me/CONFIG_V2RAY_VIP",
    "sources": [],
    "max_workers": 50,
    "max_candidates": 1500,
    "top_n_final": 500,
    "chunk_size": 150,
    "stability_rounds": 2,
    "tcp_timeout": 1.5,
    "tls_timeout": 2.5,
    "max_ping_ms": 400,
    "max_tls_ping_ms": 600,
    "include_vmess": True,
    "golden_ports_t1": [443, 2053, 2083, 2087, 2096, 8443],
    "golden_ports_t2": [80, 2052, 2082, 2086, 8080, 8880],
    "golden_bonus_t1": 180,
    "golden_bonus_t2": 80,
    "golden_t1_reality_extra": 60,
    "golden_only_tls": True,
    "golden_filter_only": False,
    "ewma_decay": 0.7,
    "min_history_samples": 3,
    "sni_check": True,
    "geo_max_concurrent": 20,
    "geo_timeout": 3.0,
    "geo_max_calls_per_run": 800,
    "real_test_enabled": True,
    "real_test_max_candidates": 250,
    "real_test_concurrency": 15,
    "real_test_url": "http://cp.cloudflare.com/generate_204",
    "real_test_timeout": 5.0,
    "db_path": "history.db"
}

def load_config(path="config.yaml"):
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f)
            if user_cfg:
                config.update(user_cfg)
    return config
