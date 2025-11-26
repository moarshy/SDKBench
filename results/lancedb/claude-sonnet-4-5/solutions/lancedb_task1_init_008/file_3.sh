# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload

# Or run directly
python app.py  # Shows info, then run uvicorn separately