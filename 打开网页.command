#!/bin/bash
cd "$(dirname "$0")"
PORT=8766
if lsof -i :$PORT >/dev/null 2>&1; then
  echo "服务器已在运行：http://127.0.0.1:$PORT/hub.html"
else
  echo "正在启动本地服务器…"
  python3 -m http.server $PORT &
  sleep 1
fi
open "http://127.0.0.1:$PORT/hub.html"
