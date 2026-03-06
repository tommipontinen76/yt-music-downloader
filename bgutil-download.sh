#!/bin/bash

# Target directory
REPO_URL="https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git"
BRANCH="1.3.0"
DIR_NAME="bgutil-ytdlp-pot-provider"

# Use APP_BASE_PATH if provided by the caller (ytmusic-downloader.py)
BASE_DIR="${APP_BASE_PATH:-$(pwd)}"
cd "$BASE_DIR" || exit 1

# Clone if not present
if [ ! -d "$DIR_NAME" ]; then
    echo "Cloning $REPO_URL (branch $BRANCH)..."
    git clone --single-branch --branch "$BRANCH" "$REPO_URL" "$DIR_NAME"
fi

cd "$DIR_NAME/server" || { echo "Could not enter server directory"; exit 1; }

# Only install/compile if build/main.js doesn't exist (e.g. first run or development)
# In packaged versions, these should already be present.
if [ ! -f "build/main.js" ] || [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    npm audit fix --force

    echo "Compiling..."
    npx tsc
fi

echo "Starting server in the background..."
# Run node build/main.js in the background
# We use a pid file in a writable location if possible
PID_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/yt-music-downloader"
mkdir -p "$PID_DIR"
PID_FILE="$PID_DIR/server.pid"

nohup node build/main.js > server.log 2>&1 &
echo $! > "$PID_FILE"
# Also keep the old location for compatibility if writable
echo $! > ../server.pid 2>/dev/null

echo "Server started with PID $(cat "$PID_FILE")"
