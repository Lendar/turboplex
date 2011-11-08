#!/bin/sh

# this code is property of @bobuk

B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/Turbofilm.bundle"
test -d "$B" || B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/Turbofilm.bundle"
I="$B/Contents"
mkdir -p "$B/"
cp -r "Contents" "$B/"
FILE="$I/Code/__init__.py"
find "$I" -name '*.py' -exec sed -i -e 's/^.*#tmp.*$//' {} \;
echo "Done."