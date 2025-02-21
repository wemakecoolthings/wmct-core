# WMCT Core

**NOTICE: This plugin is currently under development. Do not attempt to utilize this plugin as it is- we will publish releases.**

A server management plugin for Minecraft Events & Survival Servers using Endstone -> https://github.com/EndstoneMC/endstone

NOTES: 
- All features are disabled by default for performance. Use /settings to enable modules in-game or via the config file.
- This plugin does not support the use of command selectors. Rather, you specify a player name or specify the term "ALL" if applicable.
- All custom commands that target players supports offline players!

**FEATURES**
- Game Patches & Enhancements
  - FIX: /me crasher
    - Logs will always fire but you can choose whether to auto-kick or auto-ban as this usually only ever is caused by hacked clients
  - FIX: Riptide trident collision with players in spectator mode
  - FIX: Sneak-Flight Block Placement
  - ENHANCEMENT: Auto-recalc for permissions upon changing a player's permission status
  - ENHANCEMENT: AFK Detection (optional public log & OP log)
  - ENHANCEMENT: Aliases for gamemode commands
  - ENHANCEMENT: Prolonged death screen detection
    - If a player forces the game to stay stuck on the death screen while the immediate respawn gamerule is enabled, they will be automatically kicked or logged depending on settings
    
- Commands
  - [OP] /settings (A menu for all plugin settings)
    - Set discord webhook (per logging system)
    - Toggle chat logging
    - Toggle discord logging
    - Toggle grief logging
    - Toggle mod logging
    - Toggle command logging
    - Toggle game patches (sub menu)
    - AFK Detection Settings
    - Prolonged Death Screen Settings
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
  - [OP] /reloadpacks (Automatically increments resource pack UUIDs then performs a server restart and relogs players)
  - [OP] /activity [player] [list number: optional] (Lists out session information and the total time playing on the server)
  - [OP] /activitylist (Lists all of the player's total session logs in a menu)
  - [OP] /viewscriptprofiles (Views script profiler outputs)
  - [OP] /logtag [add | remove] [tag] (Adds or removes a tag to be used when sending log notifications)
  - [OP] /logs [true | false] (Enables or disables whether you should recieve logs at all)
  - [OP] /dimtoggle [DIM] [true | false] (Enables OR disables world dimensions)
  - [OP] /dimtp [player] [DIM] [coords: optional] (Warps player(s) to another dimension at the same or specified coordiantes)
  - [OP] /ability [player] [ability node] [ability settings: optional] (Sets a player's ability node such as flight, speed, and so on)
    - Ability Nodes
      - Flight
      - Flight Speed
  - [OP] /mute [player] [duration number] [duration string] [reason: optional] (A moderation command that blocks chat messages)
  - [OP] /unmute [player] [reason: optional] (Unmutes a muted player)
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
  - [DEFAULT] /spectate [player: optional] (Through a menu or directly through the command- allows players in spectator to teleport to players in other gamemodes)

- Logging Systems
  - Grief Logger
  - Command Logger
  - Mod Logger
  - Chat Logger
  - Discord Webhook Logger
