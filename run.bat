@echo off
echo ========================================================
echo   AI Learning Path Generator - Starting Streamlit App
echo ========================================================
echo.

IF EXIST ".venv\Scripts\python.exe" (
    echo Using project virtual environment...
    ".venv\Scripts\python.exe" -m streamlit run app.py
) ELSE (
    echo Virtual environment not found. Attempting to use system python...
    python -m streamlit run app.py
)

pause
