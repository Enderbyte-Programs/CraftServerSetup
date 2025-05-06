#define MyAppName "Craft Server Setup"



#define MyAppVersion "1.50.2"
;The above line must be on line 5!




#define MyAppPublisher "Enderbyte Programs"
#define MyAppURL "https://enderbyteprograms.net"
#define MyAppExeName "craftserversetup.exe"
#define MyAppAssocName "Minecraft Server"
#define MyAppAssocExt ".amc"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{46F44661-8B88-481E-915B-CCA93A0742CE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=C:\Python\crss\LICENSE
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\python\crss\installer





OutputBaseFilename=CraftServerSetup-1.50.2-installer
;The above line MUST be on line 42





SetupIconFile=C:\Python\crss\mc.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName},0
UninstallDisplayName=CraftServerSetup
WizardImageFile=C:\Python\crss\sidebar.bmp
WizardSmallImageFile=C:\Python\crss\icon.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";
Name: "reg";Description: "Register .amc file extension";GroupDescription: "Registry";

[Files]
Source: "C:\Python\crss\dist\craftserversetup\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "C:\Python\Scripts\craftserversetup.epdoc";DestDir:"{userappdata}\mcserver\assets"; Flags: ignoreversion
Source: "C:\Python\crss\translations.toml"; DestDir: "{userappdata}\mcserver"; Flags: ignoreversion
Source: "C:\Python\crss\defaulticon.png";DestDir:"{userappdata}\mcserver\assets"; Flags: ignoreversion
Source: "C:\Python\crss\LICENSE";DestDir:"{userappdata}\mcserver\assets"; Flags: ignoreversion
;Source: "C:\Users\jorda\Downloads\mc.ico"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue;Tasks: reg
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey ;Tasks: reg
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0" ;Tasks: reg
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""  ;Tasks: reg
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".amc"; ValueData: ""  ;Tasks: reg

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

