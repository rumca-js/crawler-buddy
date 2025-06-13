import asyncio

puppeteer_feature_enabled = True
try:
    from pyppeteer import launch
except Exception as E:
    print(str(E))
    puppeteer_feature_enabled = False

import crawlerscript
from src import webtools


async def main() -> None:
    parser = crawlerscript.Parser()
    parser.parse()
    if not parser.is_valid():
        return

    if not puppeteer_feature_enabled:
        print("Python: puppeteer package is not available")
        return

    request = parser.get_request()
    print("Running request:{}".format(request))

    browser = await launch()
    page = await browser.newPage()

    this_response = webtools.PageResponseObject(request.url, request_url=request.url)

    # Define a callback to handle responses
    async def intercept_response(response):
        this_response.url = response.url
        this_response.status_code = response.status
        this_response.headers = response.headers

    # Attach the callback to the response event
    page.on("response", intercept_response)

    await page.goto(parser.args.url)

    content = await page.evaluate("document.body.textContent", force_expr=True)

    await browser.close()

    c = crawlerscript.ScriptCrawlerInterface(parser, None, __file__)
    c.response = this_response
    c.save_response()


asyncio.get_event_loop().run_until_complete(main())
