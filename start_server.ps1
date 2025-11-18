# PowerShell script to start the Django server
Set-Location $PSScriptRoot
& .\venv\Scripts\Activate.ps1
python manage.py runserver

