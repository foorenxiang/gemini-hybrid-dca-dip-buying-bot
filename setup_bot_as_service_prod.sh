#!/bin/bash

sudo -H pip3 install -r /home/foorx/gemini-hybrid-dca-dip-buying-bot/requirements.txt
sudo cp /home/foorx/gemini-hybrid-dca-dip-buying-bot/gemini_bot_service.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gemini_bot_service.service
sudo systemctl start gemini_bot_service.service
