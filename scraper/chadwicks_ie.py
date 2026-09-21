"""Chadwicks.ie (EUR, Ireland) — /media/sitemap-1-products-categories.xml
is a MASSIVE category sitemap. Product URLs end .html; ld+json Product with EUR price.
"""
import re
from common import get, sitemap_urls, sane_price, valid_ean, first_str, ldjson_products, offer_from_ld, write_jsonl, scrape_urls

BASE = "https://www.chadwicks.ie"
OUT = "data/latest/chadwicks_ie.jsonl"


def fetch_url_list(limit=None):
    # the sitemap is ~11MB and product URLs are deep category paths
    xml = get(f"{BASE}/media/sitemap-1-products-categories.xml")
    us = [u for u in sitemap_urls(xml) if ".html" in u and u.count("/") >= 4]
    return us[:limit] if limit else us


def handle(u, html):
    rows = []
    for p in ldjson_products(html):
        off = offer_from_ld(p)
        if off:
            off["price"] = sane_price(off["price"])
        if not off or not off["price"]:
            continue
        sku = u.rstrip("/").rsplit("/", 1)[-1].replace(".html", "")
        rows.append({
            "chain": "chadwicks_ie",
            "country": "ie",
            "currency": off["currency"],
            "sku": sku,
            "ean": valid_ean(p.get("gtin13") or p.get("gtin") or p.get("ean")),
            "name": p.get("name"),
            "url": u,
            "price": off["price"],
            "in_stock": off["in_stock"],
            "image": first_str(p.get("image")),
        })
        break
    return rows


def scrape(limit=None):
    return scrape_urls(fetch_url_list(limit), handle)


if __name__ == "__main__":
    import sys
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rows = scrape(lim)
    write_jsonl(OUT, rows)
    print("chadwicks_ie: %d products -> %s" % (len(rows), OUT))
