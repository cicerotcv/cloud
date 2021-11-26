#!/bin/bash

NPM_GLOBAL_DIR="/home/ubuntu/.npm-global"
SERVER_DIR="/home/ubuntu/server"

NODE_PORT=8080
NODE_SECRET=${NODE_SECRET}

MONGO_PORT=27017
MONGO_USER=${MONGO_USER}
MONGO_PWD=${MONGO_PWD}
MONGO_HOST=${MONGO_HOST}
MONGO_DB=${MONGO_DB}

sudo apt update && sudo apt upgrade -y
sudo apt install build-essential -y

# instala versão mais atual do node
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# verifica se o npm global está configurado
if [[ -d $NPM_GLOBAL_DIR  && $(npm get prefix) == $NPM_GLOBAL_DIR ]]; then
    echo "NPM_GLOBAL_DIR already set as $NPM_GLOBAL_DIR"
else
    echo ""
    echo "Setting NPM_GLOBAL_DIR as $NPM_GLOBAL_DIR";
    echo ""
    mkdir $NPM_GLOBAL_DIR
    npm config set prefix "$NPM_GLOBAL_DIR"
fi

export PATH=$NPM_GLOBAL_DIR/bin:$PATH

if [ -d "$SERVER_DIR" ]; then
    cd $SERVER_DIR
    git pull
else
    echo $'\nCloning repository\n'
    git clone https://github.com/cicerotcv/cloud-server $SERVER_DIR
fi

cd $SERVER_DIR

# se a porta estiver em uso,
# finaliza o serviço que está utilizando
if [[ $(sudo lsof -t -i:$NODE_PORT) != "" ]]; then
    sudo kill -9 $(sudo lsof -t -i:$NODE_PORT)
fi

# set node server credentials
echo "NODE_PORT=$NODE_PORT" >> .env
echo "NODE_SECRET=$NODE_SECRET" >> .env

# set mongo db related env. variables
echo "MONGO_PORT=$MONGO_PORT" >> .env
echo "MONGO_USER=$MONGO_USER" >> .env
echo "MONGO_PWD=$MONGO_PWD" >> .env
echo "MONGO_HOST=$MONGO_HOST" >> .env
echo "MONGO_DB=$MONGO_DB" >> .env

echo $'\nInstalling dependencies\n'

npm install

echo $'\nBuilding application\n'

npm run build

echo $'\Running application\n'

NODE_ENV="production" npm start
