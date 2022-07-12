# Gemini Hybrid DCA and Buy-The-Dip Bot

A trading bot that DCAs a token pair on Gemini cryptocurrency centralised exchange.

By setting a monthly reserved amount of token B for DCA, the remainder of the account balance will be used to create stop limit orders to buy the dip when it arrives.

The dip is considered to start at 4 stop limit price steps below market price when the bot is started.

When the next calendar month starts, and the available amount of token B to trade falls below the monthly reserved amount for DCA, the bot will reset existing limit orders to replenish the budget.

If the market prices start to soar, the bot will track this drastic price change and adjust its definition of the dip, adding higher stop limit orders in the case the price starts crashing down again.

The buy-the-dip functionality can be disabled in the config file. `ENABLE_LIMIT_ORDERS=False`

Your individual trading preferences can be configured at `bot/config.py`

## Running the bot as a script for local development

```bash
python3 __main__.py
```

## Launching the bot as a daemon process

```bash
./launch_gemini_bot.sh
```

## Installing the bot as a service on a linux server

```bash
./setup_bot_as_service.sh
```

sudo access is required.

## Useful commands for managing bot deployed as a service

```bash
systemctl reset-failed gemini_bot_service # reset timeout for starting a failed service
sudo service gemini_bot_service status # check the status of the gemini bot
sudo systemctl start gemini_bot_service # start the bot as a service
sudo systemctl stop gemini_bot_service # stop the bot as a service
sudo journalctl -u gemini_bot_service # see output logs of the service
sudo journalctl -u gemini_bot_service -n 50 # see last 50 logs
sudo journalctl -u gemini_bot_service -n 50 -f # see last 50 logs and follow new logs
sudo journalctl -u gemini_bot_service -n 200 -r # see last 200 logs in reverse chronological order
```
