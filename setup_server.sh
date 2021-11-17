#!/bin/bash

git clone https://github.com/cicerotcv/cloud.git server

cd ./server/api

# sudo kill -9 $(sudo lsof -t -i:8080)

echo "PORT=8080" > .env.development
echo "PORT=3334" > .env.production

echo $'\nInstalling dependencies\n'

npm install

echo $'\nBuilding application\n'

npm run build

echo $'\Running application\n'

NODE_ENV="production" npm start
