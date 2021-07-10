import time

import requests

for i in range(3):
    print(i)
    time.sleep(0.1)

requests.get('badurl')

for i in range(3):
    print(i)
    time.sleep(0.1)
