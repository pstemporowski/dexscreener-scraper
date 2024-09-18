
from managers.wallet_manager import WalletScraper


class ScraperManager:
    """
    Manages the scraping of Solana wallet addresses by delegating the scraping to a `WalletScraper` instance.
    
    The `ScraperManager` class is responsible for iterating through the list of wallet addresses and calling the `scrape_address` method on the `WalletScraper` instance for each address. It also handles any exceptions that may occur during the scraping process.
    """
    def __init__(self, addresses):
        self.addresses = addresses
        self.wallet_scraper = WalletScraper()

    async def scrape_all(self):
        """
        Scrapes all the addresses in the `self.addresses` list by calling the `scrape_address` method on the `self.wallet_scraper` instance for each address. If a `KeyboardInterrupt` exception is raised, it will be propagated up the call stack. If any other exception occurs during the scraping process, it will be caught and the error message will be printed to the console.
        """
        for addr in self.addresses:
            try:
                await self.wallet_scraper.scrape_address(addr)
            except KeyboardInterrupt:
                raise KeyboardInterrupt("KeyboardInterrupt")
            except Exception as e:
                print(f"Error with {addr}: {str(e)}")
