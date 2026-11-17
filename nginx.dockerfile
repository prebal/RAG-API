FROM nginx:stable-alpine3.24

COPY nginx.conf /etc/nginx/nginx.conf

COPY frontend/ /var/www/frontend

COPY shell_scripts/nginx_entrypoint.sh /nginx_entrypoint.sh

RUN chmod +x /nginx_entrypoint.sh 

ENTRYPOINT ["/nginx_entrypoint.sh"]



