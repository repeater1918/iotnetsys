FROM nginx:latest

# Install required packages
RUN apt-get update \
    && apt-get install -y sudo \
    && apt-get install -y python3-acme python3-certbot python3-mock python3-openssl python3-pkg-resources python3-pyparsing python3-zope.interface \
    && apt-get install -y python3-certbot-nginx

COPY nginx.conf /etc/nginx/nginx.conf 
COPY index.html /etc/nginx/html/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 80 443

CMD ["/entrypoint.sh"]
