@echo off

REM Create the app directory and its subdirectories
mkdir app
mkdir app\templates
mkdir app\static
mkdir app\static\css
mkdir app\static\js

REM Create the Python files
type nul > app\__init__.py
type nul > app\main.py
type nul > app\routes.py
type nul > app\pdf_processing.py
type nul > app\gemini_client.py

REM Create the HTML templates
type nul > app\templates\base.html
type nul > app\templates\index.html

REM Create the CSS and JavaScript files
type nul > app\static\css\style.css
type nul > app\static\js\script.js

REM Create the root-level files
type nul > Dockerfile
type nul > docker-compose.yml
type nul > requirements.txt
type nul > README.md

echo Directory structure created successfully!