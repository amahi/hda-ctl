%global rubyrelease 2.0.0
%define systemd_dir %{_prefix}/lib/systemd/system

Name:           hda-ctl
Version: 4.2.21
Release:        1

Summary:        hda-ctl is the Amahi HDA daemon.

Group:          System Environment/Daemons
License:        GPL
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: hda-platform >= 6.0.0
Requires: dnsmasq, sudo >= 1.7.2
Requires: mariadb-server samba httpd
Requires: ruby(release) = %{rubyrelease}
Requires: monit perl-Authen-PAM fpaste
Requires: ruby-mysql ruby-libs ruby-augeas rubygem(bundler) rubygem(ruby-dbus)
Requires: perl-Authen-PAM perl-libwww-perl perl-LWP-Protocol-https wget curl
Requires: cadaver php php-mysqlnd perl-URI filesystem rsync cronie pmount
Requires:         systemd
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%define debug_package %{nil}

%description
hda-ctl is the Amahi HDA daemon process.

%prep
%setup -q

make hda-ctl-hup

%build


%install
rm -rf %{buildroot}

%{__mkdir} -p %{buildroot}%{_bindir}
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__mkdir} -p %{buildroot}/var/cache
%{__mkdir} -p %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sudoers.d
%{__mkdir} -p %{buildroot}/var/hda
%{__mkdir} -p %{buildroot}/usr/share/hda-ctl
%{__mkdir} -p %{buildroot}/etc/skel/Desktop
%{__mkdir} -p %{buildroot}/root/Desktop
%{__mkdir} -p %{buildroot}%{systemd_dir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d

%{__install} -m 755 -p hda-ctl hda-install %{buildroot}%{_bindir}
%{__install} -m 755 -p hda-settings hda-alias hda-install-file %{buildroot}%{_bindir}
%{__install} -m 755 -p hda-register-apps hda-install-gem %{buildroot}%{_bindir}
%{__install} -m 755 -p hda-change-gw hda-change-dns amahi-installer hda-php-zone-change hda-fix-sudoers %{buildroot}%{_bindir}
# FIXME - remove after a while. added on Mon Feb 28 01:16:51 PST 2011
%{__install} -m 755 -p hda-upgrade-amahi5-to-amahi6 %{buildroot}%{_bindir}
%{__install} -m 4755 -p hda-ctl-hup %{buildroot}%{_bindir}
%{__install} -m 0440 -p hda-privs %{buildroot}%{_sysconfdir}/sudoers.d/amahi
%{__install} -m 0644 -p hda-ctl.service %{buildroot}%{systemd_dir}/hda-ctl.service
%{__install} -p hda-ctl.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/hda-ctl
%{__install} -p amahi-hda %{buildroot}/usr/share/hda-ctl/amahi-hda
%{__install} -p amahi-installer.initscript %{buildroot}%{_initrddir}/amahi-installer
%{__install} -m 0644 -p hda-ctl.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/hda-ctl

%{__cp} -a desktop-icons/ %{buildroot}/etc/skel/Desktop
%{__cp} -a desktop-icons/ %{buildroot}/root/Desktop
%{__cp} -a web-installer %{buildroot}/usr/share/hda-ctl/

# periodic updates
%{__mkdir} -p %{buildroot}%{_sysconfdir}/cron.hourly
%{__install} -m 700 -p hda-update %{buildroot}%{_sysconfdir}/cron.hourly

# base initialitation
%{__cp} -a httpd %{buildroot}/usr/share/hda-ctl/

# calendar server non-destructive initialitation
%{__mkdir} -p %{buildroot}/var/hda/calendar
%{__mkdir} -p %{buildroot}/var/hda/calendar/logs
%{__mkdir} -p %{buildroot}/var/hda/calendar/html
%{__mkdir} -p %{buildroot}/var/hda/calendar/locks

# file server non-destructive initialization for later
%{__cp} -a samba %{buildroot}/usr/share/hda-ctl/
%{__mkdir} -p %{buildroot}/var/hda/files/Backups
%{__mkdir} -p %{buildroot}/var/hda/files/Books
%{__mkdir} -p %{buildroot}/var/hda/files/Docs
%{__mkdir} -p %{buildroot}/var/hda/files/Videos
%{__mkdir} -p %{buildroot}/var/hda/files/Movies
%{__mkdir} -p %{buildroot}/var/hda/files/Music
%{__mkdir} -p %{buildroot}/var/hda/files/Pictures
%{__mkdir} -p %{buildroot}/var/hda/files/Public

%clean
rm -rf %{buildroot}

%pre

%post
%systemd_post hda-ctl.service
if [ $1 -eq 1 ] ; then 
    # initial install
    /sbin/chkconfig --add amahi-installer
fi

%{__mkdir} -p /var/hda/files

if [[ -e /var/cache/hda-ctl.cache ]]; then
    if grep -q yes /var/cache/hda-ctl.cache ; then
        (/usr/sbin/usermod -a -G users apache) || true
    fi
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
%systemd_preun hda-ctl.service
if [ $1 -eq 0 ]; then
    # removal, not upgrade
    /sbin/chkconfig --del amahi-installer
fi

%postun
%systemd_postun_with_restart hda-ctl.service

%files
%defattr(-,root,root,-)
%{_bindir}/amahi-installer
%{_bindir}/hda-alias
%{_bindir}/hda-change-dns
%{_bindir}/hda-change-gw
%{_bindir}/hda-ctl
%{_bindir}/hda-fix-sudoers
%{_bindir}/hda-install
%{_bindir}/hda-install-file
%{_bindir}/hda-install-gem
%{_bindir}/hda-php-zone-change
%{_bindir}/hda-register-apps
%{_bindir}/hda-settings
%{_bindir}/hda-upgrade-amahi5-to-amahi6
%{_sysconfdir}/sysconfig/hda-ctl
%{_sysconfdir}/skel/Desktop
/root/Desktop/*
%{_sysconfdir}/cron.hourly/hda-update
%attr(0440, root, root)%{_sysconfdir}/sudoers.d/amahi
%ghost %attr(0775, apache, users) /var/hda/files
%attr(4755, root, root) %{_bindir}/hda-ctl-hup
%{_initrddir}/amahi-installer
/usr/share/hda-ctl/*
%attr(755, apache, apache) /var/hda/calendar
%{systemd_dir}/hda-ctl.service
%config(noreplace) %{_sysconfdir}/logrotate.d/hda-ctl

%changelog
* Mon Mar  4 2013 carlos puchol
- add logrotate
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
