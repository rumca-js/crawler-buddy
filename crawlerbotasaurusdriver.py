"""
TODO
This is just a starting point.
This should be implemented
"""

from botasaurus_driver import Driver

driver = Driver()
driver.google_get(
    "https://www.g2.com/products/github/reviews.html?page=5&product_id=github",
    bypass_cloudflare=True,
)
driver.prompt()
heading = driver.get_text('.product-head__title [itemprop="name"]')
print(heading)
