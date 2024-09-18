import time
from typing import Dict, List, Any
from seleniumbase.common.exceptions import NoSuchElementException, NotConnectedException
from lxml import html
from seleniumbase import SB

class Scraper:
    def __init__(self):
        """
        Initialize the Scraper with a maximum number of attempts.
        """
        self.max_attempts = 6

    def check_address(self, address: str) -> Dict[str, List[Any]]:
        """
        Check the given address and return token symbol and wallets list.

        Args:
            address (str): The address to check.

        Returns:
            Dict[str, List[Any]]: A dictionary containing the token symbol and wallets list.
        """
        wallets_list = []

        with SB(uc=True, headless=True) as driver:
            print("Opening chrome driver...")

            for attempt in range(self.max_attempts):
                try:
                    token_symbol = self._process_dexscreener(driver, address)
                    wallets_list = self._process_wallets(driver)
                    return {"token_symbol": token_symbol, "wallets_list": wallets_list}
                except KeyboardInterrupt:
                    raise KeyboardInterrupt("KeyboardInterrupt")
                except NotConnectedException:
                    self._handle_not_connected_exception(attempt)
                except IndexError:
                    self._handle_index_error(address)
                except NoSuchElementException:
                    self._handle_no_such_element_exception(attempt)
                except:
                    print(f"Attempt: {attempt + 1} | Error: Unknown error")

        print("Driver closed")
        return {"token_symbol": "--", "wallets_list": []}

    def _process_dexscreener(self, driver, address: str) -> str:
        """
        Process the dexscreener website for the given address.

        Args:
            driver: The Selenium driver.
            address (str): The address to process.

        Returns:
            str: The token symbol.
        """
        driver.uc_open_with_reconnect("https://dexscreener.com/solana/" + address, 6)
        time.sleep(5)
        print("opened site")

        self._handle_cloudflare(driver)
        return self._get_token_symbol(driver)

    def _handle_cloudflare(self, driver):
        """
        Handle Cloudflare protection.

        Args:
            driver: The Selenium driver.

        Raises:
            NotConnectedException: If Cloudflare protection is not passed.
        """
        if driver.get_title() == "Just a moment...":
            raise NotConnectedException
        print("Passed CloudFlare")
        time.sleep(2)

    def _get_token_symbol(self, driver) -> str:
        """
        Get the token symbol from the page.

        Args:
            driver: The Selenium driver.

        Returns:
            str: The token symbol.
        """
        try:
            tree_xml = html.fromstring(driver.get_page_source())
            token_symbol = tree_xml.xpath("//*[@id='root']/div/main/div/div/div[1]/div/div[1]/div[1]/div/div[1]/h2/span[1]/span")[0].text_content().strip()
            if not token_symbol.startswith("$"):
                token_symbol = "$" + token_symbol
            return token_symbol
        except:
            print("No token symbol found")
            return "--"

    def _process_wallets(self, driver) -> List[Dict[str, Any]]:
        """
        Process wallets information from the page.

        Args:
            driver: The Selenium driver.

        Returns:
            List[Dict[str, Any]]: A list of wallet information.
        """
        wallets_list = []
        driver.click("//*[@id='root']/div/main/div/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/button[2]")
        time.sleep(2)
        tree_xml = html.fromstring(driver.get_page_source())
        elements = tree_xml.xpath("//*[@id='root']/div/main/div/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/div[2]")[0]

        for child in elements:
            wallet_info = self._process_wallet(driver, child)
            if wallet_info:
                wallets_list.append(wallet_info)

        return wallets_list

    def _process_wallet(self, driver, child) -> Dict[str, Any]:
        """
        Process individual wallet information.

        Args:
            driver: The Selenium driver.
            child: The HTML element containing wallet information.

        Returns:
            Dict[str, Any]: Wallet information including address, PNL, and win rate.
        """
        price = self._get_price(child)
        if not price or price > 3000:
            return None

        wallet = self._get_wallet_address(child)
        if not wallet:
            return None

        driver.uc_open_with_reconnect("https://gmgn.ai/sol/address/" + wallet, 20)
        time.sleep(1)

        self._handle_modals(driver)
        self._select_30_day_stats(driver)

        pnl, winrate = self._get_wallet_stats(driver)
        wallet_pnl = float(pnl.rstrip("%"))
        wallet_winrate = float(winrate.rstrip("%")) if winrate != "--%" else winrate.rstrip("%")

        if wallet_pnl > 100 or (wallet_winrate != "--" and wallet_winrate == 100):
            return {
                "address": wallet,
                "pnl": wallet_pnl,
                "winrate": wallet_winrate,
            }
        return None

    def _get_price(self, child) -> float:
        """
        Get the price from the wallet element.

        Args:
            child: The HTML element containing price information.

        Returns:
            float: The price value.
        """
        price_element = child[2].find(".//span")
        if price_element is None:
            return None
        price_value = price_element.text_content()
        if price_value[-1] in ["K", "M"] or price_value == "-":
            return None
        try:
            return float(price_value.replace("$", "").replace(",", ""))
        except:
            print("Unexpected error")
            return None

    def _get_wallet_address(self, child) -> str:
        """
        Get the wallet address from the wallet element.

        Args:
            child: The HTML element containing wallet address information.

        Returns:
            str: The wallet address.
        """
        link_element = child[-1].find(".//a")
        if link_element is None:
            return None
        href_value = link_element.attrib.get("href")
        return href_value.rsplit("/", 1)[-1]

    def _handle_modals(self, driver):
        """
        Handle modal windows on the page.

        Args:
            driver: The Selenium driver.
        """
        self._handle_modal(driver, "//*[@id='chakra-modal--body-:r13:']/div/button")
        self._handle_modal(driver, "//*[@id='chakra-modal-:ri:']/button")

    def _handle_modal(self, driver, xpath):
        """
        Handle a specific modal window.

        Args:
            driver: The Selenium driver.
            xpath (str): The XPath of the modal element.
        """
        try:
            tree_xml = html.fromstring(driver.get_page_source())
            if len(tree_xml.xpath(xpath)) > 0:
                driver.click(xpath)
        except:
            pass

    def _select_30_day_stats(self, driver):
        """
        Select 30-day statistics on the page.

        Args:
            driver: The Selenium driver.
        """
        driver.click("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[1]/div/div[2]")
        time.sleep(1)

    def _get_wallet_stats(self, driver) -> tuple:
        """
        Get wallet statistics from the page.

        Args:
            driver: The Selenium driver.

        Returns:
            tuple: A tuple containing PNL and win rate.
        """
        pnl = driver.get_text("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]")
        winrate = driver.get_text("//*[@id='__next']/div/div/main/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]")
        return pnl, winrate

    def _handle_not_connected_exception(self, attempt):
        """
        Handle NotConnectedException.

        Args:
            attempt (int): The current attempt number.

        Raises:
            NotConnectedException: If maximum attempts are reached.
        """
        print(f"Attempt: {attempt + 1} | Error: Antibot not passed")
        if attempt < self.max_attempts - 1:
            print("Starting next attempt...")
        else:
            print("Driver closed")
            raise NotConnectedException("Antibot not passed\nContact the admin to resolve this")

    def _handle_index_error(self, address):
        """
        Handle IndexError.

        Args:
            address (str): The address that caused the error.

        Raises:
            IndexError: With the address that caused the error.
        """
        print(f"Error: No such address: {address}")
        print("Driver closed")
        raise IndexError(f"No such address: {address}")

    def _handle_no_such_element_exception(self, attempt):
        """
        Handle NoSuchElementException.

        Args:
            attempt (int): The current attempt number.

        Raises:
            NoSuchElementException: If maximum attempts are reached.
        """
        print(f"Attempt: {attempt + 1} | Error: No such element")
        if attempt < self.max_attempts - 1:
            print("Starting next attempt...")
        else:
            print("Driver closed")
            raise NoSuchElementException("No such element\nContact the admin to resolve this")
