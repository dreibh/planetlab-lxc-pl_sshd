#!/usr/bin/python
#
# Copyright 2005 Princeton University
#
# autofs(5) executable map for /var/pl_sshd/keys/
#

import cStringIO
import os
import pwd
import pycurl
import sys



def abort(msg):
    print >>sys.stderr, msg
    sys.exit(1)
    
if len(sys.argv) != 2:
    print >>sys.stderr, "usage:\n    %s <slicename>" % sys.argv[0]
    sys.exit(1)

slice = sys.argv[1]
try:
    (name, passwd, uid, gid, comment, home, sh) = pwd.getpwnam(slice)
except KeyError, ex:
    abort("no such user: " + slice)

result = "--bind,-r :"

sshdir = home + "/.ssh"
keyfile = sshdir + "/authorized_keys"

# check whether authorized_keys exists in the real home dir
if os.access(keyfile, os.R_OK):
    # yes - use it
    result += sshdir
else:
    # no - look in the vserver
    # try to get keys from KeySensor
    sys.stderr.write("Retrieving SSH keys for %s... " % slice)
    pycurl.global_init(pycurl.GLOBAL_ALL)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "http://localhost:815/keys?slice=" + slice)
    out = cStringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, out.write)
    c.setopt(pycurl.NOSIGNAL, 1)
    c.setopt(pycurl.TIMEOUT, 1)
    try:
        c.perform()
        rc = c.getinfo(pycurl.HTTP_CODE)
        if rc != 200:
            abort("HTTP error: " + str(rc))
    except pycurl.error, ex:
        if ex[0] == 28:  # XXX - pycurl doesn't define error constants
            abort("timed-out")
        abort("curl error: " + ex[1])
    keydata = out.getvalue()

    # try to update keyfile
    vsbase = "/vservers/" + slice
    os.chroot(vsbase)
    os.setgid(gid)
    os.setuid(uid)
    if not os.path.isdir(sshdir):
        os.mkdir(sshdir, 0700)
        
    f = file(keyfile, "w")
    f.write(keydata)
    f.close()
    os.chmod(keyfile, 0600)
    result += vsbase + sshdir
    print >>sys.stderr, "succeeded."

print result
