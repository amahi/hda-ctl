Name:           hda-ctl
Version: 4.2.3
Release:        1

Summary:        hda-ctl is the Amahi HDA daemon.

Group:          System Environment/Daemons
License:        GPL
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: hda-platform >= 6.0.0
Requires: bind bind-utils caching-nameserver
Requires: sudo >= 1.7.2
Requires: dhcp mysql-server samba httpd
Requires: monit perl-Authen-PAM fpaste
Requires: ruby ruby-mysql ruby-libs ruby-devel eruby ruby-augeas
Requires: ruby-irb ruby-racc rubygem-rdoc eruby-libs
Requires: perl-Authen-PAM perl-libwww-perl
Requires: cadaver php php-mysql perl-URI filesystem
Requires: rubygem-passenger rsync
#Requires: ruby-bdb

BuildRequires:      gcc

%define debug_package %{nil}

%description
hda-ctl is the Amahi HDA daemon process.

%prep
%setup -q

make hda-ctl-hup

%build


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT/var/cache
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.d
mkdir -p $RPM_BUILD_ROOT/var/hda
mkdir -p $RPM_BUILD_ROOT/var/hda/elevated
mkdir -p $RPM_BUILD_ROOT/usr/share/hda-ctl
mkdir -p $RPM_BUILD_ROOT/etc/skel/Desktop
mkdir -p $RPM_BUILD_ROOT/root/Desktop

install -m 755 -p hda-ctl hda-install $RPM_BUILD_ROOT%{_bindir}
(cd $RPM_BUILD_ROOT%{_bindir} && ln -sf hda-install hda-new-install)
install -m 755 -p hda-settings hda-alias hda-install-file $RPM_BUILD_ROOT%{_bindir}
install -m 755 -p hda-register-apps hda-install-gem $RPM_BUILD_ROOT%{_bindir}
install -m 755 -p hda-change-gw hda-change-dns amahi-installer hda-php-zone-change hda-fix-sudoers $RPM_BUILD_ROOT%{_bindir}
# FIXME - remove after a while. added on Mon Feb 28 01:16:51 PST 2011
install -m 755 -p hda-upgrade-amahi5-to-amahi6 $RPM_BUILD_ROOT%{_bindir}
install -m 4755 -p hda-ctl-hup $RPM_BUILD_ROOT%{_bindir}
install -m 0440 -p hda-privs $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.d/amahi
install -p hda-ctl.initscript $RPM_BUILD_ROOT%{_initrddir}/hda-ctl
install -p hda-ctl.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/hda-ctl
install -p amahi-hda $RPM_BUILD_ROOT/usr/share/hda-ctl/amahi-hda
install -p amahi-installer.initscript $RPM_BUILD_ROOT%{_initrddir}/amahi-installer

rsync -Ca desktop-icons/ $RPM_BUILD_ROOT/etc/skel/Desktop
rsync -Ca desktop-icons/ $RPM_BUILD_ROOT/root/Desktop
rsync -Ca web-installer $RPM_BUILD_ROOT/usr/share/hda-ctl/

# periodic updates
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.hourly
install -m 700 -p hda-update $RPM_BUILD_ROOT%{_sysconfdir}/cron.hourly

# base initialitation
rsync -Ca httpd $RPM_BUILD_ROOT/usr/share/hda-ctl/

# calendar server non-destructive initialitation
mkdir -p $RPM_BUILD_ROOT/var/hda/calendar
mkdir -p $RPM_BUILD_ROOT/var/hda/calendar/logs
mkdir -p $RPM_BUILD_ROOT/var/hda/calendar/html
mkdir -p $RPM_BUILD_ROOT/var/hda/calendar/locks

# file server non-destructive initialization for later
rsync -Ca samba $RPM_BUILD_ROOT/usr/share/hda-ctl/
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Backups
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Books
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Docs
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Movies
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Music
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Pictures
mkdir -p $RPM_BUILD_ROOT/var/hda/files/Public

%clean
rm -rf $RPM_BUILD_ROOT

%pre

%post
/sbin/chkconfig --add hda-ctl
/sbin/chkconfig --add amahi-installer

mkdir -p /var/hda/files

if [[ -e /var/cache/hda-ctl.cache ]]; then
	if grep -q yes /var/cache/hda-ctl.cache ; then
		(/usr/sbin/usermod -a -G users apache) || true

		# FIXME - added on 3/24/09, to be removed after 5/30/09
		# make the platform default
		(/bin/mv -f /etc/httpd/conf.d/04-platform.conf /etc/httpd/conf.d/01-platform.conf > /dev/null 2>&1) || true
		(/bin/rm -rf /var/hda/as > /dev/null 2>&1) || true
		(/bin/rm -rf /etc/httpd/conf.d/01-as.conf > /dev/null 2>&1) || true

		# FIXME: to be removed in the next major version of amahi 6.0
		INSUDOERS=`grep '^#includedir /etc/sudoers.d' /etc/sudoers`;
		if [ -z "$INSUDOERS" ]; then
			echo "#includedir /etc/sudoers.d" >> /etc/sudoers 
		fi
	fi
else
	(cd /var/hda/files/ && mkdir -p Backups Books Docs Movies Music Pictures Public && chown 500:100 . * && chmod 775 *)
fi

if [ -f %{_sysconfdir}/samba/smbpasswd ]; then
	mv -f %{_sysconfdir}/samba/smbpasswd /tmp/
fi
if [ -f %{_sysconfdir}/samba/smbusers ]; then
	mv -f %{_sysconfdir}/samba/smbusers /tmp/
fi
if [ -f %{_sysconfdir}/samba/secrets.tdb ]; then
	mv -f %{_sysconfdir}/samba/secrets.tdb /tmp/
fi

%preun

if [ "$1" = 0 ]; then
	# not an update, a complete uninstall
	/sbin/service hda-ctl stop > /dev/null 2>&1 || true
	/sbin/chkconfig --del hda-ctl
	/sbin/chkconfig --del amahi-installer
else
	# an update
	/sbin/service hda-ctl restart > /dev/null 2>&1 || true
fi

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_sysconfdir}/sysconfig/hda-ctl
%{_sysconfdir}/skel/Desktop
/root/Desktop/*
%{_sysconfdir}/cron.hourly/hda-update
%attr(0440, root, root)%{_sysconfdir}/sudoers.d/amahi
%ghost %attr(-, 500, 100) /var/hda/files
%attr(4755, root, root) %{_bindir}/hda-ctl-hup
%{_initrddir}/hda-ctl
%{_initrddir}/amahi-installer
/usr/share/hda-ctl/*
/var/hda/elevated
%attr(755, apache, apache) /var/hda/calendar

%changelog
* Sun Jan 13 2013 carlos puchol
- rename to hda-ctl and start on f18 port
* Sun Mar 11 2007 carlos puchol
- added hda.repo, and many other improvements
* Sat Mar 10 2007 carlos puchol
- add hda-install skeleton
* Sat Dec 09 2006 carlos puchol
- initial file
* Tue Feb 20 2006 carlos puchol
- add hda-ctl-hup, with uid
