import time, random
from datetime import datetime

paths = ["/", "/home", "/login", "/cart", "/api/order"]
statuses = [200, 200, 404, 500]

while True:
    line = f'127.0.0.1 - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET {random.choice(paths)} HTTP/1.1" {random.choice(statuses)} 123\n'
    with open("access.log", "a") as f:
        f.write(line)
    time.sleep(1)
