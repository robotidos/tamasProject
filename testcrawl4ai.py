import asyncio
import re
from crawl4ai import AsyncWebCrawler

async def main():
    url = "https://zakanyszerszamhaz.hu/elektromos-holegbefuvok/gude-geh-3000-elektromos-holegbefuvo-230-v-futoteljesitmeny-3000-w-467-mperc-p101602756"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)

        # Reguláris kifejezés a <h1> elem kinyerésére, amely tartalmazza a termék nevét.
        title_pattern = re.compile(
            r'<h1\s+[^>]*class=["\']main-title ml-3["\'][^>]*\s+itemprop=["\']name["\'][^>]*>(.*?)</h1>',
            re.DOTALL | re.IGNORECASE
        )
        title_match = title_pattern.search(result.html)
        if title_match:
            product_title = title_match.group(1).strip()
            print("Termék neve:")
            print(product_title)
        else:
            print("A termék neve nem található.")

        # Reguláris kifejezés a leírás kinyerésére: a <div> elem, melynek class attribútuma "product__long-description mb-2"
        description_pattern = re.compile(
            r'<div\s+[^>]*class=["\']product__long-description mb-2["\'][^>]*>(.*?)</div>',
            re.DOTALL | re.IGNORECASE
        )
        description_match = description_pattern.search(result.html)
        if description_match:
            product_description = description_match.group(1).strip()
            print("\nTermék leírása:")
            print(product_description)
        else:
            print("A termék leírása nem található.")

if __name__ == "__main__":
    asyncio.run(main())
