import os
import sys
from datetime import date

import scraper
import summarizer
import site_generator
import emailer


def main():
    date_str = date.today().strftime("%Y-%m-%d")
    pages_url = os.environ.get("PAGES_URL", "").rstrip("/")
    if not pages_url:
        print("[main] WARNING: GITHUB_PAGES_URL not set")
        pages_url = "https://example.github.io/ai-voice-digest"

    print(f"=== AI Voice & Agent Digest — {date_str} ===")

    print("\n[step 1] Scraping articles...")
    articles = scraper.scrape_all()
    if not articles:
        print("[main] No articles found, aborting.")
        sys.exit(1)

    print(f"\n[step 2] Summarizing {len(articles)} articles with DeepSeek...")
    relevant, digest = summarizer.process(articles)
    print(f"[main] Relevant articles: {len(relevant)}")
    print(f"[main] Digest preview: {digest[:120]}...")

    print("\n[step 3] Generating site...")
    site_generator.generate(date_str, relevant, digest)

    print("\n[step 4] Sending email...")
    emailer.send(date_str, relevant, digest, pages_url)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
