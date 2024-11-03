<div align="center">

# 🤖 Discord Embed Builder Bot

A powerful Discord bot that allows server administrators to create, customize, and manage embeds through an interactive interface.

<img src="preview.png" alt="Discord Embed Builder Preview" style="margin-left: 5px">

## ✨ Features

🎨 Interactive embed builder with real-time preview<br>
🛠️ Customizable elements:<br>
  • Title and description<br>
  • Color picker (hex/name support)<br>
  • Thumbnail and large images<br>
  • Author information<br>
  • Footer with optional icon<br>
  • Multiple fields (inline/non-inline)<br>
💾 JSON template support<br>
🔒 Administrator-only access<br>
🚀 Hybrid commands (both slash and prefix commands)

## 🔧 Installation

Clone the repository<br>
<div align="center">
<pre>
git clone https://github.com/Koma4k/discord-embed-builder.git
cd discord-embed-builder
</pre>
</div>

Install required dependencies<br>
<div align="center">
<pre>
pip install -r requirements.txt
</pre>
</div>

Configure the bot<br>
• Rename `config.example.yml` to `config.yml`<br>
• Fill in your bot token and preferred settings<br>

Start the bot<br>
<div align="center">
<pre>
python bot.py
</pre>
</div>

In Discord, run the following:<br>
<div align="center">
<pre>
$sync guild or $sync globally
</pre>
</div>

To start the embed building process run:<br>
<div align="center">
<pre>
/embedbuild
</pre>
</div>

## 🎮 Usage

Use the interactive buttons to customize your embed:<br>
📝 Title text<br>
📄 Description text<br>
🎨 Embed Color<br>
🖼️ Thumbnail Image<br>
🌅 Large Image<br>
👤 Author text<br>
📊 Add Field<br>
🗑️ Clear Fields<br>
📤 Post Embed<br>
💾 Get JSON format

## 🛠️ Commands

### Administrator Commands
`/embedbuild` - Start the embed builder interface

### Owner Commands
`/sync [scope]` - Sync slash commands (scope: global/guild)<br>
`/unsync [scope]` - Unsync slash commands<br>
`/load [cog]` - Load a cog<br>
`/unload [cog]` - Unload a cog<br>
`/reload [cog]` - Reload a cog<br>
`/shutdown` - Shutdown the bot

## 📋 Requirements

Python 3.8+<br>
discord.py 2.0+<br>
PyYAML<br>
matplotlib

## 🔒 Security

Ensure your bot token remains private<br>
Only server administrators can use the embed builder<br>
Only the bot owner can use management commands

</div>
