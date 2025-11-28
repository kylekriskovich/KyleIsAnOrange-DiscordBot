import os

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from mcrcon import MCRcon


# ===== MINECRAFT RCON CONFIG =====
MC_RCON_HOST = os.getenv("MC_RCON_HOST", "127.0.0.1")
MC_RCON_PORT = int(os.getenv("MC_RCON_PORT", "25575"))
MC_RCON_PASSWORD = os.getenv("MC_RCON_PASSWORD", "")
# =================================


class MinecraftRconClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

    def _connect(self):
        if not self.password:
            raise RuntimeError("MC_RCON_PASSWORD is not set.")
        return MCRcon(self.host, self.password, port=self.port)

    def run(self, command: str) -> str:
        """
        Run a raw Minecraft console command via RCON and return the output.
        """
        with self._connect() as mcr:
            resp = mcr.command(command)
            return resp or ""

    def list_players(self) -> dict:
        """
        Call the vanilla 'list' command and try to parse:
        'There are X of a max of Y players online: name1, name2'
        """
        raw = self.run("list")
        result = {
            "raw": raw,
            "online": 0,
            "max": None,
            "players": [],
        }

        if not raw:
            return result

        # Try to extract counts
        try:
            parts = raw.split()
            nums = [int(p) for p in parts if p.isdigit()]
            if nums:
                result["online"] = nums[0]
            if len(nums) >= 2:
                result["max"] = nums[1]
        except Exception:
            return result

        # Player list (after colon)
        if ":" in raw:
            after_colon = raw.split(":", 1)[1].strip()
            if after_colon:
                players = [p.strip() for p in after_colon.split(",") if p.strip()]
                result["players"] = players

        return result


class Minecraft(commands.Cog):
    """
    Cog that contains all Minecraft / RCON-related commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rcon = MinecraftRconClient(MC_RCON_HOST, MC_RCON_PORT, MC_RCON_PASSWORD)

    # --- Base group: !mc --- #

    @commands.group(name="mc", invoke_without_command=True)
    async def mc(self, ctx: commands.Context):
        """
        Base command for Minecraft controls.
        Usage: !mc <subcommand>
        """
        await ctx.send(
            "Minecraft commands:\n"
            "`!mc status` – check RCON status\n"
            "`!mc list` – list online players\n"
            "`!mc say <message>` – send message to in-game chat\n"
            "`!mc whitelist add/remove <player>` – manage whitelist\n"
            "`!mc cmd <raw command>` – run console command (admin only)"
        )

    # --- Status / list --- #

    @mc.command(name="status")
    async def mc_status(self, ctx: commands.Context):
        """
        Check if the Minecraft server is reachable via RCON.
        """
        try:
            raw = self.rcon.run("list")
            if raw:
                await ctx.send(f"✅ RCON connected.\n```{raw}```")
            else:
                await ctx.send("⚠️ RCON connected but got an empty response from `list`.")
        except Exception as e:
            await ctx.send(f"❌ Could not reach Minecraft via RCON.\n```{e}```")

    @mc.command(name="list")
    async def mc_list(self, ctx: commands.Context):
        """
        Show online players with a bit of formatting.
        """
        try:
            info = self.rcon.list_players()
            if info["online"] == 0 or not info["players"]:
                await ctx.send("🌐 Server online, but no players are currently online.")
                return

            max_str = f"/{info['max']}" if info["max"] is not None else ""
            players_str = ", ".join(info["players"])
            await ctx.send(
                f"👥 Players online **{info['online']}{max_str}**:\n`{players_str}`"
            )
        except Exception as e:
            await ctx.send(f"❌ Error fetching player list.\n```{e}```")

    # --- Chat bridge: !mc say --- #

    @mc.command(name="say")
    @has_permissions(manage_messages=True)
    async def mc_say(self, ctx: commands.Context, *, message: str):
        """
        Broadcast a message into Minecraft chat.
        Requires 'Manage Messages' in Discord.
        """
        try:
            self.rcon.run(f'say [Discord] {ctx.author.display_name}: {message}')
            await ctx.send("✅ Sent message to Minecraft chat.")
        except Exception as e:
            await ctx.send(f"❌ Error sending message.\n```{e}```")

    @mc_say.error
    async def mc_say_error(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to use `!mc say`.")

    # --- Whitelist management: !mc whitelist ... --- #

    @mc.group(name="whitelist", invoke_without_command=True)
    async def mc_whitelist(self, ctx: commands.Context):
        await ctx.send("Use: `!mc whitelist add <player>` or `!mc whitelist remove <player>`")

    @mc_whitelist.command(name="add")
    @has_permissions(manage_guild=True)
    async def mc_whitelist_add(self, ctx: commands.Context, player: str):
        """
        Add a player to the whitelist and reload it.
        """
        # Strip wrapping quotes if the user typed !mc whitelist add "Name"
        player = player.strip('"').strip("'")

        try:
            r1 = self.rcon.run(f"whitelist add {player}")
            r2 = self.rcon.run("whitelist reload")

            combined = f"{r1}\n{r2}".strip()

            # Basic error detection from Minecraft output
            error_markers = [
                "Incorrect argument for command",
                "Unknown player",
                "No player was found",
                "does not exist"
            ]

            if any(marker in r1 for marker in error_markers):
                await ctx.send(
                    f"❌ Failed to whitelist `{player}`.\n"
                    f"```{r1}```"
                )
            else:
                await ctx.send(
                    f"✅ Whitelisted `{player}`.\n"
                    f"```{combined}```"
                )

        except Exception as e:
            await ctx.send(f"❌ Error whitelisting `{player}`.\n```{e}```")


    @mc_whitelist.command(name="remove")
    @has_permissions(manage_guild=True)
    async def mc_whitelist_remove(self, ctx: commands.Context, player: str):
        """
        Remove a player from the whitelist and reload it.
        """
        player = player.strip('"').strip("'")

        try:
            r1 = self.rcon.run(f"whitelist remove {player}")
            r2 = self.rcon.run("whitelist reload")
            combined = f"{r1}\n{r2}".strip()

            await ctx.send(
                f"✅ Removed `{player}` from whitelist.\n"
                f"```{combined}```"
            )
        except Exception as e:
            await ctx.send(f"❌ Error removing `{player}` from whitelist.\n```{e}```")

    # --- Raw console: !mc cmd --- #

    @mc.command(name="cmd")
    @has_permissions(administrator=True)
    async def mc_cmd(self, ctx: commands.Context, *, command: str):
        """
        Run a raw console command on the Minecraft server.
        ADMIN ONLY – dangerous if abused.
        """
        try:
            resp = self.rcon.run(command)
            if resp.strip():
                await ctx.send(f"🖥 Ran: `{command}`\n```{resp}```")
            else:
                await ctx.send(f"🖥 Ran: `{command}`\n(no response)")
        except Exception as e:
            await ctx.send(f"❌ Error running command.\n```{e}```")

    @mc_cmd.error
    async def mc_cmd_error(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("`!mc cmd` is admin-only.")


async def setup(bot: commands.Bot):
    """
    Required entrypoint for discord.py extensions.
    Called by bot.load_extension("minecraft").
    """
    await bot.add_cog(Minecraft(bot))
