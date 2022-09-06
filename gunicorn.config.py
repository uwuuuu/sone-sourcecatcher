from gevent import monkey; monkey.patch_all()
print("Successfully applied monkey patch")

worker_class = 'gevent'
preload_app = True
bind = '127.0.0.1:8000'
workers = 4
