#!/bin/bash

pip3 install Flask
pip3 install requests
pip3 install bs4
pip3 install numpy

mkdir project/Webcrawling
cp -r project/app_final.py project/templates project/Webcrawling
echo copy source files and templates

gnome-terminal -x ./elasticsearch-7.6.2/bin/elasticsearch
echo initiating elasticsearch
./project/Webcrawling/app_final.py

