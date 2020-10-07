# shell script to copy over production ini files on the production server

cd /home/ubuntu/webapp_amazons

# Update to newest Nginx Config.
sudo cp nginx_amazons.conf /etc/nginx/sites-enabled/nginx_amazons.conf
sudo rm /etc/nginx/sites-enabled/amazons
sudo mv /etc/nginx/sites-enabled/nginx_amazons.conf /etc/nginx/sites-enabled/amazons

# Update Supervisor Config
# sudo rm /etc/supervisor/conf.d/amazons.conf
# sudo cp amazons.conf /etc/supervisor/conf.d/amazons.conf

# Reload supervisor and nginx
# sudo supervisorctl reload
sudo service nginx reload
