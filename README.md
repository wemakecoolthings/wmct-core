# WMCT Core

**NOTICE: This plugin is currently under development. All of the listed features are just planned features and may not be fully implemented.**

A server management plugin for Minecraft Events & Survival Servers using Endstone -> https://github.com/EndstoneMC/endstone

NOTES: 
- All features are disabled by default for performance. Use /settings to enable modules in-game or via the config file.
- This plugin does not support the use of command selectors. Rather, you specify a player name or specify the term "ALL" if applicable.
- All custom commands that target players will attempt to target offline players!

**FEATURES**
- Game Patches & Enhancements
  - FIX: /me crasher
    - Logs will always fire but you can choose whether to auto-kick or auto-ban as this usually only ever is caused by hacked clients
  - FIX: Sneak-Flight Block Placement
  - ENHANCEMENT: Optionally toggle a server-side PvP system
    - Change hit delay
    - Change horizontal KB
    - Change vertical KB
    - Change sprint multiplier 
  - ENHANCEMENT: Admin protection to prevent higher internal permission levels from getting kicked or banned from lower permission levels
    - Read the Internal Permissions Information section below for more info!
  - ENHANCEMENT: Custom moderation system (This disables Endstone's banning systems)
  - ENHANCEMENT: Additional movement commands (/top /bottom)
  - ENHANCEMENT: Aliases for gamemode commands
  - ENHANCEMENT: AFK Detection
  - ENHANCEMENT: Prolonged death screen detection
    - If a player forces the game to stay stuck on the death screen while the immediate respawn gamerule is enabled, they will be automatically kicked or logged depending on settings

- Internal Permissions Information
  - Internal Ranks (from highest to lowest): This includes Minecraft's Permissions & WMCT Core's Permissions Systems
    - Operator: Default Minecraft OP + All Plugin Permissions
    - Mod: Access to MODERATION permissions without the need for operator
    - Helper: Access to INFO permissions without the need for operator
    - Default: Regular permissions based on Minecraft's internal level: visitor or regular
  - Rank Protection
    - Moderation permissions will not effect players with a higher permission level
    - This applies to moderation commands such as /tempban or /mute as well as Minecraft's moderation commands such as /kick 
  
- Commands
  - [OP] /settings (A menu for all plugin settings)
    - Logging Settings
    - Spectator Module Settings
    - Custom Combat Settings
    - Prolonged Death Screen Settings
    - Level DB Storage Settings
    - Grief Log DB Storage Settings
  - [OP] /monitor [statistic: optional] (Used to track active changes in server stability & player connection)
    - Server Statistics
      - ALL / No Stat Specified (displays a compressed version of important server information)
      - Chunk Info
      - MSPT (Milliseconds Per Tick)
      - Entities
      - CPU Usage
      - Command Usage Per Second
      - Player Ping List (sorted from highest to lowest)
  - [OP] /check [player] (Displays all client info associated with the player)
  - [OP] /reloadscripts (Reloads only the Script API, ignoring plugins and other external data)
  - [OP] /updatepacks (Dynamically allows you to increment resource pack versions & update behavior pack dependencies REQUIRES RESTART AFTER)
    - This allows you to update resource packs for forced redownloads as well as update behavior packs in-game on title updates
  - [OP] /saveleveldb [ID] (Saves scoreboards and player data to an external DB)
  - [OP] /loadleveldb [ID] (Loads scoreboards and player data to the world if saved data was found)
  - [OP] /bossbar [player] [text] [color] [progress] (Creates a custom bossbar that can be set to only display to certain players)
  - [OP] /activity [player] [list number: optional] (Lists out session information and the total time playing on the server)
  - [OP] /activitylist (Lists all of the player's total session logs in a menu)
  - [OP] /viewscriptprofiles (Views script profiler outputs)
  - [OP] /logs [true | false] (Enables or disables whether you should recieve logs at all)
  - [OP] /dimtp [player] [DIM] [coords: optional] (Warps player(s) to another dimension at the same or specified coordiantes)
  - [OP] /attribute [player] [ability node] [ability settings: optional] (Sets a player's ability nodes such as flight and flight speed) 
    - Ability Nodes
      - Flight
      - Flight Speed
  - [OP] /sendpopup [player] [text] (Sends a custom popup message)
  - [OP] /sendtip [player] [text] (Sends a custom tip message)
  - [OP] /sendtoast [player] [title] [text] (Sends a custom toast message)
  - [OP] /top [min_y] (Sends the player to the topmost block)
  - [OP] /bottom [max_y] (Sends the player to the first air pocket below them)
  - [OP] /mute [player] [reason: optional] (A moderation command that blocks chat messages)
  - [OP] /unmute [player] [reason: optional] (Unmutes a muted player)
  - [OP] /tempmute [player] [duration number] [duration string] [reason: optional] (A moderation command that blocks chat messages)
  - [OP] /permban [player] [reason: optional] (A moderation command that prevents the player from rejoining the server)
  - [OP] /removeban [player] [reason: optional]
  - [OP] /tempban [player] [duration number] [duration string] [reason: optional]
  - [OP] /punishments [player] (Displays past and current moderation actions taken on the player)
  - [OP] /setrank [player] [Default | Helper | Mod | Operator] (Applies an internal permission setting to the player without operator)
  - [OP] /inspect (Toggles inspect mode where interacting or breaking a block will return any related grief logs)
  - [OP] /grieflog [player] [radius] [filter: optional] (Returns grief logs in the specified area)
    - Supported Logs
      - Login Location
      - Logout Location
      - Block Place
      - Block Break
      - Block Interact
      - Item Use
  - [DEFAULT] /ping [player: optional] (Displays the ping of a player in the chat)
  - [DEFAULT] /refresh (Updates player permissions & commands - to avoid relogging incidents with OP updates)
  - [DEFAULT] /spectate [player: optional] (Through a menu or directly through the command- allows players in spectator to teleport to players in other gamemodes)  

- Logging Systems
  - Grief Logger
  - Command Logger
  - Mod Logger
  - Chat Logger
  - Discord Webhook Logger
