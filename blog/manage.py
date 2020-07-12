#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading

z = 0
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def run_redis():
    print("哈哈")
    os.system('start redis-cli -h 534640040.top -p 6379 ')


if __name__ == '__main__':
    # threading.Thread(target=run_redis).start()  # 多线程开启redis
    main()
