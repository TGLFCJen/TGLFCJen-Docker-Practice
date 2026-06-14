FROM nginx:alpine

COPY index.html /usr/share/nginx/html 

EXPOSE 80

CMD ["nginx", "-g", "daemon off;", "-c", "/etc/nginx/my-custom-config.conf"]

