#!/bin/bash
sudo su - ubuntu

HOME="/home/ubuntu/"
MONGO_USER=${MONGO_USER}
MONGO_PWD=${MONGO_PWD}
MONGO_DB=${MONGO_DB}

wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl enable mongod

echo '@reboot sudo service mongod start | crontab'

cd $HOME

echo "
const conn = new Mongo();
const db = conn.getDB('admin');

db.createUser({
  user: '$MONGO_USER',
  pwd: '$MONGO_PWD',
  roles: [
    { role:'userAdminAnyDatabase', db: 'admin' },
    { role:'readWriteAnyDatabase', db: 'admin' },
    { role:'dbAdminAnyDatabase', db: 'admin' },
  ]
});
" > create_admin.js

sudo service mongod start

sleep 1
while ! sudo lsof -i:27017 | grep "mongodb" -q; do
    sleep 1
done

sudo sed -i 's/127.0.0.1/0.0.0.0/' /etc/mongod.conf

mongo create_admin.js

sudo service mongod restart