#! /bin/bash

if [ -d "dist" ]; then
    sudo cp dist/passgen /usr/bin;
    echo "installed successfully";
else
    echo "the program is not packed"
fi
