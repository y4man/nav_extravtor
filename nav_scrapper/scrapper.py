# from gologin import GoLogin
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import time
# import os
# from dotenv import load_dotenv

# load_dotenv()

# def scrape_navbar_links(query):
#     GOLOGIN_TOKEN = os.getenv("GOLOGIN_TOKEN")
#     PROFILE_ID = os.getenv("GOLOGIN_PROFILE_ID")
#     CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

#     if not all([GOLOGIN_TOKEN, PROFILE_ID, CHROMEDRIVER_PATH]):
#         raise ValueError("Missing one or more environment variables: GOLOGIN_TOKEN, PROFILE_ID, CHROMEDRIVER_PATH")

#     print("TOKEN:", GOLOGIN_TOKEN)
#     print("PROFILE_ID:", PROFILE_ID)
#     print("CHROMEDRIVER:", CHROMEDRIVER_PATH)

#     gologin = GoLogin({
#         "token": GOLOGIN_TOKEN,
#         "profile_id": PROFILE_ID,
#         "port": 3500
#     })

#     # Prevent AttributeError inside gologin internals
#     if not hasattr(gologin, 'profile_path'):
#         gologin.profile_path = ""

#     debugger_address = None
#     driver = None

#     try:
#         debugger_address = gologin.start()

#         options = webdriver.ChromeOptions()
#         options.debugger_address = debugger_address
#         service = Service(CHROMEDRIVER_PATH)
#         driver = webdriver.Chrome(service=service, options=options)
#         wait = WebDriverWait(driver, 10)

#         driver.get("https://www.google.com")
#         time.sleep(2)

#         try:
#             accept_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]")))
#             accept_btn.click()
#         except TimeoutException:
#             pass

#         search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
#         search_box.send_keys(query)
#         search_box.send_keys(Keys.RETURN)
#         time.sleep(2)

#         h3_elements = driver.find_elements(By.CSS_SELECTOR, "a h3")
#         first_valid_result = None
#         for h3 in h3_elements:
#             try:
#                 parent_a = h3.find_element(By.XPATH, "./ancestor::a")
#                 href = parent_a.get_attribute("href")
#                 if href and "google" not in href:
#                     first_valid_result = parent_a
#                     break
#             except Exception:
#                 continue

#         if not first_valid_result:
#             raise Exception("No valid search result found.")

#         website_url = first_valid_result.get_attribute("href")
#         driver.get(website_url)
#         time.sleep(3)

#         try:
#             nav = driver.find_element(By.TAG_NAME, 'nav')
#             links = nav.find_elements(By.TAG_NAME, 'a')
#         except:
#             header = driver.find_element(By.TAG_NAME, 'header')
#             links = header.find_elements(By.TAG_NAME, 'a')

#         navbar_links = []
#         for link in links:
#             href = link.get_attribute("href")
#             text = link.text.strip()
#             if href:
#                 navbar_links.append((text, href))

#         return website_url, navbar_links

#     except Exception as e:
#         print("Scraping failed:", e)
#         return None, []

#     finally:
#         # Clean up safely
#         if driver:
#             try:
#                 driver.quit()
#             except Exception as e:
#                 print("Driver quit failed:", e)
#         if debugger_address:
#             try:
#                 gologin.stop()
#             except Exception as e:
#                 print("gologin stop failed:", e)


from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from dotenv import load_dotenv
import psutil
import subprocess

load_dotenv()
gologin_browser_pid = None
driver_instance = None  # initialize at module level
gologin_instance = None

