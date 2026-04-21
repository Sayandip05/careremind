FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Create SSL directory (certs mounted at runtime)
RUN mkdir -p /etc/nginx/ssl

# Create certbot webroot
RUN mkdir -p /var/www/certbot

# Create custom error page
RUN echo '{"error":"Service temporarily unavailable"}' > /usr/share/nginx/html/50x.html

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
