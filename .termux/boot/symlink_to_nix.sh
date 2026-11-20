#!/data/data/com.termux/files/usr/bin/bash

# Directories
TERMUX_BIN="/data/data/com.termux/files/usr/bin"
NIX_BIN="/data/data/ru.ldral.nix/nix/var/nix/profiles/default/bin"

# Ensure Nix-on-Droid's bin directory exists
mkdir -p "$NIX_BIN"

# Iterate over Termux binaries
for binary in "$TERMUX_BIN"/*; do
    # Skip directories and non-executable files
    [ -f "$binary" ] && [ -x "$binary" ] || continue

    # Extract binary name
    bin_name=$(basename "$binary")

    # Skip if binary already exists in Nix-on-Droid's bin
    if [ -e "$NIX_BIN/$bin_name" ]; then
        echo "Skipping $bin_name (already exists in Nix-on-Droid)"
        continue
    fi

    # Create symlink
    ln -s "$binary" "$NIX_BIN/$bin_name-termux"
    echo "Symlinked $bin_name to Nix-on-Droid as $bin_name-termux"
done
