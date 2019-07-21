bind = "127.0.0.1:8000"
workers = 3
proc_name = "R2"
user = "ubuntu"
group = "ubuntu"
loglevel = "debug"
timeout = 120
errorlog = "/home/ubuntu/logs/gunicorn.log"
raw_env = [
   'DB_USER=root',
   'DB_PASSWORD=9S5ZhsM6',
   'DB_ADDRESS=r2beta-db.ctfzbndjkjq9.us-east-2.rds.amazonaws.com',
   'DB_NAME=r2_db'
]
