#!/bin/sh
#
# this wrapper runs sshd on an alternate port with a different argv[0]
# and PID file (rather annoyingly, the latter has to be specified
# explicitly even if argv[0] is changed).
#
# the alternate port is necessary so we can have two instances of sshd
# running, the different name and PID file are required so that stopping
# the standard sshd won't affect this one.
#
# we use port 806 unless there is a '-p' argument specifying a different
# port.  we also have to specify a different PID file so that one sshd
# doesn't clobber the other's PID file.
#
# XXX - unfortunately the standard init.d/sshd script is fairly brutal
# when stopping sshd processes - it will stop anything that looks
# remotely like sshd.  the measures taken here still don't prevent that
# but i have decided that restarting/stopping sshd should be sufficiently
# rare that it's not worth worrying about to any greater extent.
#
name=pl_sshd
echo "$@" | grep -q -- '-p[ 0-9]' || port='-p 806'

exec -a $name /usr/sbin/sshd -o "PidFile /var/run/$name.pid" $port "$@"
