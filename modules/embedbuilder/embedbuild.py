import discord
from discord.ext import commands
import matplotlib.colors as mcolors
import json
from discord.ui import Select

class ChannelSelectView(discord.ui.View):
    def __init__(self, user_id, embed_data, guild):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.embed_data = embed_data
        self.guild = guild
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in self.guild.text_channels
        ]
        self.add_item(ChannelSelect(user_id=self.user_id, options=options, embed_data=self.embed_data))

class ChannelSelect(discord.ui.Select):
    def __init__(self, user_id, options, embed_data):
        self.user_id = user_id
        self.embed_data = embed_data
        super().__init__(placeholder="Select a channel to send the embed", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        channel_id = int(self.values[0])
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed.from_dict(self.embed_data)
            await channel.send(embed=embed)

            preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[self.user_id]['preview_message_id']
            preview_message = await interaction.channel.fetch_message(preview_message_id)
            await preview_message.delete()
            del interaction.client.get_cog('EmbedBuilder').embed_config[self.user_id]

            await interaction.response.send_message(f"Embed successfully sent to {channel.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message("Failed to send embed. Invalid channel!", ephemeral=True)

class EmbedButtonView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        select = discord.ui.Select(placeholder="Load a template", options=[
            discord.SelectOption(label="Load a JSON tempalate", value="json_template")
        ])
        select.callback = self.load_json_template
        self.add_item(select)

    @discord.ui.button(label="Title text", style=discord.ButtonStyle.secondary, row=0)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedTitleModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Description text", style=discord.ButtonStyle.secondary, row=0)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedDescriptionModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Embed Color", style=discord.ButtonStyle.secondary, row=0)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedColorModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Thumbnail Image", style=discord.ButtonStyle.secondary, row=0)
    async def edit_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedThumbnailModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Large Image", style=discord.ButtonStyle.secondary, row=1)
    async def edit_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedImageModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Footer text", style=discord.ButtonStyle.secondary, row=1)
    async def edit_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedFooterModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Author text", style=discord.ButtonStyle.secondary, row=1)
    async def edit_author(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedAuthorModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.primary, row=2)
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = EmbedFieldModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Clear Fields", style=discord.ButtonStyle.danger, row=2)
    async def clear_fields(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        embed.clear_fields()
        
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)

        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.response.send_message("All fields cleared!", ephemeral=True)

    @discord.ui.button(label="Post Embed", style=discord.ButtonStyle.success, row=3)
    async def complete_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.id != self.user_id:
            await interaction.followup.send("Unauthorized request!", ephemeral=True)
            return
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        guild = interaction.guild
        view = ChannelSelectView(self.user_id, embed_data, guild)
        await interaction.followup.send("Select the channel to send the embed:", view=view, ephemeral=True)

    @discord.ui.button(label="Get JSON format", style=discord.ButtonStyle.secondary, row=3)
    async def get_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.user.id != self.user_id:
            await interaction.followup.send("Unauthorized request!", ephemeral=True)
            return
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed_json = json.dumps(embed_data, indent=4)
        
        await interaction.followup.send(f"```json\n{embed_json}\n```", ephemeral=True)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger, row=3)
    async def exit_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        embed_builder = interaction.client.get_cog('EmbedBuilder')
        if interaction.user.id in embed_builder.embed_config:
            del embed_builder.embed_config[interaction.user.id]

        await interaction.response.send_message("Embed creation exited. All unsaved changes discarded.", ephemeral=True)
        await interaction.message.delete()

    async def load_json_template(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Unauthorized request!", ephemeral=True)
            return
        modal = JSONInputModal()
        await interaction.response.send_modal(modal)

#--------------------------MODALS --------------------------------------
class EmbedTitleModal(discord.ui.Modal, title="Edit Embed Title"):
    title_input = discord.ui.TextInput(label="Title", placeholder="Enter 'none' to remove title.", max_length=256)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        if self.title_input.value.strip().lower() == "none":
            embed.title = None
            await interaction.followup.send("Title has been removed!", ephemeral=True)
        else:
            embed.title = self.title_input.value.strip()
            await interaction.followup.send(f"Title updated to '{self.title_input.value}'!", ephemeral=True)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()

class EmbedDescriptionModal(discord.ui.Modal, title="Edit Embed Description"):
    description_input = discord.ui.TextInput(
        label="Description", 
        style=discord.TextStyle.long, 
        placeholder="Enter 'none' for no description."
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        if self.description_input.value.strip().lower() == "none":
            embed.description = None
        else:
            embed.description = self.description_input.value
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        await interaction.followup.send(f"Description updated to '{self.description_input.value}'", ephemeral=True)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()

class EmbedColorModal(discord.ui.Modal, title="Edit Embed Color"):
    color_input = discord.ui.TextInput(
        label="Color",
        placeholder="Enter color name eg. 'red', 'blue' or hex code eg. '#FF0000'. ",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        color_value = self.color_input.value.strip().lower()
        if color_value in mcolors.CSS4_COLORS:
            hex_color = mcolors.CSS4_COLORS[color_value]
            embed.color = discord.Color(int(hex_color.lstrip("#"), 16))
        else:
            try:
                embed.color = discord.Color(int(color_value.lstrip("#"), 16))
            except ValueError:
                await interaction.followup.send("Invalid color! Please use a valid color name or hex code (e.g., 'red', 'blue', #FF5733).", ephemeral=True)
                return
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Color updated to '{color_value}'", ephemeral=True)

class EmbedThumbnailModal(discord.ui.Modal, title="Edit Embed Thumbnail"):
    thumbnail_url = discord.ui.TextInput(label="Thumbnail URL", placeholder="Enter thumbnail URL here.")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        embed.set_thumbnail(url=self.thumbnail_url.value)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Thumbnail successfully updated!", ephemeral=True)

class EmbedImageModal(discord.ui.Modal, title="Edit Embed Image"):
    image_url = discord.ui.TextInput(label="Image URL", placeholder="Enter a URL for the image")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        embed.set_image(url=self.image_url.value)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Image successfully updated!", ephemeral=True)

class EmbedFooterModal(discord.ui.Modal, title="Edit Embed Footer"):
    footer_text = discord.ui.TextInput(label="Footer Text", placeholder="Enter footer text")
    footer_icon_url = discord.ui.TextInput(label="Footer Icon URL", required=False, placeholder="Enter URL for the footer icon (optional)")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        embed.set_footer(text=self.footer_text.value, icon_url=self.footer_icon_url.value or None)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Footer successfully updated!", ephemeral=True)

class EmbedAuthorModal(discord.ui.Modal, title="Edit Embed Author"):
    author_name = discord.ui.TextInput(label="Author Name", placeholder="Enter author name")
    author_icon_url = discord.ui.TextInput(label="Author Icon URL", required=False, placeholder="Enter URL for the author icon (optional)")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        embed.set_author(name=self.author_name.value, icon_url=self.author_icon_url.value or None)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Author successfully updated!", ephemeral=True)

class EmbedFieldModal(discord.ui.Modal, title="Add Embed Field"):
    field_name = discord.ui.TextInput(label="Field Name", placeholder="Enter field name")
    field_value = discord.ui.TextInput(label="Field Value", placeholder="Enter field value", style=discord.TextStyle.paragraph)
    inline = discord.ui.TextInput(label="Inline (True/False)", placeholder="Enter True or False", default="False")
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        embed_data = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed']
        embed = discord.Embed.from_dict(embed_data)
        inline_val = self.inline.value.lower() == "true"
        embed.add_field(name=self.field_name.value, value=self.field_value.value, inline=inline_val)
        preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
        preview_message = await interaction.channel.fetch_message(preview_message_id)
        await preview_message.edit(embed=embed)
        interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
        await interaction.followup.send(f"Filed successfully updated!", ephemeral=True)

class JSONInputModal(discord.ui.Modal, title="Paste your JSON Embed"):
    json_input = discord.ui.TextInput(label="JSON Input", style=discord.TextStyle.paragraph, placeholder="Paste your JSON here")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            json_data = json.loads(self.json_input.value)
            embed = discord.Embed.from_dict(json_data)
            preview_message_id = interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['preview_message_id']
            preview_message = await interaction.channel.fetch_message(preview_message_id)
            await preview_message.edit(embed=embed)
            interaction.client.get_cog('EmbedBuilder').embed_config[interaction.user.id]['embed'] = embed.to_dict()
            await interaction.followup.send("Embed updated from JSON successfully!", ephemeral=True)
        except json.JSONDecodeError:
            await interaction.followup.send("Invalid JSON format. Please try again.", ephemeral=True)

#---------------------END OF MODALS----------------------------------------#

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_config = {}  
    @commands.hybrid_command(name="embedbuild", description="Start building your embed!")
    @commands.has_permissions(administrator=True)
    async def embedbuild(self, ctx: commands.Context):  
        embed = discord.Embed(title="Embed Builder", description="Welcome to **Koma4k EMBED BUILDER** here you can create your custom embed using the buttons and dropdowns below. When you're finished, click **post embed** to send it!", color=discord.Color.dark_embed())
        view = EmbedButtonView(ctx.author.id)
        preview_message = await ctx.send(embed=embed, view=view)
        self.embed_config[ctx.author.id] = {
            "embed": embed.to_dict(),
            "preview_message_id": preview_message.id,
        }
async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))
