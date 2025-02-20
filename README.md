# WMCT Core

**NOTICE: This plugin is currently under development. Do not attempt to utilize this plugin as it is- we will publish releases.**

A server management plugin for Minecraft Events & Survival Servers.

NOTES: 
- All features are disabled by default for performance. Use /settings to enable modules in-game or via the config file.
- This plugin does not support the use of command selectors. Rather, you specify a player name or specify the term "ALL" if applicable.

**FEATURES**
- Game Patches & Enhancements
  - FIX: /me crasher
    - Logs will always fire but you can choose whether to auto-kick or auto-ban as this usually only ever is caused by hacked clients
  - FIX: Riptide trident collision with players in spectator mode
  - FIX: Sneak-Flight Block Placement
  - ENHANCEMENT: Prolonged death screen detection
    - If a player forces the game to stay stuck on the death screen, they will be automatically kicked or logged depending on settings
    
- Commands
  - [OP] /settings [module] [true | false] (Through a menu or directly through the command- allows you to enable or disable plugin modules)
  - [OP] /monitor [statistic] (Used to track active changes in server stability & player connection)
    - Server Statistics
      - ALL / No Stat Specified (displays a compressed version of important server information)
      - Chunk Info
      - MSPT (Milliseconds Per Tick)
      - Entities
      - CPU Usage
      - Command Usage Per Second
      - Player Ping List (sorted from highest to lowest)
  - [OP] /check [player] (Displays all client info associated with the player)
  - [OP] /activity <player> [list number] (Lists out session information and the total time playing on the server)
  - [OP] /logtag <add | remove> <tag> (Adds or removes a tag to be used when sending log notifications)
  - [OP] /logs <true | false> (Enables or disables whether you should recieve logs at all)
  - [OP] /dim <DIM> [true | false] (Enables are disables world dimensions)
  - [OP] /dimtp <player> <DIM> [coords] (Warps player(s) to another dimension at the same or specified coordiantes)
  - [OP] /ability <player> <ability node> [ability settings] (Sets a player's ability node such as flight, speed, and so on)
    - Ability Nodes
      - Flight
      - Flight Speed
  - [OP] /mute <player> <duration number> <duration string> <reason> (A moderation command that blocks chat messages)
  - [DEFAULT] /ping [player] (Displays the ping of a player in the chat!)
  - [DEFAULT] /spectate [player] (Through a menu or directly through the command- allows players in spectator to teleport to players in other gamemodes)

- Logging Systems
  - Grief Logger
  - Command Logger
  - Mod Logger
  - Discord Webhook Logger
