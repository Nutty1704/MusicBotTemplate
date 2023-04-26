# Music Bot Template Code

## A fully functional discord music bot written in python. Features all basic music bot commands and offers YouTube and Spotify support.

This bot was built to serve private servers and is not meant to be used commercially. Commercial Discord music bots that play audio from YouTube violate YouTube guidelines.

* Discord Music Bot
* Supports YouTube and Spotify
* Has all features like play, skip, playnow, queue, loop, move, skipto, search, etc.
* Utilizes Discord API, Spotify API, and Wavelink node servers.

## How to use this bot

1. Clone this project
2. Edit config.py file and add your discord bot token, spotify client id, and spotify client secret id. Spotify API ids can be generated [here](https://developer.spotify.com/)
3. Run main.py file to get the bot online and functioning.

## How to add additional features

You can add more features to this bot as per your need. Refer to [discord.py docs](https://discordpy.readthedocs.io/en/stable/) and write your own features in files inside the cogs/ directory. There are some util files inside utils/ to faciliate actions like playing and comments have been provided to help you understand the files.
