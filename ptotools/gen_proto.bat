@echo off
chcp 936 >nul 2>&1
set "PYTHONIOENCODING=gbk"

set "scriptdir=%~dp0"
pushd "%scriptdir%" || exit /b 1

echo Start generating protocol files...

rem Set proto directory
set "PROTO_DIR=.\proto\proto_desc"

rem 1. Generate netPb.lua and netPb.json (Protocol IDs)
echo Running extractlua.py...
python script/extractlua.py "%PROTO_DIR%"
if errorlevel 1 (
    echo Failed to run extractlua.py
    pause
    exit /b 1
)

rem 2. Generate .pb and .cs files (Protocol Buffers)
echo Running extractluapb.py...
python script/extractluapb.py "%PROTO_DIR%"
if errorlevel 1 (
    echo Failed to run extractluapb.py
    pause
    exit /b 1
)

echo All protocol files generated successfully.
pause
