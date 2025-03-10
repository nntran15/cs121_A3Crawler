# CS121 Web Scraper

## Building the index

1) Download and install the developer.zip file into /backend/
2) cd into /backend/ and unzip developer.zip, which should create a /backend/DEV/ folder with associated subdirectories as subfolders
3) Run 'python indexer.py'
4) After a few minutes of compiling time, the following folders will be created:
    a) '/backend/tmp/': stores partial indexes of size 'batch_size' (as defined in indexer.py) offloaded onto disk from memory
    b) '/backend/index/': stores inverted indexes as .pkl files
        NOTE: also contains key.pkl files for faster searching through inverted indexes, as well as the complete final_inverted_index.pkl file


## Running the search engine locally

1) cd into /backend/ and run 'python search.py'
2) Type in queries into the terminal and hit "enter" to return the top 5 urls


## Building the web app

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
python -c "import nltk; nltk.download('punkt_tab')" # if you do not have punkt_tab for nltk installed
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

Now open the link returned.