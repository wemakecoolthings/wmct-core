# WMCT Core

A server management plugin for Minecraft Events & Survival Servers.

NOTE: All features are disabled by default for performance. Use /settings to enable modules in-game or via the config file.

**FEATURES**
- Game Patches
  - FIX: /me crasher
  - FIX: iptide trident collision with players in spectator mode
  - ENHANCEMENT: Prolonged death screen detection
    - If a player forces the game to stay stuck on the death screen, they will be automatically kicked or logged depending on settings
  - FIX: Sneak-Flight Block Placement
    
- Commands
  - [OP] /monitor [statistic] (Used to track active changes in server stability & player connection)
    - Server Statistics
      - ALL / No Stat Specified (displays a compressed version of important server information)
      - Chunk Info
      - Processed MSPT (Milliseconds Per Tick)
      - Entities
      - CPU Usage
      - Command Usage Per Second
      - Player Ping List (sorted from highest to lowest)
  - [OP] /check [player] (Displays all client info associated with the player)
  - 
  - [DEFAULT] /ping [player] (Displays the ping of a player in the chat!)
  - 
