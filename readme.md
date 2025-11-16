/mpti-chatbase/
│
├── wordpress/
│   ├── mpti-chatbase.php       # Main plugin
│   ├── assets/
│   │   ├── chatbot.js
│   │   ├── chatbot.css
│   └── includes/
│       ├── api-handler.php
│       └── admin-panel.php
│
└── backend/
    ├── app.py                  # Flask AI backend
    ├── embedder.py             # Text vectorization
    ├── data/                   # Trained FAQ text files
    └── chroma/                 # Local vector database

    cd python-backend && quick_start.bat
To get started, simply run start_mpti_backend.bat and then test the system with python test_scraper.py to verify everything is working correctly!

python view_database.py
python view_database.py tact-program
python db_browser.py