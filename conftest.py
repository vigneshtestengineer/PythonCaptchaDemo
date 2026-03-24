import pytest
from browser_setup.setup_browser import SetupBrowser


def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser to run tests: chrome or edge"
    )


@pytest.fixture(scope="class")
def driver(request):
    """
    Class-scoped driver fixture.
    Equivalent to Java @BeforeClass / @AfterClass in SetupBrowser.java
    """
    browser_name = request.config.getoption("--browser")
    setup = SetupBrowser(browser=browser_name)
    driver_instance = setup.get_driver()

    # Inject driver into test class
    request.cls.driver = driver_instance

    yield driver_instance

    # Teardown — equivalent to @AfterClass
    driver_instance.quit()
