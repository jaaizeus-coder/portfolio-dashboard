#!/bin/bash
# Manage development server

case "$1" in
  start)
    echo "🟢 Starting development server on port 8080..."
    python3 -m http.server 8080 > server.log 2>&1 &
    echo $! > server.pid
    sleep 2
    echo "✅ Server running: http://localhost:8080"
    ;;
  stop)
    if [ -f server.pid ]; then
      kill $(cat server.pid) 2>/dev/null
      rm server.pid
      echo "🔴 Server stopped"
    else
      echo "⚠️  Server not running"
    fi
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  status)
    if [ -f server.pid ] && ps -p $(cat server.pid) > /dev/null 2>&1; then
      echo "🟢 Server running on http://localhost:8080"
    else
      echo "🔴 Server not running"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    ;;
esac
