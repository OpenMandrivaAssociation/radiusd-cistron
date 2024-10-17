Summary:	Cistron RADIUS daemon (with PAM) 
Name:		radiusd-cistron
Version:	1.6.8
Release:	2
License:	GPL
Group:		System/Servers
URL:		https://www.radius.cistron.nl/
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


%changelog
* Sun Sep 07 2008 Oden Eriksson <oeriksson@mandriva.com> 1.6.8-1mdv2009.0
+ Revision: 282149
- 1.6.8
- drop P2, it's in there
- don't strip at install (P4)

* Fri Aug 01 2008 Thierry Vignaud <tvignaud@mandriva.com> 1.6.6-13mdv2009.0
+ Revision: 260011
- rebuild

* Fri Jul 25 2008 Thierry Vignaud <tvignaud@mandriva.com> 1.6.6-12mdv2009.0
+ Revision: 247814
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 1.6.6-10mdv2008.1
+ Revision: 140743
- restore BuildRoot

  + Thierry Vignaud <tvignaud@mandriva.com>
    - kill re-definition of %%buildroot on Pixel's request

  + Emmanuel Andry <eandry@mandriva.org>
    - uncompress patches

* Tue Oct 02 2007 Andreas Hasenack <andreas@mandriva.com> 1.6.6-10mdv2008.0
+ Revision: 94819
- fix rpm-helper requires
- fix pam config file (#31654)
- fix build
- import radiusd-cistron



* Wed Nov 12 2003 Michael Scherer <scherer.michael@free.fr> 1.6.6-9mdk 
- BuildRequires ( glibc-static-devel )

* Thu Jul 10 2003 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-8mdk
- rebuild

* Sun Jun 29 2003 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-7mdk
- added P2 which addresses CAN-2003-0450

* Fri Apr 25 2003 Frederic Lepied <flepied@mandrakesoft.com> 1.6.6-6mdk
- added BuildRequires

* Thu Jan 23 2003 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-5mdk
- package should not own /var/log
- fix no-prereq-on rpm-helper
- bzip S1 & S2
- misc spec file fixes

* Mon Jan 20 2003 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-4mdk
- build release
- misc spec file fixes

* Mon May 27 2002 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-3mdk
- radclient was missing (duh!) reported by Marcin Klimowski

* Mon May 20 2002 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-2mdk
- rebuilt with gcc3.1

* Sat May 4 2002 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.6.6-1mdk
- new version
- rediff P0
- remove P1
- misc spec file fixes
- added S2
- added new P1

* Fri Aug 31 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.6.4-3mdk
- rebuild

* Tue Apr 24 2001 Frederic Lepied <flepied@mandrakesoft.com> 1.6.4-2mdk
- recompiled for pam 0.74

* Sat Dec 16 2000 Frederic Lepied <flepied@mandrakesoft.com> 1.6.4-1mdk
- first release

* Thu Sep 14 2000 Rodrigo Barbosa <rodrigob@conectiva.com>
- Only use gcc-stackguard if avaliable. Andreas: added CPP
  for stackguard
- Adopted rpm macros
- Removed referenced to gzipman

* Wed May 17 2000 Elvis Pfützenreuter <epx@conectiva.com>
- using stackguard compiler
- allows non-root compilation
- /usr/s?bin files put explicit in %%files, %%defattr included

* Tue Dec 14 1999 Guilherme Wunsch Manika <gwm@conectiva.com>
- Included es init script translation

* Mon Nov 29 1999 Rudá Moura <ruda@conectiva.com>
- Updated to version 1.6.1
- Compressed man pages
- Corrected (I hope) a bug in radiusd-init

* Thu Jul 01 1999 Rodrigo Parra Novo <rodarvus@conectiva.com>
- Fixed radiusd.init (me/cavassin)
- Fixed radwatch.sh (cavassin)

* Sun Jun 20 1999 Conectiva <dist@conectiva.com>
- Recompiled with glibc 2.1.x, egcs 1.1.x, rpm 3.0.x and kernel 2.2.x

* Sun Jun 20 1999 Arnaldo Carvalho de Melo <acme@conectiva.com>
- sources recompressed

* Sat Nov 21 1998 Tim Hockin <thockin@ais.net>
- Based on work by Christopher McCrory <chrismcc@netus.com>
- Build with PAM
- Included pam.d/radius
- Fixed some small errors in this spec
- Changed to build to BuildRoot
- Changed Release to "beta11" from "1"
- Included users, naslist, huntgroups, clients files, not just -dist

* Tue Oct 27 1998 Mauricio Mello de Andrade <mandrade@mma.com.br>
- Corrected the script to Start/Stop the Radius under RH5.x
- Included the script to Rotate Radius Logs under RedHat
- Checkrad Utility now works fine with Cyclades PathRas

