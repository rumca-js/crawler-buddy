from datetime import datetime, timedelta
import json

from src.webtools import (
    Url,
    PageOptions,
    HtmlPage,
    PageResponseObject,
    HttpPageHandler,
)
from utils import CrawlHistory

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


example_requests_properties = """
[
  {
    "data": {
      "album": null,
      "author": null,
      "date_published": "Fri, 17 Jan 2025 19:59:54 GMT",
      "description": "Le Monde.fr - ",
      "language": "en",
      "link": "https://www.lemonde.fr/en/rss/une.xml",
      "page_rating": 86,
      "tags": null,
      "thumbnail": null,
      "title": "Le Monde.fr - Actualitet Infos en France et dans le monde"
    },
    "name": "Properties"
  },
  {
    "data": {
      "Contents": "test"
    },
    "name": "Text"
  },
  {
    "data": {
      "bytes_limit": 5000000,
      "crawler": "RequestsCrawler",
      "enabled": true,
      "name": "RequestsCrawler",
      "settings": {
        "remote-server": "http://127.0.0.1:3000",
        "timeout_s": 20
      }
    },
    "name": "Settings"
  },
  {
    "data": {
      "Charset": "UTF-8",
      "Content-Length": 21705,
      "Content-Type": "application/xml; charset=UTF-8",
      "body_hash": "s6n8SxxMt8pDWEN/clZS1w==",
      "crawler_data": {
        "crawler": "RequestsCrawler",
        "name": "RequestsCrawler",
        "settings": {
          "crawler": "RequestsCrawler",
          "full": null,
          "headers": false,
          "name": "RequestsCrawler",
          "ping": false,
          "remote-server": "http://192.168.0.200:3000",
          "remote_server": "http://192.168.0.200:3000",
          "timeout": 10,
          "timeout_s": 20
        }
      },
      "hash": "s6n8SxxMt8pDWEN/clZS1w==",
      "is_valid": true,
      "status_code": 200
    },
    "name": "Response"
  },
  {
    "data": {
      "Accept-Ranges": "bytes",
      "Age": "123",
      "Charset": "UTF-8",
      "Connection": "keep-alive",
      "Content-Length": 21705,
      "Content-Type": "application/xml; charset=UTF-8",
      "Date": "Fri, 17 Jan 2025 20:01:57 GMT",
      "Set-Cookie": "lmd_a_c=0; Path=/; Domain=.lemonde.fr; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
      "Strict-Transport-Security": "max-age=31557600",
      "Vary": "Accept-Encoding, X-device",
      "X-Cache": "MISS, HIT",
      "X-Cache-Hits": "0, 1",
      "X-Served-By": "cache-fra-eddf8230050-FRA, cache-fra-eddf8230112-FRA",
      "X-Timer": "S1737144118.952411,VS0,VE7",
      "cache-control": "public, max-age=300",
      "content-security-policy": "default-src data: 'unsafe-inline' 'unsafe-eval' https:; script-src data: 'unsafe-inline' 'unsafe-eval' https: blob:; style-src data: 'unsafe-inline' https:; img-src data: https: blob:; font-src data: https:; connect-src https: wss:; media-src https: blob: data:; object-src https:; child-src https: data: blob:; form-action https:; block-all-mixed-content;",
      "content-type": "application/xml; charset=UTF-8",
      "expires": "Fri, 17 Jan 2025 20:04:54 GMT",
      "last-modified": "Fri, 17 Jan 2025 19:59:54 GMT",
      "via": "1.1 varnish, 1.1 varnish",
      "x-content-type-options": "nosniff",
      "x-frame-options": "SAMEORIGIN",
      "x-xss-protection": "1; mode=block"
    },
    "name": "Headers"
  },
  {
    "data": [
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 16:52:49 GMT",
        "description": "With TikTok in danger of being banned in the US, many Americans have decided to migrate to an equivalent Chinese app, provoking some interesting conversations between young people on both sides of the Pacific.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/pixels/article/2025/01/17/the-astonishing-migration-of-american-tiktok-refugees-to-a-chinese-app-they-knew-nothing-about_6737147_13.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/15/428/0/5132/2566/644/322/60/0/3f4f960_sirius-fs-upload-1-tnu7wbrn3y3x-1736960848051-776927.jpg",
        "title": "These American TikTok 'refugees' joined a Chinese app they knew nothing about"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 07:29:04 GMT",
        "description": "Israel cabinet has recommended approving a deal that would pause the fighting in Gaza and release dozens of hostages held by militants.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/international/article/2025/01/17/netanyahu-s-office-says-cabinet-to-meet-on-friday-over-ceasefire-after-hostage-deal-finalized_6737123_4.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/17/343/0/4124/2062/644/322/60/0/f270c12_ftp-import-images-1-1yfdfpnujg4b-a5ea18cccf944a81974484744a4b5e50-0-8038b0f7d87b4569a8b38457a1e7deab.jpg",
        "title": "Israel's security cabinet approves Gaza ceasefire deal"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 20:00:08 GMT",
        "description": "'Wine is great for the heart, abstinence is useless, it's a youth problem...' Incorrect ideas about alcohol are hard to overcome despite scientific findings.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/les-decodeurs/article/2025/01/17/dry-january-five-common-misconceptions-about-alcohol-consumption_6737150_8.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/14/905/0/5426/2713/644/322/60/0/d8a8210_sirius-fs-upload-1-shpbn3zpv0p7-1736861412951-000-33un3aw.jpg",
        "title": "Dry January: Five common misconceptions about alcohol consumption"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 20:01:58 GMT",
        "description": "With every legislative change related to abortion, the clause stipulating that no healthcare provider 'is obliged to perform a voluntary termination of pregnancy' is questioned.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/france/article/2025/01/17/abortion-has-been-legal-in-france-for-50-years-yet-a-clause-allowing-doctors-to-decline-to-perform-the-procedure-raises-questions_6737153_7.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/394/0/5548/2774/644/322/60/0/95dcd36_sirius-fs-upload-1-gg0eeprv53kg-1737050390023-000-347t67g.jpg",
        "title": "Abortion has been legal in France for 50 years. Yet a clause allowing doctors to decline to perform the procedure raises questions"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 20:01:58 GMT",
        "description": "The leaders of the Rassemblement National, who had feared a potential 're-demonization' of the party following the death of its co-founder, praised his career, encouraged by measured media coverage and political reactions.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/opinion/article/2025/01/17/far-right-restores-jean-marie-le-pen-s-image-without-causing-a-stir_6737151_23.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/106/0/3360/1680/644/322/60/0/88773bd_ftp-import-images-1-cp9gtaznrknq-5753582-01-06.jpg",
        "title": "Far right restores Jean-Marie Le Pen's image without causing a stir"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 16:37:24 GMT",
        "description": "The filmmaker, who died on January 16, pushed the limits of what television could produce with a long-running whodunnit to find out who killed small-town high schooler Laura Palmer.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/culture/article/2025/01/17/david-lynch-and-the-twin-peaks-television-revolution_6737146_30.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/20/0/1280/640/644/322/60/0/3d3ed1f_sirius-fs-upload-1-6geag5fqtcus-1737056807479-twinpeaks-credit-abc.jpeg",
        "title": "David Lynch and the 'Twin Peaks' television revolution"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 11:34:10 GMT",
        "description": "Lebanon has just elected a president and appointed a prime minister, after months of deadlock. The French president didn't hesitate to visit, sensing an opportunity to take stock of the ceasefire signed at the end of November between Israel and Hezbollah.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/international/article/2025/01/17/macron-visits-lebanon-where-ceasefire-is-taking-hold_6737134_4.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/17/340/0/1600/800/644/322/60/0/30dc9fe_sirius-fs-upload-1-8d2vm3tn6r4t-1737109817100-whatsapp-image-2025-01-17-at-09-52-31-2.jpeg",
        "title": "Macron visits Lebanon, where ceasefire is taking hold"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 15:34:41 GMT",
        "description": "Eric Zemmour and MEP Sarah Knafo of Reconqu\u00eate! will be at the Capitol on January 20, a hard-won invitation. They will share the podium with the cr\u00e8me de la cr\u00e8me of the world's nationalist reactionaries.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/m-le-mag/article/2025/01/17/how-eric-zemmour-s-small-far-right-party-snagged-seats-to-trump-s-inauguration-over-the-more-powerful-rassemblement-national_6737143_117.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/14/125/0/1500/750/644/322/60/0/a2cd9ab_ftp-import-images-1-qqdknbqsaixq-365348-3405620.jpg",
        "title": "How Eric Zemmour's small far-right party snagged seats to Trump's inauguration over the more powerful Rassemblement National"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 14:00:06 GMT",
        "description": "Intentionally terminating a pregnancy within the first few months of a relationship is not part of the classic pattern of a couple's life. It can leave after-effects and unfulfilled dreams, but it can also be the cement that holds a relationship together.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/intimacy/article/2025/01/17/couples-describe-having-abortions-at-the-start-of-a-relationship-it-sealed-a-pact-between-us_6737140_310.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/14/149/0/1913/956/644/322/60/0/49d5ec5_sirius-fs-upload-1-tkngagw6h2g0-1736874348706-lemondeintimites-heleneblanc-fondnoir2-1.jpg",
        "title": "Couples describe having abortions at the start of a relationship: 'It sealed a pact between us'"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 20:01:58 GMT",
        "description": "Daniel Chapo was sworn in Wednesday in a heavily guarded ceremony, extending his Frelimo party's 50-year rule of the gas-rich African nation after the contested election sparked weeks of violent demonstrations.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/international/article/2025/01/17/mozambique-s-new-president-appoints-pm-senior-ministers_6737152_4.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/372/0/4608/2304/644/322/60/0/83e1edc_ftp-import-images-1-uyrzmdhx0s6v-2025-01-16t120752z-808137309-rc2xacax93hf-rtrmadp-3-mozambique-politics.JPG",
        "title": "Mozambique's new president appoints PM, senior ministers"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 11:13:05 GMT",
        "description": "On Thursday, Parti Socialiste MPs decided to vote against the motion of no confidence submitted by their radical-left allies and supported by the Greens and the Communists. Socialist leader Olivier Faure nonetheless pledged to embody 'a left that makes the government yield.'",
        "language": "en",
        "link": "https://www.lemonde.fr/en/politics/article/2025/01/17/how-pm-bayrou-managed-to-detach-the-socialists-from-the-left-wing-coalition_6737133_5.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/437/0/4620/2310/644/322/60/0/d018cef_sirius-fs-upload-1-0uideis9m0vw-1737043133075-304895.jpg",
        "title": "How PM Bayrou managed to detach the Socialists from the left-wing coalition"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 18:46:37 GMT",
        "description": "They were sentenced for bringing messages from the late opposition leader from prison to the outside world.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/international/article/2025/01/17/russia-sentences-navalny-lawyers-to-years-behind-bars_6737149_4.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/17/282/0/4378/2189/644/322/60/0/a498344_ftp-import-images-1-fqwoadnlngvh-5763928-01-06.jpg",
        "title": "Russia sentences Navalny lawyers to years behind bars"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 18:24:55 GMT",
        "description": "The French president made the announcement as he visited Beirut in a show of support for Lebanon's new leaders.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/international/article/2025/01/17/macron-announces-aid-conference-to-rebuild-lebanon_6737148_4.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/17/0/0/2805/1402/644/322/60/0/d01a754_ftp-import-images-1-qjn0fan7clid-5764472-01-06.jpg",
        "title": "Macron announces aid conference to rebuild Lebanon"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 09:00:11 GMT",
        "description": "The investigation into 'forever chemicals' carried out by Le Monde and its partners reveals a lack of traceability in the exchanges between public authorities and PFAS manufacturers and users.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/les-decodeurs/article/2025/01/17/lobbying-campaign-against-pfas-ban-highlights-opacity-of-european-decision-making_6737126_8.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/10/250/0/3000/1500/644/322/60/0/27aba54_sirius-fs-upload-1-utuvjwfho5tx-1736532072744-7-transparence-malmenei-e.jpg",
        "title": "Lobbying campaign against PFAS ban highlights opacity of European decision-making"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 12:20:26 GMT",
        "description": "France has rebounded stronger than most other countries in terms of cinema audience figures, but is still not back to pre-Covid levels.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/france/article/2025/01/17/france-s-cinemas-lead-the-way-in-post-covid-recovery_6737137_7.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2022/09/16/295/0/3780/1890/644/322/60/0/95b730e_1663331782462-ftgfrtcf.jpg",
        "title": "France's cinemas lead the way in post-Covid recovery"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 12:32:12 GMT",
        "description": "Olaf Scholz's comments come after the tech billionaire has been voicing his support on X for the far-right Alternative for Germany party.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/germany/article/2025/01/17/musk-backing-for-european-far-right-threatens-democracy-says-scholz_6737138_146.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/477/0/6092/3046/644/322/60/0/cc25eb5_ftp-import-images-1-e1vhdluj51yw-a60853f80a2143338d55f15f8675ce48-0-1b524c810cdc49248e7e8aebccc54ec2.jpg",
        "title": "Musk backing for European far-right 'threatens democracy', says German Chancellor Scholz"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 05:06:02 GMT",
        "description": "President Bassirou Diomaye Faye called for certain main roads bearing colonial names to be renamed in honor of 'national heroes.'",
        "language": "en",
        "link": "https://www.lemonde.fr/en/le-monde-africa/article/2025/01/17/in-senegal-the-authorities-want-to-do-away-with-french-street-names_6737122_124.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/16/27/0/2400/1200/644/322/60/0/a5189fc_sirius-fs-upload-1-y4eyhz6zrat3-1737039568040-000-36u99u3.jpg",
        "title": "Senegalese authorities want to do away with French street names"
      },
      {
        "album": "",
        "author": null,
        "bookmarked": false,
        "date_published": "Fri, 17 Jan 2025 08:10:40 GMT",
        "description": "From his Haitian roots to his travels around the world, the 61-year-old artist has never stopped putting his intimate quest for a metaphorical insularity into images. His world, currently on display in Perth, Australia, is accompanied by a beautiful book featuring a selection of shots.",
        "language": "en",
        "link": "https://www.lemonde.fr/en/m-le-mag/article/2025/01/17/the-mysterious-island-of-photographer-henry-roy_6737124_117.html",
        "page_rating": 86,
        "source": "https://www.lemonde.fr/en/rss/une.xml",
        "tags": null,
        "thumbnail": "https://img.lemde.fr/2025/01/02/240/0/1500/750/644/322/60/0/d24d40f_363678-3404221.jpg",
        "title": "The mysterious island of photographer Henry Roy"
      }
    ],
    "name": "Entries"
  }
]
"""

