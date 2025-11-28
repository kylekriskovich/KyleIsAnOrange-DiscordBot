# KyleIsAnOrange Discord Bot

A small Discord bot written in Python using `discord.py` that integrates with a Minecraft (Paper/Spigot/Vanilla) server via RCON.

- Run the **Discord bot** on Windows for development.
- Deploy it on an **Ubuntu server** alongside your Minecraft server (or anywhere that can reach it over the network).
- Provide Discord commands for server status, player list, whitelist management, and running console commands.

---

## Features

### Discord Bot

- `!ping` – basic connectivity test.
- `!hello` – simple greeting.

### Minecraft Integration (`!mc` commands)

Uses RCON to send commands to the Minecraft server.

- `!mc status`  
  Check whether RCON is reachable and show the output of the `list` command.

- `!mc list`  
  Show online player count and names.

- `!mc say <message>`  
  Broadcast a message into Minecraft chat as:
  > [Discord] <DiscordName>: message  
  Requires `Manage Messages` permission in Discord.

- `!mc whitelist add <player>`  
  Add a player to the whitelist and reload it.  
  Requires `Manage Server` / `Manage Guild` permission.

- `!mc whitelist remove <player>`  
  Remove a player from the whitelist and reload it.  
  Requires `Manage Server` / `Manage Guild` permission.

- `!mc cmd <raw command>`  
  Run a raw console command on the Minecraft server via RCON.  
  **Admin-only** (requires `Administrator` permission in Discord).  
  _This is powerful and should only be used by trusted admins._

---

## Tech Stack

- **Language:** Python 3.x
- **Discord Library:** [`discord.py`](https://pypi.org/project/discord.py/)
- **RCON Library:** [`mcrcon`](https://pypi.org/project/mcrcon/)
- **Minecraft Server:** Paper (or any server with RCON support enabled)

---

## Repository Layout

```text
KyleIsAnOrange-DiscordBot/
├─ bot.py          # Main Discord bot entrypoint
├─ minecraft.py    # Minecraft / RCON integration (Discord Cog)
├─ requirements.txt
└─ .venv/          # Local virtual environment (ignored by git)
