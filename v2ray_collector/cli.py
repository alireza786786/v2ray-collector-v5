import argparse
import sys
from .config import load_config
from .pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="V2Ray Smart Collector v5")
    parser.add_argument("command", nargs="?", default="run", choices=["run"], help="دستور اجرایی")
    parser.add_argument("--config", default="config.yaml", help="مسیر فایل تنظیمات")
    parser.add_argument("--dry-run", action="store_true", help="فقط ساخت فایل‌ها بدون ارسال به تلگرام")
    parser.add_argument("--top", type=int, default=None, help="تعداد نودهای برتر برای نمایش")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.top:
        config["top_n_final"] = args.top

    if args.command == "run":
        success = run_pipeline(config, dry_run=args.dry_run)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
