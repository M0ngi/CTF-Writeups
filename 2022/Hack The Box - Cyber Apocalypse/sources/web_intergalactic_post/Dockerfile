FROM alpine:edge

# Setup usr
RUN adduser -D -u 1000 -g 1000 -s /bin/sh www

# Install system packages
RUN apk add --no-cache --update supervisor nginx php7-fpm php7-sqlite3 php7-json

# Configure php-fpm and nginx
COPY config/fpm.conf /etc/php7/php-fpm.d/www.conf
COPY config/supervisord.conf /etc/supervisord.conf
COPY config/nginx.conf /etc/nginx/nginx.conf

# Copy challenge files
COPY challenge /www

# Copy flag
RUN RND=$(echo $RANDOM | md5sum | head -c 15) && \
	echo "HTB{f4k3_fl4g_f0r_t3st1ng}" > /flag_${RND}.txt

# Setup permissions
RUN chown -R www:www /var/lib/nginx /www

# Expose the port nginx is listening on
EXPOSE 80

CMD /usr/bin/supervisord -c /etc/supervisord.conf
