#!/bin/bash

OUTPUT_LOG="gemini_bot.log"
PROGRAM_DIR="~/gemini-hybrid-dca-dip-buying-bot"
cd $PROGRAM_DIR
rm gemini_bot.log
nohup python3 bot/trade.py >$OUTPUT_LOG &
tail -f $OUTPUT_LOG
