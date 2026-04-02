import os
import multiprocessing

# Worker Settings
# Respect WEB_CONCURRENCY (Render default is 1 for free tier)
# This prevents OOM errors on limited RAM instances
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = 'gthread'
threads = 4
timeout = 120

# Network Settings
bind = "0.0.0.0:5000"

# Logging Settings
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Performance Tuning
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
