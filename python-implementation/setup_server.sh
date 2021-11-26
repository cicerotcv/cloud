#!/bin/bash

NPM_GLOBAL_DIR="/home/ubuntu/.npm-global"
SERVER_DIR="/home/ubuntu/server"

NODE_DEV_PORT=3333
NODE_PROD_PORT=8080
MONGO_ADMIN_USER=${MONGO_ADMIN_USER}
MONGO_ADMIN_PWD=${MONGO_ADMIN_PWD}

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
if [[ $(sudo lsof -t -i:$NODE_PROD_PORT) != "" ]]; then
    sudo kill -9 $(sudo lsof -t -i:$NODE_PROD_PORT)
fi

echo "PORT=$NODE_PROD_PORT" > .env
echo "MONGO_ADMIN_USER=$MONGO_ADMIN_USER" >> .env
echo "MONGO_ADMIN_USER=$MONGO_ADMIN_PWD" >> .env

echo $'\nInstalling dependencies\n'

npm install

echo $'\nBuilding application\n'

npm run build

echo $'\Running application\n'

NODE_ENV="production" npm start
