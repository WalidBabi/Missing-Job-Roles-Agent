"""
Utility functions for safe printing on Windows
"""
import sys


def safe_print(*args, **kwargs):
    """
    Print function that handles Unicode encoding errors on Windows.
    Replaces emojis with ASCII-safe alternatives if encoding fails.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace emojis with ASCII alternatives
        emoji_map = {
            '🚀': '[START]',
            '🔍': '[ANALYZING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🔴': '[CRITICAL]',
            '🟠': '[HIGH]',
            '🟡': '[MEDIUM]',
            '⚪': '[LOW]',
        }
        
        # Convert args to strings and replace emojis
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_arg = arg
                for emoji, replacement in emoji_map.items():
                    safe_arg = safe_arg.replace(emoji, replacement)
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        
        try:
            print(*safe_args, **kwargs)
        except Exception:
            # Last resort: encode as ASCII with error handling
            safe_args_str = []
            for arg in safe_args:
                if isinstance(arg, str):
                    safe_args_str.append(arg.encode('ascii', errors='replace').decode('ascii'))
                else:
                    safe_args_str.append(str(arg))
            print(*safe_args_str, **kwargs)

