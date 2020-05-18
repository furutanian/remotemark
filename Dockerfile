FROM fedora

LABEL 'maintainer=Furutanian <furutanian@gmail.com>'

ARG http_proxy
ARG https_proxy

RUN set -x \
	&& dnf install -y \
		httpd \
		ruby \
		rubygem-sqlite3 \
		git \
		procps-ng \
		net-tools \
		diffutils \
	&& rm -rf /var/cache/dnf/* \
	&& dnf clean all

# git clone remotemark しておくこと
COPY remotemark /var/www/cgi-bin
RUN cp /var/www/cgi-bin/dot.htaccess /var/www/cgi-bin/.htaccess

RUN mv /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.org \
	&& cat /etc/httpd/conf/httpd.conf.org \
		| sed '/^<Directory "\/var\/www\/cgi-bin">/,/^</s/AllowOverride None/AllowOverride All/' \
		| sed '/^<Directory "\/var\/www\/cgi-bin">/,/^</s/Options None/Options All/' \
		> /etc/httpd/conf/httpd.conf \
	&& diff -C 2 /etc/httpd/conf/httpd.conf.org /etc/httpd/conf/httpd.conf \
	|| echo '/etc/httpd/conf/httpd.conf changed.'
RUN systemctl enable httpd

EXPOSE 80

# Dockerfile 中の設定スクリプトを抽出するスクリプトを出力、実行
COPY Dockerfile .
RUN echo $'\
cat Dockerfile | sed -n \'/^##__BEGIN/,/^##__END/p\' | sed \'s/^#//\' > startup.sh\n\
' > extract.sh && bash extract.sh

# docker-compose up の最後に実行される設定スクリプト
##__BEGIN__startup.sh__
#
#	chown -v apache:apache /var/www/cgi-bin/data
#	if [ -v http_proxy ]; then
#		mv /var/www/cgi-bin/remotemark.conf /var/www/cgi-bin/remotemark.conf.org
#		cat /var/www/cgi-bin/remotemark.conf.org \
#			| sed 's!\(:PROXY] = \).*!\1"'$http_proxy'"!' \
#			> /var/www/cgi-bin/remotemark.conf
#		diff -C 2 /var/www/cgi-bin/remotemark.conf.org /var/www/cgi-bin/remotemark.conf
#	fi
#	echo 'startup.sh done.'
#
##__END__startup.sh__

