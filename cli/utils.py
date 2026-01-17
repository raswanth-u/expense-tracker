from datetime import datetime

def get_datetime_input(prompt: str) -> datetime:
    """Get datetime input with multiple format support"""
    formats = [
        "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:00
        "%Y-%m-%d",           # 2024-01-15 (will add 00:00:00)
        "%Y/%m/%d %H:%M:%S",  # 2024/01/15 14:30:00
        "%Y/%m/%d",           # 2024/01/15
    ]
    
    while True:
        date_str = input(prompt + r" in %Y-%m-%d" + ": ").strip()
        
        # Try empty for current time
        if not date_str:
            return datetime.now()
        
        # Try each format
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print("Invalid format. Try: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD")