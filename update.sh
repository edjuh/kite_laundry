#!/bin/zsh
cd /Users/ed/kite_laundry
git checkout feature/new-app
git pull origin feature/new-app
if [ -n "$(git status --porcelain)" ]; then
  git add .
  git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin feature/new-app
fi
if [ -n "$(docker ps -q)" ]; then
  docker stop $(docker ps -q)
fi
if [ -n "$(docker ps -a -q)" ]; then
  docker rm $(docker ps -a -q)
fi
docker build -t kite-laundry .
docker run -p 5001:5000 -v $(pwd):/app kite-laundry
