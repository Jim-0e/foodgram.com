FROM nginx:1.22.1  

# COPY nginx.conf /etc/nginx/templates/default.conf.template 
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

CMD nginx -g 'daemon=off;'