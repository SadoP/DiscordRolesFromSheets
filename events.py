from itertools import product

import numpy as np
import pandas as pd
from discord.ext import commands, tasks

from sheets import SheetReader


class Events(commands.Cog):
    guild = None
    logchannel = None

    def __init__(self, bot):
        self.bot = bot
        self.sr = SheetReader()
        self.guildID = self.sr.config.get("guildID")
        if not self.guildID:
            raise Exception("no Guild ID given")
        self.logChannelId = self.sr.config.get("loggingChannel")
        if not self.logChannelId:
            raise Exception("no log channel set")

    def setup(self):
        guilds = self.bot.guilds
        if not guilds:
            raise Exception("no guilds joined")
        self.guild = next(guild for guild in guilds if guild.id == int(self.guildID))
        if not self.guild:
            raise Exception("destined guild not present")

        self.logchannel = self.guild.get_channel(int(self.logChannelId))
        if not self.logchannel:
            raise Exception("logchannel not found on server")
        self.updater.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot logged in as {}".format(self.bot.user.name))
        self.setup()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("{} joined the server".format(member.name))
        await self.update_roles()

    def cog_unload(self):
        self.updater.cancel()

    @tasks.loop(minutes=5.0)
    async def updater(self):
        await self.update_roles()

    async def update_roles(self):
        print("updating")
        dataSheet = self.sr.read_spreadsheet()
        dataDiscord = await self.user_list_and_roles()
        rolesAssign, rolesRemove = self.compare_roles(dataSheet, dataDiscord)
        roles = rolesAssign.columns
        users = rolesAssign.index
        for user, role in product(users, roles):
            drole = self.guild.get_role(int(role))
            member = self.guild.get_member(int(user))
            if not drole:
                continue
            if not member:
                continue
            rolename = drole.name
            membername = member.name

            if rolesAssign.loc[user, role]:
                await self.log("assigning {} to {}".format(rolename, membername))
                await self.assign_role(user, role)
            if rolesRemove.loc[user, role]:
                await self.log("removing {} from {}".format(rolename, membername))
                await self.remove_role(user, role)

    async def user_list_and_roles(self):
        roles = [role.get("roleID") for role in self.sr.config.get("roles")]
        data = pd.DataFrame(columns=roles)
        for r in roles:
            role = self.guild.get_role(int(r))
            for m in role.members:
                data.loc[str(m.id), r] = True
            data = data.fillna(False)
        return data

    def compare_roles(self, dataSheet: pd.DataFrame, dataDiscord: pd.DataFrame):
        users = dataSheet.index.union(dataDiscord.index)
        roles = dataSheet.columns
        rolesAssign = pd.DataFrame(np.zeros((len(users), len(roles)), dtype=bool),
                                   index=users, columns=roles)
        rolesRemove = pd.DataFrame(np.zeros((len(users), len(roles)), dtype=bool),
                                   index=users, columns=roles)
        for user, role in product(users, roles):
            hasRole = False
            shallRole = False
            try:
                hasRole = dataDiscord.loc[user, role]
            except KeyError:
                pass
            try:
                shallRole = dataSheet.loc[user, role]
            except KeyError:
                pass
            rolesAssign.loc[user, role] = (not hasRole) & shallRole
            rolesRemove.loc[user, role] = hasRole & (not shallRole)
        return rolesAssign, rolesRemove

    async def assign_role(self, userID, roleID):
        member = self.guild.get_member(int(userID))
        role = self.guild.get_role(int(roleID))
        await member.add_roles(role)

    async def remove_role(self, userID, roleID):
        member = self.guild.get_member(int(userID))
        role = self.guild.get_role(int(roleID))
        await member.remove_roles(role)

    async def log(self, message):
        await self.logchannel.send(message)


def setup(bot):
    bot.add_cog(Events(bot))
