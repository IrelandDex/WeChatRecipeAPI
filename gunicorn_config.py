# gunicorn_config.py

import multiprocessing

bind = "0.0.0.0:80"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'  # 使用同步模式
threads = 2  # 每个 worker 的线程数
accesslog = "-"  # 访问日志输出到标准输出
errorlog = "-"  # 错误日志输出到标准输出
loglevel = "info"  # 日志级别
timeout = 120  # 请求超时时间
keepalive = 5  # 保持连接的时间
graceful_timeout = 30  # 优雅重启超时时间
preload_app = True  # 预加载应用程序
