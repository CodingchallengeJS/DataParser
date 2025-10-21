# --- Standard Library Imports ---
import ast
import base64
import json
import logging
import os
import re
import time
import zipfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

# --- Third-Party Library Imports ---
from dotenv import find_dotenv, load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# --- Selenium WebDriver and Options Setup ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": "D\\Python\\DataForge-automated\\MathTHPT2025",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.ebabled": "false",
    },
)

driver = webdriver.Chrome(options=options)
useOutsideOCR = 1
driver.get(
    "https://dotsocr.xiaohongshu.com/"
    if useOutsideOCR == 1
    else "https://dotsocr.trunghsgs.edu.vn/"
)

# --- Wait for Page to Load ---
wait = WebDriverWait(driver, 60)
try:
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    try:
        wait.until(EC.presence_of_element_located((By.ID, "parse_button")))
    except Exception:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
    time.sleep(1)
    print("Page loaded")
except Exception as e:
    print("Timeout waiting for page to load:", e)
    driver.quit()
    exit()

# --- Environment Variable Loading ---
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    load_dotenv()
    print("No .env file found; loaded environment from system variables")

data_dir = os.environ.get("DATA_DIR", "MathTHPT2025")
loading_folder_env = os.environ.get(
    "LOADING_FOLDER",
    '["1.Chuyen de", "2.De chac diem 8", "3.De chac diem 9", "4.De luyen them", "5.De quan trong", "6.De so"]',
)
try:
    loading_folder = json.loads(loading_folder_env)
except Exception:
    try:
        loading_folder = ast.literal_eval(loading_folder_env)
    except Exception:
        loading_folder = [
            s.strip() for s in re.split(r"[;,]", loading_folder_env) if s.strip()
        ]

# --- Logging Setup ---
log_dir = Path(data_dir)
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / "process.log"

logger = logging.getLogger("pdf_processor")
logger.setLevel(logging.INFO)

if not any(
    isinstance(h, RotatingFileHandler) and h.baseFilename == str(log_path)
    for h in logger.handlers
):
    fh = RotatingFileHandler(
        str(log_path), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

log = logger.info

# --- Main PDF Processing Loop ---
for folder in loading_folder:
    pdf_files = []
    folder_path = os.path.join(data_dir, folder)
    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            pdf_files.append(file)
            file_path = os.path.abspath(os.path.join(folder_path, file))

            file_input = driver.find_element(
                By.CSS_SELECTOR, "input[type='file'][data-testid='file-upload']"
            )
            file_input.send_keys(file_path)
            print("Sent file to upload input:", file_path)

            upload_selector = "span.uploading"
            try:
                upload_wait = WebDriverWait(driver, 1800)
                upload_wait.until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, upload_selector))
                )
                print("Upload indicator disappeared")
            except Exception as e:
                print("Timeout waiting for upload indicator to disappear:", e)

            time.sleep(2)
            parse_btn = driver.find_element(By.ID, "parse_button")
            parse_btn.click()
            print("Clicked parse button")

            try:
                tab_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "component-38-button"))
                )
                tab_btn.click()
                print("Clicked Markdown Raw Text tab")
            except Exception as e:
                print("Failed to click Markdown Raw Text tab:", e)

            file_no_ext = os.path.splitext(file)[0]
            download_dir = os.path.join(folder_path, file_no_ext, "zip")
            os.makedirs(download_dir, exist_ok=True)

            before_files = set(os.listdir(download_dir))
            try:
                driver.execute_cdp_cmd(
                    "Page.setDownloadBehavior",
                    {"behavior": "allow", "downloadPath": os.path.abspath(download_dir)},
                )
            except Exception as e:
                print("Could not set download directory via CDP:", e)

            download_wait = WebDriverWait(driver, 1800)
            btn = download_wait.until(
                EC.element_to_be_clickable((By.ID, "component-45"))
            )
            print("Target download dir:", os.path.abspath(download_dir))
            print("Download button found, clicking...")
            btn.click()

            end_time = time.time() + 1800
            downloaded_file = None
            while time.time() < end_time:
                time.sleep(0.5)
                new_files = set(os.listdir(download_dir)) - before_files
                if new_files:
                    for f in new_files:
                        if not f.endswith(".crdownload"):
                            downloaded_file = f
                            break
                if downloaded_file:
                    break

            if downloaded_file:
                print("Downloaded file:", downloaded_file)
            else:
                print("No completed download detected within timeout.")
                continue

            zip_path = os.path.join(download_dir, downloaded_file)
            extract_to = os.path.join(folder_path, file_no_ext, "output")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_to)
            print("Extracted:", zip_path, "->", extract_to)

            suffix = os.path.splitext(downloaded_file)[0].split("_")[-1]
            final_md_path = os.path.join(extract_to, "final.md")
            with open(final_md_path, "w", encoding="utf-8") as out_f:
                for i in range(100):
                    part_name = f"demo_{suffix}_page_{i}.md"
                    part_path = os.path.join(extract_to, part_name)
                    if not os.path.exists(part_path):
                        continue
                    with open(part_path, "r", encoding="utf-8") as part_f:
                        content = part_f.read()
                    out_f.write(content)
                    out_f.write("\n\n")
            print("Merged pages into:", final_md_path)

            try:
                clear_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "component-13"))
                )
                clear_btn.click()
                print("Clicked Clear button")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[type='file'][data-testid='file-upload']")
                    )
                )
                time.sleep(1)
            except Exception as e:
                print("Failed to click Clear button or wait for reset:", e)

            try:
                drop_selector = "div.wrap.svelte-12ioyct"
                WebDriverWait(driver, 1800).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, drop_selector))
                )
                print("Drop-area has reappeared")
            except Exception as e:
                print("Timeout waiting for drop-area to reappear:", e)
            print()
    print("Processed PDF files:", pdf_files)

