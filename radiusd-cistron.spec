Summary:	Cistron RADIUS daemon (with PAM) 
Name:		radiusd-cistron
Version:	1.6.8
Release:	%mkrel 2
License:	GPL
Group:		System/Servers
URL:		http://www.radius.cistron.nl/
Source0:	ftp://ftp.radius.cistron.nl/pub/radius/%{name}-%{version}.tar.gz
Source1:	radiusd.pam.bz2
Source2:	radiusd.init.bz2
Patch0:		%{name}-1.6.6-pam.patch
Patch1:		%{name}-1.6.6-prefix.patch
Patch3:		radiusd-1.6.6-build.patch
Patch4:		radiusd-cistron-no_strip.diff
Requires(post):	rpm-helper
Requires(preun): rpm-helper
BuildRequires:  pam-devel
BuildRequires:  glibc-static-devel
Conflicts:	freeradius
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
RADIUS server with a lot of functions. Short overview: 

- PAM support
- Supports access based on huntgroups
- Multiple DEFAULT entries in users file
- All users file entries can optionally "fall through"
- Caches all config files in-memory
- Keeps a list of logged in users (radutmp file)
- "radwho" program can be installed as "fingerd"
- Logs both UNIX "wtmp" file format and RADIUS detail logfiles
- Supports Simultaneous-Use = X parameter. Yes, this means
  that you can now prevent double logins!

%prep 

%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1
%patch3 -p1
%patch4 -p0

# clean up possible cvs junk.
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

cd raddb
for f in clients users naslist huntgroups ; do cp $f $f-dist ; done
cd ..

%build
%serverbuild
cd src
%make PAM=-DPAM PAMLIB="-lpam -ldl" CFLAGS="$CFLAGS -Wall"
cd ..

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/{%{_sysconfdir}/{,raddb,logrotate.d,pam.d,rc.d/{init.d,rc{0,1,2,3,4,5,6}.d}},%{_bindir},%{_sbindir},%{_mandir}/{,man{1,5,8}},%{_localstatedir}/lib/{,log/{,radacct}}}
install -d %{buildroot}%{_datadir}/radius

# make install
cd src
make install BINDIR=%{buildroot}%{_bindir} \
             SBINDIR=%{buildroot}%{_sbindir} \
             RADIUS_DIR=%{buildroot}%{_sysconfdir}/raddb \
             PAM_DIR=%{buildroot}%{_sysconfdir}/pam.d \
             MANDIR=%{buildroot}%{_mandir} \
             SHAREDIR=%{buildroot}%{_datadir}/radius
install -m0755 radtest %{buildroot}%{_bindir}
cd ..

# do %{_sysconfdir}/raddb
#cd raddb
#install -m640 * %{buildroot}%{_sysconfdir}/raddb
#cd ..

# radwatch
install -m755 scripts/radwatch %{buildroot}%{_sbindir}

# other files
cd redhat
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/pam.d/radius
bzcat %{SOURCE2} > %{buildroot}%{_sysconfdir}/rc.d/init.d/radiusd
chmod 644 %{buildroot}%{_sysconfdir}/pam.d/radius
chmod 755 %{buildroot}%{_sysconfdir}/rc.d/init.d/radiusd
install -m644 radiusd-logrotate %{buildroot}%{_sysconfdir}/logrotate.d/radiusd
cd ..

# man pages
cd doc
for i in 1 8; do
    install -m444 *.$i %{buildroot}%{_mandir}/man$i
done
install -m444 clients.5rad %{buildroot}%{_mandir}/man5/
install -m444 naslist.5rad %{buildroot}%{_mandir}/man5/
cd ..

mkdir -p %{buildroot}/var/log/radacct
for i in radutmp radwtmp radius.log; do
	touch %{buildroot}/var/log/$i
done

rm -f %{buildroot}%{_sysconfdir}/raddb/*-dist
chmod 750 %{buildroot}%{_sysconfdir}/raddb
chmod 640 %{buildroot}%{_sysconfdir}/raddb/*

%post
%_post_service radiusd
touch /var/log/radutmp /var/log/radwtmp /var/log/radius.log

%preun
%_preun_service radiusd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc doc/ChangeLog doc/README* doc/FAQ.txt todo/ 
%doc COPYRIGHT README
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/raddb/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/pam.d/radius
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/radiusd
%config(noreplace) %attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/radiusd
%{_bindir}/radclient
%{_bindir}/radlast
%{_bindir}/radtest
%{_bindir}/radwho
%{_bindir}/radzap
%{_sbindir}/checkrad
%{_sbindir}/radiusd
%{_sbindir}/radrelay
%{_sbindir}/radwatch
%attr(0644,root,root) %{_mandir}/man1/*
%attr(0644,root,root) %{_mandir}/man5/*
%attr(0644,root,root) %{_mandir}/man8/*
%ghost /var/log/radutmp
%ghost /var/log/radwtmp
%ghost /var/log/radius.log
%dir /var/log/radacct
%dir %{_datadir}/radius
%{_datadir}/radius/dictionary*
