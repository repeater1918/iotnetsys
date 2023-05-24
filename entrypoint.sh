#!/bin/sh

# Start Nginx server
nginx -g "daemon off;" &

# Run certbot command for SLL
certbot --nginx -d iotnetsys.net --agree-tos --email jomc7031@uni.sydney.edu.au --non-interactive

# Keep the container running
tail -f /dev/null