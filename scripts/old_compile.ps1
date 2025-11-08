curl "https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/src/craftserversetup.py" -OutFile C:\Python\Scripts\craftserversetup.py
curl "https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/src/translations.toml" -OutFile C:\Python\Scripts\translations.toml
Push-Location C:\Python\Scripts
rm C:\Python\Scripts\dist\craftserversetup -Recurse
.\pyinstaller --icon=mc.ico --version-file=vf.txt -y craftserversetup.py
Pop-Location
sleep 5
Start-Process -FilePath "C:\Program Files (x86)\Inno Setup 6\Compil32.exe" -ArgumentList "/cc C:\Python\Scripts\crss.iss" -Wait
copy C:\Python\Scripts\dist\startupflags.txt C:\Python\Scripts\dist\craftserversetup\startupflags.txt
Compress-Archive -DestinationPath craftserversetup-portable.zip -Path C:\Python\Scripts\dist\craftserversetup -CompressionLevel Optimal -Force