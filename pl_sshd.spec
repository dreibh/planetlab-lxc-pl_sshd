Summary: SSH server config for PlanetLab
Name: pl_sshd
Version: 1.0
Release: 1
Requires: autofs, openssh-server
Copyright: GPL
URL: http://www.planet-lab.org
Group: System Environment/Base
Source: %{_fullname}.tar.gz

%description 
SSH server configuration for PlanetLab nodes.  Configures an automounted
directory as source for authorized_keys files and points sshd to that
directory.

$Header: /cvs/pl_sshd/pl_sshd.spec,v 1.4 2003/12/01 22:16:47 sjm-pl_sshd Exp $
%prep
%setup

%build


%install
mkdir -p $RPM_BUILD_ROOT/usr/local/sbin
mkdir -p $RPM_BUILD_ROOT/etc/{sysconfig,init.d}
mkdir -p $RPM_BUILD_ROOT/var/pl_sshd/keys
install -m 0755 pl_sshd.sh $RPM_BUILD_ROOT/usr/local/sbin
install -m 0755 pl_sshd $RPM_BUILD_ROOT/etc/init.d
install -m 0755 auto.pl_sshd $RPM_BUILD_ROOT/etc

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0755,root,root) /usr/local/sbin/pl_sshd.sh
%attr(0755,root,root) /etc/init.d/pl_sshd
%attr(0755,root,root) /etc/auto.pl_sshd

%pre


%post
RUNLEVEL=`/sbin/runlevel`

if [ "$1" -ge 1 ]; then
	# create the magic directory for automount
	keydir=/var/pl_sshd/keys
	[ -d $keydir ] || mkdir -p $keydir

	# add appropriate entry to auto.master
	auto_master=/etc/auto.master
	auto_master_entry="$keydir /etc/auto.pl_sshd"
	grep -qF "$auto_master_entry" $auto_master || \
	    echo $auto_master_entry >>$auto_master

	#
	# use the sysconfig file to tell our system sshd to look in the
	# magic location for authorized_keys files
	#
	sysconfig_sshd=/etc/sysconfig/sshd
	[ -r $sysconfig_sshd ] && \
	    mv $sysconfig_sshd $sysconfig_sshd.pl_sshd
	echo "OPTIONS='-o \"AuthorizedKeysFile $keydir/%u/authorized_keys\"'" \
	    >$sysconfig_sshd

	# link sshd pam config to pl_sshd so that we can actually login
	pam_pl_sshd=/etc/pam.d/pl_sshd
	[ -r $pam_pl_sshd ] || ln -s sshd $pam_pl_sshd

	chkconfig --add pl_sshd

	if [[ "$RUNLEVEL" != "unknown" ]]; then
		/etc/init.d/autofs restart
		/etc/init.d/sshd restart
		/etc/init.d/pl_sshd start
	fi
fi

%preun
RUNLEVEL=`/sbin/runlevel`

if [ "$1" -ge "0" ]; then
	#
	# stop pl_sshd, remove it from rcX.d init dirs, remove link
	# to sshd's pam config
	#
	[ "$RUNLEVEL" != "unknown" ] && /etc/init.d/pl_sshd stop
	chkconfig --del pl_sshd
	rm -f /etc/pam.d/pl_sshd

	#
	# remove funky config options for sshd (so that when we restart
	# things will operate normally i.e., without automount magic),
	# then restart
	#
	rm /etc/sysconfig/sshd
	[ "$RUNLEVEL" != "unknown" ] && /etc/init.d/sshd restart

	#
	# stop automounter, remove entry from auto.master, restart if
	# necessary
	#
	[ "$RUNLEVEL" != "unknown" ] && /etc/init.d/autofs stop
	auto_master=/etc/auto.master
	mv $auto_master $auto_master.pl_sshd.preun
	sed -e '\,^/var/pl_sshd/keys,d' $auto_master.pl_sshd.preun \
	    >$auto_master

	[ "$RUNLEVEL" != "unknown" ] && /etc/init.d/autofs start
fi


%postun


%changelog
* Mon Dec  1 2003 Steve Muir <smuir@cs.princeton.edu>
- initial creation from files in sidewinder repository

