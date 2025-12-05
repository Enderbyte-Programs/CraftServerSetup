import os
import sys
import arguments as _arguments

UPDATEINSTALLED = False
DOCFILE = "https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/doc/craftserversetup.epdoc"
DEVELOPER = False#Enable developer tools by putting DEVELOPER as a startup flag
MODRINTH_USER_AGENT = f"Enderbyte-Programs/CraftServerSetup"
SHOW_ADVERT = False
DEFAULT_SERVER_PROPERTIES = r"""
#Minecraft server properties
#[Generation date and time]
accepts-transfers=false
allow-flight=false
broadcast-console-to-ops=true
broadcast-rcon-to-ops=true
bug-report-link=
difficulty=easy
enable-code-of-conduct=false
enable-jmx-monitoring=false
enable-query=false
enable-rcon=false
enable-status=true
enforce-secure-profile=true
enforce-whitelist=false
entity-broadcast-range-percentage=100
force-gamemode=false
function-permission-level=2
gamemode=survival
generate-structures=true
generator-settings={}
hardcore=false
hide-online-players=false
initial-disabled-packs=
initial-enabled-packs=vanilla
level-name=world
level-seed=
level-type=minecraft:normal
log-ips=true
management-server-enabled=false
management-server-host=localhost
management-server-port=0
management-server-secret=[Random text]
management-server-tls-enabled=true
management-server-tls-keystore=
management-server-tls-keystore-password=
max-chained-neighbor-updates=1000000
max-players=20
max-tick-time=60000
max-world-size=29999984
motd=A Minecraft Server
network-compression-threshold=256
online-mode=true
op-permission-level=4
pause-when-empty-seconds=60
player-idle-timeout=0
prevent-proxy-connections=false
query.port=25565
rate-limit=0
rcon.password=
rcon.port=25575
region-file-compression=deflate
require-resource-pack=false
resource-pack=
resource-pack-id=
resource-pack-prompt=
resource-pack-sha1=
server-ip=
server-port=25565
simulation-distance=10
spawn-protection=16
status-heartbeat-interval=0
sync-chunk-writes=true
text-filtering-config=
text-filtering-version=0
use-native-transport=true
view-distance=10
white-list=false
"""

BEDROCK_DEFAULT_SERVER_PROPERTIES = r"""
server-name=Dedicated Server
gamemode=survival
force-gamemode=false
difficulty=easy
allow-cheats=false
max-players=10
online-mode=true
allow-list=false
server-port=19132
server-portv6=19133
enable-lan-visibility=true
view-distance=32
tick-distance=4
player-idle-timeout=30
max-threads=8
level-name=Bedrock level
level-seed=
default-player-permission-level=member
texturepack-required=false
content-log-file-enabled=false
compression-threshold=1
compression-algorithm=zlib
server-authoritative-movement=server-auth
player-position-acceptance-threshold=0.5
player-movement-action-direction-threshold=0.85
server-authoritative-block-breaking-pick-range-scalar=1.5
chat-restriction=None
disable-player-interaction=false
client-side-chunk-generation-enabled=true
block-network-ids-are-hashes=true
disable-persona=false
disable-custom-skins=false
server-build-radius-ratio=Disabled
allow-outbound-script-debugging=false
allow-inbound-script-debugging=false
script-debugger-auto-attach=disabled
"""

PLUGIN_HELP = r"""
So You Can't Find Your Plugin

Sometimes Modrinth can be finicky and you can't find your plugin. Here are some things that could have happened:

- The plugin owner misconfigured the plugin, leading to its exclusion from results
- The plugin is listed to work on (say 1.19 +) but since it is 1.20, it works anyway but you can't find it
- You are using a forge or fabric server. This program does not officially support them but you are allowed to import them anyway

Do not worry; There are things you can do to find your plugin/mod. These are leniency settings. In leniency settings, you can change the following settings:

Enforce Version         If enabled, makes sure that the plugin explicitly lists the server version as a supported version

Enforce Software        If enabled, makes sure that the plugin explicitly supports Bukkit

Enforce Type            If enabled, makes sure that what you are downloading is actually a mod and not something else
"""

COLOURS_ACTIVE = False

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
BUNGEECORD_DOWNLOAD_URL = "https://ci.md-5.net/job/BungeeCord/lastStableBuild/artifact/bootstrap/target/BungeeCord.jar"

ON_WINDOWS = False
IN_SOURCE_TREE = False

APP_APPDATA_VERSION = 0
APP_FRIENDLY_VERSION = ""

def setup_ua(version,apiversion):
    """Super early-load function to set up the user agent"""
    global MODRINTH_USER_AGENT
    global APP_APPDATA_VERSION
    global APP_FRIENDLY_VERSION
    MODRINTH_USER_AGENT = f"Enderbyte-Programs/CraftServerSetup/{version}"
    APP_FRIENDLY_VERSION = version
    APP_APPDATA_VERSION = apiversion

def setup_early_load(windows:bool,debug:bool):
    """Early load function to set up CLI dependent and OS dependent variables"""
    global PORTABLE
    global DEVELOPER
    global AUTOSTART_ID
    global AUTOMANAGE_ID
    global APPDATADIR
    global SERVERS_BACKUP_DIR
    global SERVERSDIR
    global TEMPDIR
    global BACKUPDIR
    global DOCDOWNLOAD
    global ASSETSDIR

    #Get argparse
    _arguments.startup()
    PORTABLE = _arguments.is_portable_mode()
    DEVELOPER = _arguments.is_developer_mode()
    AUTOSTART_ID = _arguments.get_startup_id()
    AUTOMANAGE_ID = _arguments.get_manage_id()

    ogpath = sys.argv[0]
    execdir = os.path.split(os.path.abspath(ogpath))[0]
    global ON_WINDOWS
    global IN_SOURCE_TREE
    ON_WINDOWS = windows
    IN_SOURCE_TREE = debug
    if not ON_WINDOWS:
        APPDATADIR = os.path.expanduser("~/.local/share/mcserver")
        if PORTABLE:
            APPDATADIR = execdir+"/AppData"
            os.makedirs(APPDATADIR,exist_ok=True)
        SERVERSDIR = APPDATADIR + "/servers"
        SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
        TEMPDIR = APPDATADIR + "/temp"
        BACKUPDIR = os.path.expanduser("~/.local/share/crss_backup")
        ASSETSDIR = APPDATADIR + "/assets"
    else:
        
        APPDATADIR = os.path.expandvars("%APPDATA%/mcserver")
        if PORTABLE:
            APPDATADIR = execdir+"/AppData"
        SERVERSDIR = APPDATADIR + "/servers"
        SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
        TEMPDIR = APPDATADIR + "/temp"
        BACKUPDIR = os.path.expandvars("%APPDATA%/crss_backup")
        ASSETSDIR = APPDATADIR + "/assets"

    DOCDOWNLOAD = ASSETSDIR + "/craftserversetup.epdoc"