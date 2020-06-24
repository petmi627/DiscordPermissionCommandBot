import os, discord, sys, logging, json

version = "1.0.0"
developed_by = "KywoSkylake: https://github.com/petmi627"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PermissionCommandClient(discord.Client):

    config = None

    def set_config(self, config):
        self.config = config

    async def on_ready(self):
        """
        The Bot started
        :return:
        """
        logger.info("I started up. Beep Bop")
        await self.change_presence(activity=discord.Game(name="mention me with a message containing the word help"))

    async def on_message(self, message):
        if message.author == client.user:
            return

        if type(message.channel) == discord.DMChannel:
            self.logUserMessage(message)
            await message.channel.send("I said please do not reply")

        if client.user in message.mentions and str(message.channel) not in self.config["limit_command_to_channel"]:
            await message.channel.send("Sorry I cannot help you in this channel")

        if str(message.channel) in self.config["limit_command_to_channel"]:
            if client.user in message.mentions:
                self.logUserMessage(message)
                if "help" in message.content.lower():
                    await message.channel.send(self.config["help_text"])
                if "version" in message.content.lower():
                    await message.channel.send('The bot version is {}'.format(version))
                if "creator" in message.content.lower() or "master" in message.content.lower() \
                    or "developer" in message.content.lower() or "created" in message.content.lower():
                    await message.channel.send('I was created by my master {}'.format(developed_by))

            if self.startsWith(message.content.lower(), ["$", "?", "!", "/"]):
                message_received = message.content[1:]
                if message_received.lower().startswith('role'):
                    self.logUserMessage(message)
                    parameter = message.content[6:].split(" ")
                    if parameter[0].lower() == "add":
                        if len(message.mentions) > 1:
                            await message.channel.send("Error: Please mention only one user")
                            logger.error("Error: Please mention only one user")
                            return
                        elif len(message.mentions) == 0:
                            await message.channel.send("Error: Please mention a user")
                            logger.error("Error: Please mention a user")
                            return

                        requested_user = message.mentions[0]

                        user_role = self.checksIfUserHasPermissions(message.author.roles)
                        if user_role is None:
                            await message.channel.send("Error: User {} has insufficient permissions!".format(message.author.mention))
                            logger.error("Error: User {} has insufficient permissions!".format(message.author.mention))
                            return

                        requested_role = self.checksIfUserCanSetPermissions(parameter[1], user_role)
                        if requested_role is None:
                            await message.channel.send(
                                "Error: User {} has insufficient permissions!".format(message.author.mention))
                            logger.error("Error: User {} has insufficient permissions!".format(message.author.mention))
                            return

                        role = message.guild.get_role(int(self.config["roles"][user_role][requested_role]['id']))
                        if self.checkIfUserHasRole(requested_user.roles, role):
                            await message.channel.send(
                                "Error: User {} has already this role!".format(requested_user.mention))
                            logger.error("Error: User {} has already this role!".format(requested_user.mention))
                            return

                        try:
                            await requested_user.add_roles(role)
                            await message.channel.send("Role {} for user {} was successfully set".format(role.name, requested_user.mention))
                            logger.info("Role {} for user {} was successfully set".format(role.name, requested_user))
                        except BaseException as e:
                            await message.channel.send("Error: cannot set role")
                            logger.error("Cannot set role: {}".format(e), exc_info=True)
                            return

                        try:
                            msg = "Hi {},\nYou received the role {} on the server {}".format(
                                requested_user.mention, role.name, message.guild,
                            )
                            if 'add_message' in self.config["roles"][user_role][requested_role].keys():
                                msg += "\n" + self.config["roles"][user_role][requested_role]['add_message']
                            msg += "\nThis message was autogenerated please do not reply"
                            await requested_user.send(msg)
                        except BaseException as e:
                            logger.error("Cannot send private message: {}".format(e), exc_info=True)

                        return
                    elif parameter[0].lower() == "list":
                        msg = ""
                        for author_role in message.author.roles:
                            if author_role.name in self.config["roles"].keys():
                                msg += "For your role {}, you can add user to ".format(author_role.name)
                                msg += ", ".join(self.config["roles"][author_role.name].keys())
                                msg += "\n"

                        if msg == "":
                            msg += "Sorry but you cannot add users to any roles"

                        await message.channel.send(msg)
                    elif parameter[0].lower() == "remove":
                        if len(message.mentions) > 1:
                            await message.channel.send("Error: Please mention only one user")
                            logger.error("Error: Please mention only one user")
                            return
                        elif len(message.mentions) == 0:
                            await message.channel.send("Error: Please mention a user")
                            logger.error("Error: Please mention a user")
                            return

                        requested_user = message.mentions[0]

                        user_role = self.checksIfUserHasPermissions(message.author.roles)
                        if user_role is None:
                            await message.channel.send("Error: User {} has insufficient permissions!".format(message.author.mention))
                            logger.error("Error: User {} has insufficient permissions!".format(message.author.mention))
                            return

                        requested_role = self.checksIfUserCanSetPermissions(parameter[1], user_role)
                        if requested_role is None:
                            await message.channel.send(
                                "Error: User {} has insufficient permissions!".format(message.author.mention))
                            logger.error("Error: User {} has insufficient permissions!".format(message.author.mention))
                            return

                        role = message.guild.get_role(int(self.config["roles"][user_role][requested_role]['id']))
                        if not self.checkIfUserHasRole(requested_user.roles, role):
                            await message.channel.send(
                                "Error: User {} has already this role!".format(requested_user.mention))
                            logger.error("Error: User {} has already this role!".format(requested_user.mention))
                            return

                        try:
                            await requested_user.remove_roles(role)
                            await message.channel.send("Role {} for user {} was successfully removed".format(role.name, requested_user.mention))
                            logger.info("Role {} for user {} was successfully removed".format(role.name, requested_user))
                        except BaseException as e:
                            logger.error("Cannot remove role: {}".format(e), exc_info=True)
                            await message.channel.send("Error: cannot remove role")
                            return

                        try:
                            msg = "Hi {},\nyour role {} on the server {} was removed".format(
                                requested_user.mention, role.name, message.guild,
                            )
                            if 'remove_message' in self.config["roles"][user_role][requested_role].keys():
                                msg += "\n" + self.config["roles"][user_role][requested_role]['remove_message']
                            msg += "\nThis message was autogenerated please do not reply"
                            await requested_user.send(msg)
                        except BaseException as e:
                            logger.error("Cannot send private message: {}".format(e), exc_info=True)

                        return
                    else:
                        await message.channel.send(self.config["help_text"])

    def checkIfUserHasRole(self, user_roles, role):
        for user_role in user_roles:
            if user_role == role:
                return True

        return False

    def checksIfUserCanSetPermissions(self, requested_role, user_role):
        if requested_role in self.config["roles"][user_role].keys():
            return requested_role

        return None

    def checksIfUserHasPermissions(self, user_roles):
        for role in self.config["roles"].keys():
            for u_role in user_roles:
                if role == u_role.name:
                    return role

        return None

    def logUserMessage(self, message):
        logger.info(
            "Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))

    def startsWith(self, message, list):
        for item in list:
            if str(message).startswith(item):
                return True
        return False

if '__main__' == __name__:
    with open('config.json', 'r') as file:
        config = json.load(file)
    client = PermissionCommandClient()
    client.set_config(config)
    client.run(os.environ['token'])