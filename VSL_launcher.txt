@echo off
TITLE Vibration System Launcher
echo ===================================================
echo   STARTING VIBRATION FAULT DETECTION SYSTEM
echo ===================================================

:: --- CONFIGURATION (UPDATE THESE PATHS!) ---
:: Path to your Mosquitto folder
SET MOSQUITTO_PATH="C:\Program Files\mosquitto\mosquitto.exe"

:: Path to your Config file (Where did you save my_config.conf?)
:: Example: "C:\Program Files\mosquitto\my_config.conf" or "C:\Users\You\Desktop\my_config.conf"
SET CONF_PATH="C:\Program Files\mosquitto\my_config.conf"

:: Path to your Python Project 'backend' folder
:: Example: "C:\Users\You\Documents\Project\backend"
SET PROJECT_PATH="D:\Dao of Bits\EL_Sem1"

:: -------------------------------------------

echo 1. Launching MQTT Broker...
start "Mosquitto Broker" %MOSQUITTO_PATH% -v -c %CONF_PATH%

echo 2. Waiting 2 seconds for Broker to stabilize...
timeout /t 2 /nobreak >nul

echo 3. Launching Receiver Script...
cd %PROJECT_PATH%
start "Receiver Logic" python server_DL.py

echo 4. Launching Web Dashboard...
:: We are already in the backend folder from the previous command
SET PROJECT_PATH="D:\Dao of Bits\EL_Sem1\dashboard"
cd %PROJECT_PATH%
start "Flask Dashboard" python app.py

echo 5. Opening Web Browser...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo ===================================================
echo   SYSTEM IS LIVE.
echo   CLOSE THE POP-UP WINDOWS TO STOP THE SYSTEM.
echo ===================================================
pause