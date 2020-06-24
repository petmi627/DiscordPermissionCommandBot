# Discord Permissions Command Bot

This is a small discord bot, that can give user permissions using commands.

## Installation

Please clone the repository and navigate to the working directory and build the Docker container.

```bash
docker build -t dicord-permission-command-bot .
```

To modify the configuration file please copy it and make the modification to the copy

```bash
cp config.json config.local.json
```

After the operation you can start the bot, you need to change the variables as you need it.

```bash
docker run --detach -e "token=[Your Token]" -v "${PWD}/config.local.json:/config.json" --name dicord-bot-permission-command dicord-permission-command-bot
```

## Usage

In discord, mention the bot name and type help to get a list with commands