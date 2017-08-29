# -*- coding:utf-8 -*-
import binascii as B
import hashlib
url = "channel=qqapp&deviceId=355592070880643&deviceType=Nexus 5X&page=4&phoneType=andr&systemVer=23&talk_token=jj0dYZjvGhkNvG7r1svc8rGuEDd9DD1KfJ1s/q7ItTdsVwJ16PLqJ9fds/uopwrUPHWE5E-5jXSqVNvxOAIzDnN/lTiC/Rmg79E3Pno=&userId=37160010&version=4.7.6!08za$8gQKZCt^ME"
def md5():
    m = hashlib.md5()
    m.update(url)
    value = m.digest()
    h = B.b2a_hex(value)
    print h.upper()

if __name__ == "__main__":
    md5()
