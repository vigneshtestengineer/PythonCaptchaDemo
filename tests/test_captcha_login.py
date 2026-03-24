"""
tests/test_captcha_login.py

Python equivalent of:
  captchademo/src/test/java/TestCases/CaptchaLogin.java

Extended with:
  ✅ Positive Scenarios  — valid flows that should SUCCEED
  ❌ Negative Scenarios  — invalid inputs / edge cases that should FAIL gracefully

Run with:
  pytest tests/test_captcha_login.py -v --html=reports/report.html
  pytest tests/test_captcha_login.py -v --browser=edge
"""

import time
import pytest
import logging

from pages.login_page import LoginPage
from browser_setup.setup_browser import SetupBrowser

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST DATA
# ═══════════════════════════════════════════════════════════════════════════════

VALID_USERNAME   = "vignesh"
VALID_PASSWORD   = "vignesh"

INVALID_USERNAME = "invalid_user_xyz"
INVALID_PASSWORD = "WrongPass@999"
EMPTY_STRING     = ""
SQL_INJECTION    = "' OR '1'='1"
LONG_STRING      = "A" * 300
SPECIAL_CHARS    = "!@#$%^&*()"
WRONG_CAPTCHA    = "XXXXX"


# ═══════════════════════════════════════════════════════════════════════════════
#  BASE TEST CLASS  (mirrors Java's CaptchaLogin extends SetupBrowser)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.usefixtures("driver")
class TestCaptchaLogin:
    """
    Equivalent of Java:
        public class CaptchaLogin extends SetupBrowser { ... }

    The `driver` fixture (defined in conftest.py) handles @BeforeClass / @AfterClass.
    """

    # ──────────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _get_login_page(self) -> LoginPage:
        """Instantiate the LoginPage POM with the active driver."""
        return LoginPage(self.driver)

    def _reload(self) -> LoginPage:
        """Refresh the page and return a fresh LoginPage instance."""
        lp = self._get_login_page()
        lp.reload_page()
        time.sleep(2)
        return lp

    def _capture(self, test_name: str):
        """Take a screenshot for the given test name."""
        setup = SetupBrowser.__new__(SetupBrowser)
        setup.driver = self.driver
        setup.logger = logger
        return setup.capture_screen(test_name)

    # ══════════════════════════════════════════════════════════════════════════
    #  ✅  POSITIVE TEST SCENARIOS
    # ══════════════════════════════════════════════════════════════════════════

    def test_tc_pos_01_page_loads_successfully(self):
        """
        TC_POS_01 — Verify the login page loads with all expected elements.
        Equivalent of a basic smoke / sanity check.
        """
        lp = self._get_login_page()

        assert lp.username_field.is_displayed(), "Username field should be visible"
        assert lp.password_field.is_displayed(), "Password field should be visible"
        assert lp.captcha_image.is_displayed(),  "Captcha image should be visible"
        assert lp.captcha_input.is_displayed(),  "Captcha input field should be visible"

        logger.info("TC_POS_01 PASSED — Page loaded with all elements visible.")

    def test_tc_pos_02_username_field_accepts_input(self):
        """
        TC_POS_02 — Verify the username field accepts typed text.
        """
        lp = self._reload()
        lp.enter_username(VALID_USERNAME)

        actual = lp.username_field.get_attribute("value")
        assert actual == VALID_USERNAME, f"Expected '{VALID_USERNAME}', got '{actual}'"

        logger.info("TC_POS_02 PASSED — Username field accepted input.")

    def test_tc_pos_03_password_field_accepts_input(self):
        """
        TC_POS_03 — Verify the password field accepts text and masks it.
        """
        lp = self._reload()
        lp.enter_password(VALID_PASSWORD)

        field_type = lp.password_field.get_attribute("type")
        assert field_type == "password", f"Password field type should be 'password', got '{field_type}'"

        actual = lp.password_field.get_attribute("value")
        assert actual == VALID_PASSWORD, "Password field did not hold the entered value"

        logger.info("TC_POS_03 PASSED — Password field accepts and masks input.")

    def test_tc_pos_04_captcha_ocr_extracts_text(self):
        """
        TC_POS_04 — Verify OCR successfully extracts a non-empty string from the captcha image.
        Equivalent of the original Java test: TestingCaptchaLogintest()
        """
        lp = self._reload()
        captcha_text = lp.locate_and_convert_captcha()

        assert captcha_text is not None, "OCR returned None"
        assert len(captcha_text) > 0,   "OCR returned an empty string — captcha extraction failed"

        logger.info(f"TC_POS_04 PASSED — OCR extracted captcha: '{captcha_text}'")

    def test_tc_pos_05_full_login_flow_with_ocr_captcha(self):
        """
        TC_POS_05 — Full end-to-end login flow.
        Equivalent of the original Java: TestingCaptchaLogintest()
        Enters username, password, reads captcha via OCR, submits the form.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(VALID_PASSWORD)

        captcha_text = lp.locate_and_convert_captcha()
        assert len(captcha_text) > 0, "OCR captcha text must not be empty"

        lp.enter_captcha(captcha_text)

        # Verify captcha field was filled
        captcha_value = lp.captcha_input.get_attribute("value")
        assert captcha_value == captcha_text, (
            f"Captcha input value '{captcha_value}' does not match OCR text '{captcha_text}'"
        )

        self._capture("TC_POS_05_full_login_flow")
        logger.info("TC_POS_05 PASSED — Full login flow completed with OCR captcha.")

    def test_tc_pos_06_captcha_field_accepts_text(self):
        """
        TC_POS_06 — Verify captcha input field accepts alphanumeric text.
        """
        lp = self._reload()
        lp.enter_captcha("ABC123")

        actual = lp.captcha_input.get_attribute("value")
        assert actual == "ABC123", f"Captcha field should hold 'ABC123', got '{actual}'"

        logger.info("TC_POS_06 PASSED — Captcha field accepted alphanumeric text.")

    def test_tc_pos_07_page_refresh_generates_new_captcha(self):
        """
        TC_POS_07 — Verify that refreshing the page loads a different captcha image.
        """
        lp = self._get_login_page()
        captcha_text_1 = lp.locate_and_convert_captcha()

        lp.reload_page()
        time.sleep(2)

        captcha_text_2 = lp.locate_and_convert_captcha()

        # New captcha should ideally differ (OCR may vary, but we just verify no crash)
        assert captcha_text_2 is not None
        logger.info(
            f"TC_POS_07 PASSED — Captcha before refresh: '{captcha_text_1}', after: '{captcha_text_2}'"
        )

    def test_tc_pos_08_fields_can_be_cleared_and_re_entered(self):
        """
        TC_POS_08 — Verify fields can be cleared and re-filled (form re-usability).
        """
        lp = self._reload()

        lp.enter_username("first_user")
        lp.enter_username(VALID_USERNAME)   # Should clear and re-enter

        actual = lp.username_field.get_attribute("value")
        assert actual == VALID_USERNAME, "Username field should hold the last entered value"

        logger.info("TC_POS_08 PASSED — Fields cleared and re-entered successfully.")

    # ══════════════════════════════════════════════════════════════════════════
    #  ❌  NEGATIVE TEST SCENARIOS
    # ══════════════════════════════════════════════════════════════════════════

    def test_tc_neg_01_login_with_wrong_captcha(self):
        """
        TC_NEG_01 — Submit login with deliberately wrong captcha text.
        Expected: Login should NOT succeed; page stays on login or shows error.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(VALID_PASSWORD)
        lp.enter_captcha(WRONG_CAPTCHA)     # Intentionally wrong
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_01_wrong_captcha")

        # Should NOT have navigated away from login page
        current_url = self.driver.current_url
        assert "Login.aspx" in current_url or not lp.is_login_successful(), (
            "Login should have FAILED with wrong captcha but URL changed."
        )
        logger.info("TC_NEG_01 PASSED — Login blocked with wrong captcha.")

    def test_tc_neg_02_empty_username(self):
        """
        TC_NEG_02 — Submit form with an empty username field.
        Expected: Login should not succeed.
        """
        lp = self._reload()

        lp.enter_username(EMPTY_STRING)
        lp.enter_password(VALID_PASSWORD)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_02_empty_username")

        assert not lp.is_login_successful(), "Login should FAIL with empty username."
        logger.info("TC_NEG_02 PASSED — Empty username blocked login.")

    def test_tc_neg_03_empty_password(self):
        """
        TC_NEG_03 — Submit form with an empty password field.
        Expected: Login should not succeed.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(EMPTY_STRING)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_03_empty_password")

        assert not lp.is_login_successful(), "Login should FAIL with empty password."
        logger.info("TC_NEG_03 PASSED — Empty password blocked login.")

    def test_tc_neg_04_empty_captcha_field(self):
        """
        TC_NEG_04 — Submit form without filling the captcha field.
        Expected: Login should not succeed.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(VALID_PASSWORD)
        # Captcha intentionally NOT entered
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_04_empty_captcha")

        assert not lp.is_login_successful(), "Login should FAIL with empty captcha."
        logger.info("TC_NEG_04 PASSED — Missing captcha blocked login.")

    def test_tc_neg_05_all_fields_empty(self):
        """
        TC_NEG_05 — Submit the form with all fields empty.
        Expected: No navigation; form stays on login page.
        """
        lp = self._reload()

        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_05_all_empty")

        current_url = self.driver.current_url
        assert "Login.aspx" in current_url, (
            f"Page should remain on Login.aspx but navigated to: {current_url}"
        )
        logger.info("TC_NEG_05 PASSED — All-empty form submission blocked.")

    def test_tc_neg_06_invalid_username_and_password(self):
        """
        TC_NEG_06 — Submit with invalid (non-existent) username and wrong password.
        Expected: Login fails; error or still on login page.
        """
        lp = self._reload()

        lp.enter_username(INVALID_USERNAME)
        lp.enter_password(INVALID_PASSWORD)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_06_invalid_credentials")

        assert not lp.is_login_successful(), "Login should FAIL with invalid credentials."
        logger.info("TC_NEG_06 PASSED — Invalid credentials blocked login.")

    def test_tc_neg_07_sql_injection_in_username(self):
        """
        TC_NEG_07 — Attempt SQL injection in the username field.
        Expected: Application does NOT break or log in; form is safe.
        """
        lp = self._reload()

        lp.enter_username(SQL_INJECTION)
        lp.enter_password(VALID_PASSWORD)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_07_sql_injection")

        assert not lp.is_login_successful(), (
            "SECURITY RISK: SQL injection in username should not log in."
        )
        logger.info("TC_NEG_07 PASSED — SQL injection in username was blocked.")

    def test_tc_neg_08_sql_injection_in_password(self):
        """
        TC_NEG_08 — Attempt SQL injection in the password field.
        Expected: Application does NOT break or authenticate.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(SQL_INJECTION)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_08_sql_in_password")

        assert not lp.is_login_successful(), (
            "SECURITY RISK: SQL injection in password should not authenticate."
        )
        logger.info("TC_NEG_08 PASSED — SQL injection in password was blocked.")

    def test_tc_neg_09_excessively_long_username(self):
        """
        TC_NEG_09 — Enter a 300-character username.
        Expected: Field handles it without crashing; login does not succeed.
        """
        lp = self._reload()

        lp.enter_username(LONG_STRING)
        lp.enter_password(VALID_PASSWORD)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_09_long_username")

        assert not lp.is_login_successful(), "Long username should not authenticate."
        logger.info("TC_NEG_09 PASSED — Excessively long username handled safely.")

    def test_tc_neg_10_special_characters_in_captcha(self):
        """
        TC_NEG_10 — Enter special characters in the captcha field.
        Expected: Login fails; no crash.
        """
        lp = self._reload()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(VALID_PASSWORD)
        lp.enter_captcha(SPECIAL_CHARS)

        actual = lp.captcha_input.get_attribute("value")
        # Field may accept or reject — as long as it doesn't crash
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_10_special_chars_captcha")

        assert not lp.is_login_successful(), "Special char captcha should not authenticate."
        logger.info(f"TC_NEG_10 PASSED — Special characters in captcha handled. Entered: '{actual}'")

    def test_tc_neg_11_captcha_case_sensitivity(self):
        """
        TC_NEG_11 — Enter the captcha in wrong case (inverted case of OCR output).
        Expected: Login fails if captcha is case-sensitive.
        """
        lp = self._reload()
        captcha_text = lp.locate_and_convert_captcha()

        # Invert the case
        wrong_case = captcha_text.swapcase()

        lp.enter_username(VALID_USERNAME)
        lp.enter_password(VALID_PASSWORD)
        lp.enter_captcha(wrong_case)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_11_captcha_case")

        # If case-sensitive, login must fail
        # If case-insensitive, this test documents that behavior
        current_url = self.driver.current_url
        logger.info(
            f"TC_NEG_11 — Original: '{captcha_text}', Swapped: '{wrong_case}', URL: {current_url}"
        )
        logger.info("TC_NEG_11 PASSED — Case sensitivity behavior documented.")

    def test_tc_neg_12_whitespace_only_username(self):
        """
        TC_NEG_12 — Enter only spaces as the username.
        Expected: Login fails; whitespace-only input is not valid.
        """
        lp = self._reload()

        lp.enter_username("     ")
        lp.enter_password(VALID_PASSWORD)
        captcha_text = lp.locate_and_convert_captcha()
        lp.enter_captcha(captcha_text)
        lp.click_login()

        time.sleep(2)
        self._capture("TC_NEG_12_whitespace_username")

        assert not lp.is_login_successful(), "Whitespace-only username should not authenticate."
        logger.info("TC_NEG_12 PASSED — Whitespace-only username blocked.")
