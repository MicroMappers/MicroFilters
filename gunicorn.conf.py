import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
graceful_timeout = 60
timeout = 600
keepalive = 5
loglevel = "DEBUG"
errorlog = "gunicorn-error.log"
