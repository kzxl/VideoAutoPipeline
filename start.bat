@echo off
title Video Creator v3 - Starting...
echo ==================================================
echo  Video Creator v3
echo  Backend: http://localhost:5050
echo  Frontend: http://localhost:5173
echo ==================================================
echo.

:: Start Flask API in background
start "Flask API" cmd /k "cd /d e:\15. Other\VideoAutoPipeline\api && py app.py"

:: Wait for Flask to start
timeout /t 2 /nobreak >nul

:: Start Vite dev server
cd /d "e:\15. Other\VideoAutoPipeline\web"
npm run dev
