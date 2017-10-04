#!/usr/bin/env python

import hashlib
import base64

# in put svpgwdid + cid + 0x00
def hi3_auth(svpgwid,cid):
    auth = hashlib.sha512()
    auth.update((svpgwid + cid).ljust(256,'\0'))
    output = base64.b64encode(auth.digest())

    print output

svpgwid = 'INA'
cid = 'INA891'

hi3_auth(svpgwid,cid)




