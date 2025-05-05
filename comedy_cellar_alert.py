from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import smtplib
from email.message import EmailMessage

def setup_chrome_driver():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def check_sets_after_dropdown_selection(driver, dropdown_id="cc_lineup_select_dates", wait_time=1):
    newMaterialArr = []

    # Find the dropdown element
    dropdown = Select(driver.find_element(By.ID, dropdown_id))

    # Step 1: Iterate through all dropdown options
    for index in range(len(dropdown.options)):
        # Step 2: Select the option by index
        dropdown.select_by_index(index)

        # Step 3: Wait for the content to load
        time.sleep(wait_time)
        
        # Step 4: Wait for the element with the class 'sets' to appear
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sets"))
            )

            # Get fully rendered page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            titles = soup.find_all('span', class_='title')
        
            if not titles:
                print("⚠️ No titles found - check if page loaded correctly")
            else:
                print("Titles found")
            
            for title in titles:
                if ("new material" in title.text.strip().lower()):
                    newMaterialArr.append(dropdown.options[index].text + ": " + title.text.strip())
        except:
            print(f"Element with class 'sets' not found after selecting index {index}.")

    return newMaterialArr


def send_comedy_cellar_notification(body, sender_email, app_password):
    subject = "Comedy Cellar Notification"
    receiver_email = sender_email  # sending to yourself

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    print("🔍 Starting Comedy Cellar scraper...")

    print("🚀 Launching Chrome browser...")
    driver = setup_chrome_driver()
        
    print("🌐 Loading Comedy Cellar website...")
    driver.get("https://www.comedycellar.com/new-york-line-up/")
        
    # Wait for dynamic content to load
    print("⏳ Waiting for page to render...")
    titles = check_sets_after_dropdown_selection(driver)

    send_comedy_cellar_notification(
        f"New material alert! {' '.join(titles)}",
        sender_email="ericspollen@gmail.com",
        app_password=os.getenv("EMAIL_PASSWORD")
    )