def scrape_navbar_links(query, stop_event=None):
    GOLOGIN_TOKEN = os.getenv("GOLOGIN_TOKEN")
    PROFILE_ID = os.getenv("GOLOGIN_PROFILE_ID")
    CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

    if not all([GOLOGIN_TOKEN, PROFILE_ID, CHROMEDRIVER_PATH]):
        raise ValueError("Missing one or more environment variables: GOLOGIN_TOKEN, PROFILE_ID, CHROMEDRIVER_PATH")

    gologin = GoLogin({
        "token": GOLOGIN_TOKEN,
        "profile_id": PROFILE_ID,
        "port": 3500
    })

    debugger_address = None
    driver = None

    try:
        debugger_address = gologin.start()
        global gologin_instance, driver_instance, gologin_browser_pid
        gologin_instance = gologin  # save instance globally
        gologin_browser_pid = get_gologin_chrome_pid(debugger_address)

        if stop_event and stop_event.is_set():
            raise Exception("Scraping stopped before browser start")

        options = webdriver.ChromeOptions()
        options.debugger_address = debugger_address
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 10)

        # Google Search
        driver.get("https://www.google.com")
        if stop_event and stop_event.is_set():
            raise Exception("Scraping stopped after opening Google")

        # Cookie banner
        try:
            accept_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]")))
            accept_btn.click()
        except TimeoutException:
            pass

        if stop_event and stop_event.is_set():
            raise Exception("Scraping stopped before search")

        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        if stop_event and stop_event.is_set():
            raise Exception("Scraping stopped after submitting search")

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a h3")))
        h3_elements = driver.find_elements(By.CSS_SELECTOR, "a h3")

        first_valid_result = None
        for h3 in h3_elements:
            if stop_event and stop_event.is_set():
                raise Exception("Scraping stopped while analyzing search results")

            try:
                parent_a = h3.find_element(By.XPATH, "./ancestor::a")
                href = parent_a.get_attribute("href")
                if href and "google" not in href:
                    first_valid_result = parent_a
                    break
            except Exception:
                continue

        if not first_valid_result:
            raise Exception("No valid search result found.")

        website_url = first_valid_result.get_attribute("href")

        driver.get(website_url)
        if stop_event and stop_event.is_set():
            raise Exception("Scraping stopped after navigating to website")

        # Try nav > a first, fallback to header > a
        links = []
        try:
            nav = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
            links = nav.find_elements(By.TAG_NAME, 'a')
        except Exception:
            try:
                header = driver.find_element(By.TAG_NAME, 'header')
                links = header.find_elements(By.TAG_NAME, 'a')
            except Exception:
                pass

        navbar_links = []
        for link in links:
            if stop_event and stop_event.is_set():
                raise Exception("Scraping stopped while collecting links")

            href = link.get_attribute("href")
            text = link.text.strip() or link.get_attribute("aria-label") or link.get_attribute("title") or "No text"
            if href:
                navbar_links.append((text, href))

        return website_url, navbar_links

    except Exception as e:
        print("Scraping stopped or failed:", e)
        return "", []

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print("Driver quit failed:", e)
        if debugger_address:
            try:
                gologin.stop()
            except Exception as e:
                print("GoLogin stop failed:", e)

def get_gologin_chrome_pid(debugger_address):
    """Find Chrome process started by GoLogin matching debugger port."""
    try:
        port = debugger_address.split(":")[-1]
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'chrome' in (proc.info['name'] or '').lower():
                cmdline = ' '.join(proc.info['cmdline'])
                if f"--remote-debugging-port={port}" in cmdline:
                    return proc.info['pid']
    except Exception as e:
        print(f"[WARNING] Couldn't find GoLogin Chrome PID: {e}")
    return None



def stop_scraping_immediately():
    print('destroyer active')
    global driver_instance, gologin_instance, gologin_browser_pid

    # Step 1: Quit Selenium Driver (Safe)
    if driver_instance is not None:
        try:
            driver_instance.quit()
            print("[INFO] Selenium driver stopped successfully.")
        except Exception as e:
            print(f"[WARNING] Error stopping Selenium driver: {e}")
        finally:
            driver_instance = None

    # Step 2: Stop GoLogin profile safely
    if gologin_instance is not None:
        try:
            profile_path = getattr(gologin_instance, "profile_path", None)
            if profile_path and os.path.exists(profile_path):
                gologin_instance.stop()
                print("[INFO] GoLogin profile stopped successfully.")
            else:
                print("[WARNING] GoLogin profile path already deleted or not set.")
        except FileNotFoundError:
            print("[WARNING] GoLogin profile already removed.")
        except Exception as e:
            print(f"[WARNING] Error stopping GoLogin profile: {e}")
        finally:
            gologin_instance = None

    # Step 3: Kill the exact GoLogin Chrome browser PID (safe kill)
    if gologin_browser_pid:
        try:
            proc = psutil.Process(gologin_browser_pid)
            proc.kill()
            print(f"[INFO] Killed GoLogin Chrome process PID {gologin_browser_pid}")
        except psutil.NoSuchProcess:
            print(f"[INFO] GoLogin Chrome process PID {gologin_browser_pid} already exited.")
        except Exception as e:
            print(f"[WARNING] Failed to kill GoLogin Chrome process: {e}")
        finally:
            gologin_browser_pid = None
