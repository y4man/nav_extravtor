# 🕸️ GoLogin + Selenium Navbar Scraper (with Django) BY Muhammad Yaman

This project allows you to:
- Launch a GoLogin profile with Selenium
- Perform automated Google search
- Visit the first relevant website
- Scrape navigation bar (`<nav>` or `<header>`) links
- Stop scraping anytime via a "stop" route
- Prevent killing personal Chrome instances by isolating only the GoLogin-launched browser

---

## ⚙️ Prerequisites

Make sure the following are installed on your system:

- Python 3.9+
- Google Chrome (installed on your system)
- ChromeDriver (matching your Chrome version)
- Virtual environment (recommended)
- GoLogin account + created profile

---

## 🔧 Installation

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/gologin-navbar-scraper.git
cd gologin-navbar-scraper
```

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

.ENV
i have already set my own gologin PROFILE_ID  and TOKEN you can use your own 

GOLOGIN_TOKEN=your_gologin_api_token
GOLOGIN_PROFILE_ID=your_profile_id

selenium need version 134.. CHROME DRIVER so SET IT WITH THIS PROJECT THEN ASSIGN COMPLETE PATH OF THAT DRIVER
CHROMEDRIVER_PATH=/full/path/to/chromedriver

FINALLY RUN IT,
python manage.py runserver
