FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf 

# COPY build /etc/nginx/html/

EXPOSE 80 80

EXPOSE 443 443

ENTRYPOINT ["nginx", "-g", "daemon off;"]