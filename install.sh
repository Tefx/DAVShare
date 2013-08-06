#!/usr/bin/env bash

aptitude install -y apache2 libapache2-mod-encoding  libapache2-mod-wsgi python-pip python-flask git supervisor python-sqlalchemy sqlite3 python-pysqlite2 python-wtforms
a2enmod dav* encoding rewrite wsgi authn_dbd
pip install watchdog Flask-SQLAlchemy
git clone https://github.com/Tefx/DAVShare.git /var/www/DAVShare
mkdir -p /var/www/webdav/all
python /var/www/DAVShare/web.py
chown www-data /var/www/webdav/ /var/www/DAVShare/ /var/www/DAVShare/DAVShare.db
mv /var/www/DAVShare/config/davshare /etc/apache2/sites-available/
a2ensite davshare
a2dissite default
mv /var/www/DAVShare/config/DAVShare.conf /etc/supervisor/conf.d/
sudo echo "www-data ALL=(ALL) NOPASSWD:/bin/mount, /bin/umount" >> /etc/sudoers
service apache2 restart
service supervisor stop
service supervisor start