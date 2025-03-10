# CS121 Web Scraper
## Build Instructions
Instructions for setting up web app for the first time
### Frontend
Move into the frontend directory and run the following commands:
```
npm install
```
Note: node must be installed

### Backend

Move into the backend and run the following commands:
```
pip install -r requirements.txt
python -c "import nltk; nltk.download("punkt_tab") # if you do not have punkt_tab for nltk installed
```

Now create a file named .env in the backend directory and put in your gemini key:
```
GEMINI_KEY='YOUR_KEY_HERE'
```

## Run Instructions

Move into the backend directory and run the following commands:
```
flask --app app.py run
```
Now create a new terminal (or use a tool like concurrently) and move into the frontend directory and run:
```
npm run dev
```
Now open the link returned 