"""
browser_setup/setup_browser.py

Python equivalent of:
  captchademo/src/main/java/BrowserSetup/SetupBrowser.java

Handles:
- Chrome / Edge driver initialization with options
- Screenshot capture utility
- Logging setup
"""

import os
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# ─── Constants ────────────────────────────────────────────────────────────────
LOGIN_URL = "https://pmaymis.gov.in/Auth/Login.aspx"
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


class SetupBrowser:
    """
    Equivalent of Java SetupBrowser class.
    Initializes WebDriver, navigates to the login URL,
    and provides screenshot capture utility.
    """

    def __init__(self, browser: str = "chrome"):
        self.browser = browser.lower()
        self.driver = None

        # Logging — equivalent of LogManager.getLogger()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        self._initialize_driver()

    # ── Driver Initialization ────────────────────────────────────────────────

    def _initialize_driver(self):
        """
        Equivalent of setup() @BeforeClass in Java.
        Launches Chrome or Edge with options that mirror the Java ChromeOptions.
        """
        if self.browser == "chrome":
            self.driver = self._create_chrome_driver()
        elif self.browser == "edge":
            self.driver = self._create_edge_driver()
        else:
            raise ValueError(f"Unsupported browser: '{self.browser}'. Use 'chrome' or 'edge'.")

        self.logger.info(f"Launched {self.browser} browser.")

        self.driver.delete_all_cookies()
        self.driver.get(LOGIN_URL)
        self.driver.maximize_window()

        self.logger.info(f"Navigated to: {LOGIN_URL}")

    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Chrome with options equivalent to Java ChromeOptions."""
        options = ChromeOptions()

        # Equivalent: excludeSwitches "enable-automation"
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Equivalent: --remote-allow-origins=*
        options.add_argument("--remote-allow-origins=*")

        # Equivalent: --disable-notifications
        options.add_argument("--disable-notifications")

        # Equivalent: acceptInsecureCerts / ACCEPT_INSECURE_CERTS
        options.accept_insecure_certs = True

        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _create_edge_driver(self) -> webdriver.Edge:
        """Edge driver with equivalent options."""
        options = EdgeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--disable-notifications")

        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_driver(self) -> webdriver.Chrome:
        """Return the initialized WebDriver instance."""
        return self.driver

    # ── Screenshot Utility ────────────────────────────────────────────────────

    def capture_screen(self, test_name: str) -> str:
        """
        Equivalent of captureScreen() in Java.
        Takes a screenshot and saves it to /screenshots/<test_name>_<timestamp>.png
        Returns the file path.
        """
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)

        self.driver.save_screenshot(filepath)
        self.logger.info(f"Screenshot saved: {filepath}")

        return filepath
