FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf 

COPY index.html /etc/nginx/html/

EXPOSE 80 80

EXPOSE 443 443

ENTRYPOINT ["nginx", "-g", "daemon off;"]
