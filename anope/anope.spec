Name:		anope
Version:	2.0.7
Release:	1%{?dist}
Summary:	Anope is a set of IRC Services designed for flexibility and ease of use

License:	GPLv2
URL:		https://anope.org
Source0:	https://github.com/anope/anope/releases/download/%{version}/%{name}-%{version}-source.tar.gz

Source10:	anope.service

BuildRequires:	cmake >= 2.4
BuildRequires:	openssl-devel, gnutls-devel
BuildRequires:	openldap-devel
BuildRequires:	mariadb-devel, sqlite-devel
BuildRequires:	pcre-devel, glibc-headers
BuildRequires:	gettext
Requires(pre):		systemd
Requires(post):		systemd
Requires(postun):	systemd
Requires(preun):	systemd

%description
Anope is a set of IRC Services forked from Epona early 2003 to pick up where
Epona had been abandoned. Ever since there have been improvements on quality
and functionality of Anope, resulting in the feature rich set of services we
offer today.

%define extra_modules mysql,ssl_gnutls,ssl_openssl,ldap,ldap_oper,ldap_authentication,sql_oper,sql_log,sqlite,sql_authentication,regex_posix,regex_pcre

%package ldap
Summary:	Anope modules requiring LDAP
Requires:	anope == %{version}
%description ldap
%{summary}

%package sql-sqlite
Summary:	SQLite bindings for Anope
Requires:	anope == %{version}
%description sql-sqlite
%{summary}

%package sql-mysql
Summary:	MySQL bindings for Anope
Requires:	anope == %{version}
%description sql-mysql
%{summary}

%package ssl-gnutls
Summary:	GNUTLS bindings for Anope
Requires:	anope == %{version}
%description ssl-gnutls
%{summary}

%package ssl-openssl
Summary:	OpenSSL bindings for Anope
Requires:	anope == %{version}
%description ssl-openssl
%{summary}

%prep
%setup -q -n %{name}-%{version}-source
# Enable some extra modules
ln -s extra/stats modules/
ln -s extra/m_{%{extra_modules}}.cpp modules/


%build
# CMakeLists.txt uses custom install paths instead of cmake standard ones
# Also, it doesn't look into subdirs of libdir for some reason
%cmake -DREPRODUCIBLE_BUILD=ON \
 -DBIN_DIR:STRING=%{_bindir} \
 -DDB_DIR:STRING=%{_datadir}/%{name} \
 -DCONF_DIR:STRING=%{_datadir}/%{name}/examples \
 -DLIB_DIR:STRING=%{_libdir}/%{name} \
 -DLOCALE_DIR:STRING=%{_datadir}/locale \
 -DEXTRA_LIBS:STRING=%{_libdir}/mysql
make %{?_smp_mflags}


%check
ctest -V %{?_smp_mflags}


%install
%make_install
%find_lang %{name}
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mv %{buildroot}%{_bindir}/geoipupdate.sh %{buildroot}%{_bindir}/anopesmtp %{buildroot}%{_libexecdir}/%{name}
mv %{buildroot}%{_bindir}/services %{buildroot}%{_bindir}/anope
rm -f %{buildroot}%{_bindir}/anoperc
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

install -d %{buildroot}%{_sharedstatedir}/%{name} %{buildroot}%{_sharedstatedir}/%{name}/backups
install -d %{buildroot}%{_sysconfdir}/%{name} %{buildroot}%{_localstatedir}/log/%{name}
install -D -m0644 %{SOURCE10} %{buildroot}%{_unitdir}/anope.service

%files ldap
%{_libdir}/%{name}/modules/m_ldap*.so
%files sql-sqlite
%{_libdir}/%{name}/modules/m_sqlite.so
%files sql-mysql
%{_libdir}/%{name}/modules/m_mysql.so
%files ssl-gnutls
%{_libdir}/%{name}/modules/m_ssl_gnutls.so
%files ssl-openssl
%{_libdir}/%{name}/modules/m_ssl_openssl.so

%files -f %{name}.lang
%doc %{_datadir}/%{name}/examples/

%{_libexecdir}/%{name}/geoipupdate.sh
%{_libexecdir}/%{name}/anopesmtp
%{_bindir}/anope
%dir %attr(750, anope, anope) %{_localstatedir}/log/%{name}/
%dir %attr(750, anope, anope) %{_sharedstatedir}/%{name}/
%dir %attr(750, anope, anope) %{_sharedstatedir}/%{name}/backups
%config(noreplace) %dir %attr(750, anope, anope) %{_sysconfdir}/%{name}/
%{_datadir}/%{name}/modules/webcpanel
%{_unitdir}/anope.service

%{_libdir}/%{name}/modules/*.so
%exclude %{_libdir}/%{name}/modules/m_sqlite.so
%exclude %{_libdir}/%{name}/modules/m_mysql.so
%exclude %{_libdir}/%{name}/modules/m_ssl_*.so
%exclude %{_libdir}/%{name}/modules/m_ldap*.so


%pre
getent group anope >/dev/null || groupadd -r anope
getent passwd anope >/dev/null || \
    useradd -r -g anope -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "IRC Services User" anope
    exit 0
%sysusers_create_inline u anope - "IRC Services User"

%preun
%systemd_preun anope.service

%postun
%systemd_postun_with_restart anope.service

%post
%systemd_post anope.service

%changelog
* Sat Jan 11 2020 Anatole Denis <natolumin@rezel.net> - 2.0.7-1
- Version bump

* Wed Dec 13 2017 Anatole Denis <natolumin@rezel.net> - 2.0.6-1
- Version bump to 2.0.6

* Wed Sep 13 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-5
- Rebuild for CentOS 7.4 and openssl 1.0.2

* Tue Mar 14 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-4
- Create config directory
- Update service file with all relevant directories
- Create backups directory
- Remove logrotate configuration

* Mon Mar 06 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-1
- First packaging