example_selenium_properties = example_requests_properties.replace("RequestsCrawler", "SeleniumChromeFull")
example_selenium_properties = example_selenium_properties.replace(""""status_code": 200""", """"status_code": 403""")


class ScriptServerTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_read_properties_section(self):
        all_properties = json.loads(example_requests_properties)

        # call tested function
        data = CrawlHistory.read_properties_section("Text", all_properties)

        self.assertTrue(data)

    def test_find_response__by_url(self):
        all_properties = json.loads(example_requests_properties)

        url_history = CrawlHistory()
        url_history.add((datetime.now(), "https://www.lemonde.fr/en/rss/une.xml", all_properties))

        # call tested function
        data = url_history.find("https://www.lemonde.fr/en/rss/une.xml")

        self.assertTrue(data)

    def test_find_response__by_url(self):
        all_properties = json.loads(example_requests_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_properties))

        # call tested function
        data = url_history.find(url = "https://www.lemonde.fr/en/rss/une.xml")

        self.assertTrue(data)

    def test_find_response__by_name_found(self):
        all_requests_properties = json.loads(example_requests_properties)
        all_selenium_properties = json.loads(example_selenium_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_requests_properties))
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_selenium_properties))

        # call tested function
        data = url_history.find(url = "https://www.lemonde.fr/en/rss/une.xml", crawler_name = "RequestsCrawler")
        self.assertTrue(data)
        items = data[2]
        self.assertEqual(items[3]["data"]["status_code"], 200)

        # call tested function
        data = url_history.find(url = "https://www.lemonde.fr/en/rss/une.xml", crawler_name = "SeleniumChromeFull")
        self.assertTrue(data)
        items = data[2]
        self.assertEqual(items[3]["data"]["status_code"], 403)

    def test_find_response__by_index_found(self):
        all_properties = json.loads(example_requests_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_properties))

        # call tested function
        data = url_history.find(index = 0)

        self.assertTrue(data)

    def test_find_response__by_name_not_found(self):
        all_properties = json.loads(example_requests_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_properties))

        # call tested function
        data = url_history.find(url = "https://www.lemonde.fr/en/rss/une.xml", crawler_name = "Selenium")

        self.assertFalse(data)

    def test_find_response__not_found__date_old(self):
        all_properties = json.loads(example_requests_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_properties))

        url_history.container[0][0] = datetime.now() - timedelta(minutes=11)

        # call tested function
        data = url_history.find(url = "https://www.lemonde.fr/en/rss/une.xml", crawler_name = "RequestsCrawler")

        self.assertFalse(data)

    def test_remove(self):
        all_requests_properties = json.loads(example_requests_properties)
        all_selenium_properties = json.loads(example_selenium_properties)

        url_history = CrawlHistory()
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_requests_properties))
        url_history.add(("https://www.lemonde.fr/en/rss/une.xml", all_selenium_properties))

        # call tested function
        status = url_history.remove(index = 0)

        self.assertTrue(status)
        self.assertEqual(url_history.get_history_size(), 1)

        # call tested function
        status = url_history.remove(index = 1)

        self.assertTrue(status)
        self.assertEqual(url_history.get_history_size(), 0)

        # call tested function
        status = url_history.remove(index = 2)

        self.assertFalse(status)
