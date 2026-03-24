"""
pages/login_page.py

Python equivalent of:
  captchademo/src/main/java/Pages/LoginPage.java

Page Object Model for the PMAY Login page:
  https://pmaymis.gov.in/Auth/Login.aspx

Covers:
- Username / Password / Captcha field interactions
- OCR-based captcha extraction using pytesseract (equiv. of Tess4J)
- Screenshot saving of the captcha image element
"""

import os
import re
import logging
from PIL import Image

import pytesseract
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ─── Locators ─────────────────────────────────────────────────────────────────
# Equivalent of @FindBy annotations in Java LoginPage.java

USERNAME_XPATH   = "//*[@id='txtusername']"
PASSWORD_XPATH   = "//*[@id='txtpassword']"
CAPTCHA_IMG_XPATH = "//*[@id='img_pass']"
CAPTCHA_INPUT_XPATH = "//*[@id='txtcaptcha']"
LOGIN_BTN_XPATH  = "//input[@type='submit'] | //button[@type='submit'] | //*[@id='btnlogin']"
ERROR_MSG_XPATH  = "//*[contains(@class,'error') or contains(@id,'error') or contains(@class,'alert')]"

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshot")
TESSDATA_DIR   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tessdata")


class LoginPage:
    """
    Page Object for the PMAY login page.
    Equivalent of Java LoginPage class using PageFactory + @FindBy.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.logger = logging.getLogger(self.__class__.__name__)

    # ── Element Properties (lazy) ─────────────────────────────────────────────
    # Equivalent of @FindBy fields initialised by PageFactory.initElements()

    @property
    def username_field(self) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, USERNAME_XPATH)))

    @property
    def password_field(self) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, PASSWORD_XPATH)))

    @property
    def captcha_image(self) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, CAPTCHA_IMG_XPATH)))

    @property
    def captcha_input(self) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, CAPTCHA_INPUT_XPATH)))

    @property
    def login_button(self) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BTN_XPATH)))

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_username(self, username: str = "vignesh"):
        """Equivalent of EnterUsername() in Java."""
        field = self.username_field
        field.clear()
        field.send_keys(username)
        self.logger.info(f"Entered username: {username}")

    def enter_password(self, password: str = "vignesh"):
        """Equivalent of EnterPassword() in Java."""
        field = self.password_field
        field.clear()
        field.send_keys(password)
        self.logger.info("Entered password.")

    def locate_and_convert_captcha(self) -> str:
        """
        Equivalent of LocateandConvertcapctha() in Java.

        Steps:
          1. Takes a screenshot of ONLY the captcha <img> element.
          2. Saves it to /screenshot/captcha.png
          3. Runs pytesseract OCR (equiv. of Tess4J Tesseract.doOCR).
          4. Strips non-alphanumeric characters.
          5. Returns the cleaned captcha text.
        """
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        dest_path = os.path.join(SCREENSHOT_DIR, "captcha.png")

        # Screenshot of only the captcha element (equiv. getScreenshotAs on WebElement)
        captcha_element = self.captcha_image
        captcha_element.screenshot(dest_path)
        self.logger.info(f"Captcha screenshot saved to: {dest_path}")

        # OCR via pytesseract — equivalent of Tesseract.doOCR()
        # Configure: PSM 7 = treat image as a single text line (good for captchas)
        custom_config = r"--oem 3 --psm 7"

        if os.path.isdir(TESSDATA_DIR):
            pytesseract.pytesseract.tesseract_cmd = _find_tesseract()

        image = Image.open(dest_path)
        captcha_text: str = pytesseract.image_to_string(image, config=custom_config)

        # Clean — equivalent of replaceAll("[^a-zA-Z0-9]", "")
        captcha_text = re.sub(r"[^a-zA-Z0-9]", "", captcha_text)
        self.logger.info(f"OCR captcha text: '{captcha_text}'")

        return captcha_text

    def enter_captcha(self, captcha_text: str):
        """Equivalent of captchaenter() in Java."""
        field = self.captcha_input
        field.clear()
        field.send_keys(captcha_text)
        self.logger.info(f"Entered captcha: '{captcha_text}'")

    def click_login(self):
        """Click the Login / Submit button."""
        self.login_button.click()
        self.logger.info("Clicked login button.")

    def get_error_message(self) -> str:
        """
        Returns visible error/alert message text after a failed login attempt.
        Used for negative scenario assertions.
        """
        try:
            error_el = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, ERROR_MSG_XPATH))
            )
            return error_el.text.strip()
        except Exception:
            return ""

    def is_login_successful(self) -> bool:
        """
        Returns True if the URL changed away from the login page
        (i.e., login succeeded).
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_changes("https://pmaymis.gov.in/Auth/Login.aspx")
            )
            return True
        except Exception:
            return False

    def is_captcha_field_empty(self) -> bool:
        """Returns True if captcha input is present but has no value — negative check."""
        return self.captcha_input.get_attribute("value") == ""

    def reload_page(self):
        """Refreshes the page to get a fresh captcha."""
        self.driver.refresh()
        self.logger.info("Page refreshed for new captcha.")


# ─── Helper ───────────────────────────────────────────────────────────────────

def _find_tesseract() -> str:
    """Auto-locate tesseract binary on common OS paths."""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",   # Windows
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",                                # Linux
        "/usr/local/bin/tesseract",                          # macOS Homebrew
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return "tesseract"  # Fallback: assume it's on PATH
