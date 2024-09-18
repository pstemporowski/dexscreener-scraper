import asyncio
from managers.scrape_manager import ScraperManager

"""
A list of Solana wallet addresses to scrape.
"""
ADDRESSES = []



async def main():
    scraper_manager = ScraperManager(ADDRESSES)
    await scraper_manager.scrape_all()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is off")
