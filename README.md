# Gemini Hybrid DCA and Dip-Buying BOt

A trading bot that DCAs a token pair on Gemini cryptocurrency centralised exchange.

## Running the bot as a script for local development

```bash
python3 __main__.py
```

## Launching the bot as a daemon process

```bash
./launch_gemini_bot.sh
```

### Installing the bot as a service on a linux server

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
```
