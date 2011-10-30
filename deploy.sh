#!/bin/sh

# this code is property of @bobuk

B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/turbofilm.bundle"
test -d "$B" || B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/turbofilm.bundle"
I="$B/Contents"
mkdir -p "$B/"
cp -r "Contents" "$B/"

echo "Done."