# --- Post-Processing: Extract Base64 Images from Markdown ---
print("\nStarting post-processing of final.md files...")

image_counter = 0

def replace_base64_with_path(match, image_dir_path):
    global image_counter
    image_counter += 1
    base64_data = match.group(1)

    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += "=" * (4 - missing_padding)

    try:
        image_data = base64.b64decode(base64_data)
        image_filename = f"image_{image_counter}.png"
        image_save_path = os.path.join(image_dir_path, image_filename)

        with open(image_save_path, "wb") as img_file:
            img_file.write(image_data)

        relative_image_path = os.path.join("images", image_filename).replace("\\", "/")
        return f"![]({relative_image_path})"
    except Exception as e:
        print(f"  - Error decoding/saving image {image_counter}: {e}")
        return match.group(0)

for folder_name in loading_folder:
    folder_path = os.path.join(data_dir, folder_name)
    if not os.path.isdir(folder_path):
        continue

    for pdf_subfolder_name in os.listdir(folder_path):
        pdf_subfolder_path = os.path.join(folder_path, pdf_subfolder_name)
        if not os.path.isdir(pdf_subfolder_path):
            continue

        output_dir = os.path.join(pdf_subfolder_path, "output")
        final_md_path = os.path.join(output_dir, "final.md")

        if os.path.exists(final_md_path):
            image_dir = os.path.join(output_dir, "images")
            os.makedirs(image_dir, exist_ok=True)

            with open(final_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            image_counter = 0
            base64_pattern = re.compile(r"!\[.*?\]\(data:image;base64,(.*?)\)")
            
            # Use a lambda to pass the image_dir context to the replacement function
            new_content = base64_pattern.sub(
                lambda m: replace_base64_with_path(m, image_dir), content
            )

            with open(final_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            if image_counter > 0:
                print(f"Processed {final_md_path} and extracted {image_counter} images.")

print("\nPost-processing complete!")
driver.quit()