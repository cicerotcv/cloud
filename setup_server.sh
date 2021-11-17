#!/bin/bash

git clone https://github.com/cicerotcv/cloud.git server

cd ./server/api

echo "PORT=8080" > .env.development
echo "PORT=3334" > .env.production

echo ""

npm install

echo ""

NODE_ENV="development" npm run dev
