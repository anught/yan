#!/usr/bin/env python

import hashlib
import base64

# in put svpgwdid + cid + 0x00
def hi3_auth(gwid,cid):
    auth = hashlib.sha512()
    auth.update((gwid + cid).ljust(256,'\0'))
    output = base64.b64encode(auth.digest())

    print output

gwid = 'INA'
cid = 'INA891'

hi3_auth(gwid,cid)




