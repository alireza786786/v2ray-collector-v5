def calculate_score(node, latency, is_tls, config_cfg, history_score, samples):
    score = 1000 - latency
    port = node["port"]
    
    if port in config_cfg.get("golden_ports_t1", []):
        score += config_cfg.get("golden_bonus_t1", 180)
    elif port in config_cfg.get("golden_ports_t2", []):
        score += config_cfg.get("golden_bonus_t2", 80)
        
    if samples >= config_cfg.get("min_history_samples", 3):
        score = 0.5 * score + 0.5 * history_score
        
    return max(score, 10)
