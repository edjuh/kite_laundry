#!/bin/bash
cd /Users/ed/kite_laundry
git checkout feature/new-app
git pull origin feature/new-app
if [ -n "$(git status --porcelain)" ]; then
  git add .
  git commit -m "Auto-update: $(date)"
  git push origin feature/new-app
fi
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker build -t kite-laundry .
docker run -p 5001:5000 -v $(pwd):/app kite-laundry
