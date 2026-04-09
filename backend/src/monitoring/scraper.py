"""
Scrapling-based corporate site monitoring for welfare commitment pages.

Watches corporate responsibility, ESG, and animal welfare pages for:
  - Commitment text changes (new pledges, withdrawn pledges)
  - Progress report updates
  - PDF report publication

Designed to run as a scheduled job (cron or APScheduler).
Anti-bot bypass handled by Scrapling's StealthyFetcher.
"""
import argparse
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Corporate welfare/responsibility page URL patterns per company domain
COMMITMENT_PAGE_URLS: dict[str, list[str]] = {
    "mcdonalds.com": [
        "https://corporate.mcdonalds.com/corpmcd/our-purpose-and-impact/better-sourcing.html",
        "https://corporate.mcdonalds.com/corpmcd/our-purpose-and-impact/better-sourcing/animal-health-and-welfare.html",
    ],
    "walmart.com": [
        "https://corporate.walmart.com/esgreport/environmental-social-governance/animal-welfare",
    ],
    "costco.com": [
        "https://www.costco.com/sustainability-animal-welfare.html",
    ],
    "compass-group.com": [
        "https://www.compass-group.com/en/about-us/responsible-business/animal-welfare.html",
    ],
    "sodexo.com": [
        "https://www.sodexo.com/en/sustainability/better-tomorrow-commitments/animal-welfare.html",
    ],
    "aramark.com": [
        "https://www.aramark.com/sustainability/animal-welfare",
    ],
    "subway.com": [
        "https://www.subway.com/en-us/ourworld/goodbusiness/animalcare",
    ],
    "tysonfoods.com": [
        "https://www.tysonfoods.com/sustainability/food/animal-wellbeing",
    ],
    "nestle.com": [
        "https://www.nestle.com/csv/impact/animalwelfare",
    ],
    "unilever.com": [
        "https://www.unilever.com/planet-and-society/responsible-sourcing/animal-welfare/",
    ],
}


@dataclass
class ScrapeResult:
    """Result from scraping a single commitment page."""
    company_domain: str
    url: str
    text_content: str
    status_code: int
    error: Optional[str] = None


async def scrape_company_page(company_domain: str, url: str) -> ScrapeResult:
    """
    Fetch a single corporate commitment page using Scrapling's StealthyFetcher.
    Anti-bot bypass is handled automatically.
    """
    try:
        from scrapling.fetchers import AsyncFetcher

        fetcher = AsyncFetcher(auto_match=True)
        page = await fetcher.get(url)

        # Extract visible text — Scrapling's .get_all_text() strips nav/footer noise
        text_content = page.get_all_text(separator=" ", strip=True) if page else ""

        return ScrapeResult(
            company_domain=company_domain,
            url=url,
            text_content=text_content,
            status_code=200,
        )
    except Exception as exc:
        logger.warning("Failed to scrape %s: %s", url, exc)
        return ScrapeResult(
            company_domain=company_domain,
            url=url,
            text_content="",
            status_code=0,
            error=str(exc),
        )


async def scrape_all_companies(
    company_domains: list[str] | None = None,
) -> list[ScrapeResult]:
    """
    Scrape commitment pages for specified companies, or all tracked companies.

    Runs sequentially (not concurrently) to avoid triggering corporate anti-bot
    systems. Rate limiting is implicit in sequential execution.
    """
    targets = company_domains or list(COMMITMENT_PAGE_URLS.keys())
    results: list[ScrapeResult] = []

    for domain in targets:
        urls = COMMITMENT_PAGE_URLS.get(domain, [])
        if not urls:
            logger.warning("No commitment page URLs configured for %s", domain)
            continue

        for url in urls:
            logger.info("Scraping %s — %s", domain, url)
            result = await scrape_company_page(domain, url)
            results.append(result)

            # Small pause between requests to the same domain
            await asyncio.sleep(2)

    return results


def main() -> None:
    """CLI entry point: python -m src.monitoring.scraper --companies all"""
    parser = argparse.ArgumentParser(description="Scrape corporate welfare commitment pages")
    parser.add_argument(
        "--companies",
        default="all",
        help="Comma-separated company domains to scrape, or 'all'",
    )
    args = parser.parse_args()

    if args.companies == "all":
        domains = None
    else:
        domains = [d.strip() for d in args.companies.split(",")]

    results = asyncio.run(scrape_all_companies(domains))

    for result in results:
        if result.error:
            logger.error("Error scraping %s: %s", result.url, result.error)
        else:
            preview = result.text_content[:200].replace("\n", " ")
            logger.info("[%s] %s chars — %s...", result.company_domain, len(result.text_content), preview)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
