from scraper.scraper import Scraper


class WalletScraper:
    def __init__(self):
        self.scraper = Scraper()

    async def scrape_address(self, address: str):
        result = self.scraper.check_address(address)
        reply = self._format_reply(address, result)
        print("found wallets:\n" + reply)
        self._write_to_file(address, reply)

    def _format_reply(self, address: str, result: dict) -> str:
        reply = f"_Token:_ [{result['token_symbol']}](https://dexscreener.com/solana/{address})\n\n"

        if result["wallets_list"]:
            reply += "_Valid wallets:_\n"
            for wallet in result["wallets_list"]:
                reply += f"[{wallet['address']}](https://gmgn.ai/sol/address/{wallet['address']}), PnL:{wallet['pnl']}%, winrate:{wallet['winrate']}%\n"
        else:
            reply += "_No valid wallets_\n"

        return reply

    def _write_to_file(self, address: str, content: str):
        with open(f"{address}_wallets.txt", "w") as f:
            f.write(content)