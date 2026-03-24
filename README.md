# Captcha Demo — Python Selenium (POM)

Converted from the original Java/TestNG/Maven project to **Python + Selenium + pytest**.

---

## Project Structure

```
captchademo_python/
│
├── browser_setup/
│   ├── __init__.py
│   └── setup_browser.py       # Equiv. of SetupBrowser.java (@BeforeClass / @AfterClass)
│
├── pages/
│   ├── __init__.py
│   └── login_page.py          # Equiv. of LoginPage.java (POM with @FindBy)
│
├── tests/
│   ├── __init__.py
│   └── test_captcha_login.py  # Equiv. of CaptchaLogin.java + positive/negative scenarios
│
├── screenshots/               # Runtime screenshots (auto-created)
├── screenshot/                # Captcha OCR screenshot (captcha.png)
├── tessdata/                  # Place eng.traineddata here (copy from original project)
│
├── conftest.py                # pytest fixtures — driver setup / teardown
├── pytest.ini                 # pytest config + HTML report
└── requirements.txt           # Python dependencies
```

---

## Java → Python Mapping

| Java (TestNG/Maven)                | Python (pytest/Selenium)                  |
|------------------------------------|-------------------------------------------|
| `SetupBrowser.java` @BeforeClass   | `conftest.py` → `driver` fixture (setup)  |
| `SetupBrowser.java` @AfterClass    | `conftest.py` → `driver` fixture (teardown via `yield`) |
| `LoginPage.java` extends SetupBrowser | `LoginPage(driver)` in `pages/login_page.py` |
| `@FindBy(xpath=...)` + PageFactory | `@property` + `WebDriverWait` in LoginPage |
| `CaptchaLogin.java` extends SetupBrowser | `TestCaptchaLogin` class with `@pytest.mark.usefixtures("driver")` |
| `@Test` method                     | `def test_*()` method                     |
| `Tesseract.doOCR()` (Tess4J)       | `pytesseract.image_to_string()` (pytesseract) |
| `driver.manage().window().maximize()` | `driver.maximize_window()`              |
| `Thread.sleep(5000)`               | `time.sleep(5)` / `WebDriverWait`         |
| `FileUtils.copyFile(src, dest)`    | `element.screenshot(path)` (built-in)    |
| Log4j `LogManager.getLogger()`     | `logging.getLogger()`                    |

---

## Prerequisites

### 1. Python 3.9+
```bash
python --version
```

### 2. Tesseract OCR installed on your system

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
(Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Linux:**
```bash
sudo apt install tesseract-ocr
```

### 3. Copy tessdata
Copy the `eng.traineddata` from your original Java project:
```
captchademo/tessdata/eng.traineddata
         ↓
captchademo_python/tessdata/eng.traineddata
```

---

## Installation

```bash
cd captchademo_python
pip install -r requirements.txt
```

---

## Running Tests

### Run all tests (Chrome, default):
```bash
pytest
```

### Run with Edge browser:
```bash
pytest --browser=edge
```

### Run only positive tests:
```bash
pytest -k "pos"
```

### Run only negative tests:
```bash
pytest -k "neg"
```

### Run a specific test:
```bash
pytest tests/test_captcha_login.py::TestCaptchaLogin::test_tc_pos_04_captcha_ocr_extracts_text -v
```

### Generate HTML report:
```bash
pytest --html=reports/report.html --self-contained-html
```

---

## Test Cases Summary

### ✅ Positive Scenarios (8 tests)

| Test ID     | Description                                          |
|-------------|------------------------------------------------------|
| TC_POS_01   | Verify login page loads with all expected elements   |
| TC_POS_02   | Username field accepts typed text                    |
| TC_POS_03   | Password field accepts text and masks it             |
| TC_POS_04   | OCR successfully extracts non-empty captcha text     |
| TC_POS_05   | Full end-to-end login flow with OCR captcha          |
| TC_POS_06   | Captcha field accepts alphanumeric text              |
| TC_POS_07   | Page refresh generates a new captcha                 |
| TC_POS_08   | Fields can be cleared and re-entered                 |

### ❌ Negative Scenarios (12 tests)

| Test ID     | Description                                          |
|-------------|------------------------------------------------------|
| TC_NEG_01   | Login with wrong captcha text                        |
| TC_NEG_02   | Submit with empty username                           |
| TC_NEG_03   | Submit with empty password                           |
| TC_NEG_04   | Submit without filling captcha field                 |
| TC_NEG_05   | Submit with all fields empty                         |
| TC_NEG_06   | Invalid username and wrong password                  |
| TC_NEG_07   | SQL injection in username field                      |
| TC_NEG_08   | SQL injection in password field                      |
| TC_NEG_09   | Excessively long username (300 chars)                |
| TC_NEG_10   | Special characters in captcha field                  |
| TC_NEG_11   | Captcha in wrong case (case-sensitivity check)       |
| TC_NEG_12   | Whitespace-only username                             |
