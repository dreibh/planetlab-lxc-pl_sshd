Summary: SSH server config for PlanetLab
Name: pl_sshd
Version: 0.1
Release: 1
Requires: automount, sshd
Copyright: GPL
URL: http://www.planet-lab.org
Group: System Environment/Base
Source: %{_fullname}.tar.gz

%description 
SSH server configuration for PlanetLab nodes.  Configures an automounted
directory as source for authorized_keys files and points sshd to that
directory.

Created from $Header$.
%prep
%setup

%build


%install
install -m 0755 -o root -g root pl_sshd.sh $RPM_BUILD_ROOT/usr/local/sbin
install -m 0755 -o root -g root pl_sshd $RPM_BUILD_ROOT/etc/init.d
install -m 0755 -o root -g root auto.pl_sshd $RPM_BUILD_ROOT/etc
echo "OPTIONS='-p 806'" >$RPM_BUILD_ROOT/etc/sysconfig/sshd

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
	chkconfig --add pl_sshd

	if [[ "$RUNLEVEL" != "unknown" ]]; then
		/etc/init.d/pl_sshd restart
	fi
fi

%preun
if [ "$1" = 0 ]; then
	chkconfig --del pl_sshd
fi


%postun


%changelog
* Tue Nov 25 2003 Steve Muir <smuir@cs.princeton.edu>
- fixed a couple of Node Manager bugs:
  - bootstrapping pl_conf state when boot server unreachable
  - canonical hostnames should be all lower-case
- fixup UID and GID of users within vservers to match real world
- enable access to dynamic slices through port 806 sshd

* Sun Oct 26 2003 Aaron Klingaman <Aaron.L.Klingaman@intel.com>
- readded start/stop only when runlevel is known, for install purposes

* Thu Oct 16 2003 Jeff Sedayao <Jeff.Sedayao@intel.com>
- Fixed bug in pl_conf  - it was getting negative wait times.  Also added
  duke4 as a trusted user. 

* Tue Oct  8 2003 Jeff Sedayao <Jeff.Sedayao@intel.com>
- Removed special fetch login from init function, updated release

* Tue Oct  7 2003 Jeff Sedayao <Jeff.Sedayao@intel.com>
- Moved special fetch login into main loop, fix account deletion
  problem

* Tue Oct  7 2003 Aaron Klingaman <Aaron.L.Klingaman@intel.com>
- Commented out code to start pl_* upon install

* Wed Aug 26 2003 Tammo Spalink <tammo.spalink@intel.com>
- Initial build.

