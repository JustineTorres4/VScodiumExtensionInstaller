#!/bin/bash

mkdir -p lib
mkdir -p driver

pip install --upgrade pip
pip install --target=lib selenium webdriver-manager

echo "Install the geckodriver in "https://github.com/mozilla/geckodriver/releases" and put it inside the driver/ folder"