#!/bin/bash

pip3 install Flask
pip3 install requests
pip3 install bs4
pip3 install numpy


mkdir -p project/Webcrawling # directory 생성
cp -r app_final.py templates_final project/Webcrawling # project/Webcrawling에 최종 파일 복사 
mv project/Webcrawling/templates_final project/Webcrawling/templates #templates_final templates로 이름 바꾼다.
echo copy source files and templates

gnome-terminal -x ./elasticsearch-7.6.2/bin/elasticsearch
echo initiating elasticsearch
./project/Webcrawling/app_final.py

