%define name pl_sshd
%define version 1.0
%define release 4.planetlab%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 3.0
URL: http://www.planet-lab.org

Summary: SSH server config for PlanetLab
Name: %{name}
Version: %{version}
Release: %{release}
Requires: autofs, openssh-server
License: GPL
Group: System Environment/Base
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

Source0: %{name}-%{version}.tar.bz2

%description 
SSH server configuration for PlanetLab nodes. Configures an automounted
directory as source for authorized_keys files and points sshd to that
directory.

%prep
%setup

%build


%install
mkdir -p $RPM_BUILD_ROOT/var/pl_sshd/keys
install -D -m 0755 pl_sshd.sh $RPM_BUILD_ROOT/usr/local/sbin/pl_sshd.sh
install -D -m 0755 pl_sshd $RPM_BUILD_ROOT/etc/init.d/pl_sshd
install -D -m 0755 auto.pl_sshd $RPM_BUILD_ROOT/etc/auto.pl_sshd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir /var/pl_sshd/keys
%attr(0755,root,root) /usr/local/sbin/pl_sshd.sh
%attr(0755,root,root) /etc/init.d/pl_sshd
%attr(0755,root,root) /etc/auto.pl_sshd

%pre


%post
RUNLEVEL=`/sbin/runlevel`

# 1 = install, 2 = upgrade/reinstall
if [ $1 -ge 1 ]; then
    # create the magic directory for automount
    keydir=/var/pl_sshd/keys

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
	#
	# don't try to start/restart various things automatically,
	# it's too ugly (particularly if we're upgrading while
	# connected over ssh)
	#
	echo
	echo "You need to manually restart autofs and sshd, and"
	echo "start the pl_sshd (ssh on port 806) service."
	echo "Make sure you know what you're doing, particularly"
	echo "if you're making this change over an ssh connection."
	echo
    fi
fi

%preun
RUNLEVEL=`/sbin/runlevel`

# 0 = erase, 1 = upgrade
if [ $1 -ge 0 ]; then
	#
	# stop pl_sshd, remove it from rcX.d init dirs, remove link
	# to sshd's pam config
	#
	[ "$RUNLEVEL" = "unknown" ] || /etc/init.d/pl_sshd stop || :
	chkconfig --del pl_sshd
	rm -f /etc/pam.d/pl_sshd

	#
	# remove funky config options for sshd (so that when we restart
	# things will operate normally i.e., without automount magic)
	#
	rm /etc/sysconfig/sshd
	if [ "$RUNLEVEL" != "unknown" ]; then
	    echo
	    echo "You need to manually restart sshd."
	    echo "Make sure you know what you're doing, particularly"
	    echo "if you're making this change over an ssh connection."
	    echo
	fi

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

