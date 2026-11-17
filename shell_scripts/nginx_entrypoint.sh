#!/bin/sh

nginx -c /etc/nginx/nginx.conf -e /var/log/nginx/error.log -g 'daemon off;'
