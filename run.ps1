# AI Learning Path Generator - PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  AI Learning Path Generator - Starting Streamlit App" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "Starting Streamlit via local virtual environment..." -ForegroundColor Green
    & ".\.venv\Scripts\python.exe" -m streamlit run app.py
} else {
    Write-Host "Virtual environment not found. Using system python..." -ForegroundColor Yellow
    python -m streamlit run app.py
}
