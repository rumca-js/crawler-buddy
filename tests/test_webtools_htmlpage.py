from src.webtools import HtmlPage, calculate_hash

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter

webpage_no_lang = """<html>
    <body>
    </body>
</html>
"""

webpage_lang_not_default = """<html lang="it">
    <body>
    </body>
</html>
"""

webpage_no_title = """<html>
    <body>
    </body>
</html>
"""

webpage_title_lower = """<html>
 <title>This is a lower case title</title>
    <body>
    </body>
</html>
"""

webpage_title_upper = """<html>
 <TITLE>This is a upper case title</TITLE>
    <body>
    </body>
</html>
"""

webpage_title_head = """<html>
 <title>selected title</title>
    <body>
    </body>
</html>
"""

webpage_title_meta = """<html>
 <meta name="title" content="selected meta title" />
    <body>
    </body>
</html>
"""

webpage_title_meta_og = """<html>
 <TITLE>selected meta title</TITLE>
 <meta property="og:title" content="selected og:title" />
    <body>
    </body>
</html>
"""

webpage_description_head = """<html>
 <description>selected description</description>
    <body>
    </body>
</html>
"""

webpage_description_meta = """<html>
 <meta name="description" content="selected meta description"/>
    <body>
    </body>
</html>
"""

webpage_description_meta_og = """<html>
 <description>selected meta description</description>
 <meta property="og:description" content="selected og:description" />
    <body>
    </body>
</html>
"""

webpage_meta_article_date = """<html>
 <description>selected meta description</description>
 <meta property="og:description" content="selected og:description" />
 <meta property="article:published_time" content="2024-01-09T21:26:00Z" />
    <body>
    </body>
</html>
"""

webpage_meta_music_release_date = """<html>
 <description>selected meta description</description>
 <meta property="og:description" content="selected og:description" />
 <meta name="music:release_date" content="2024-01-09T21:26:00Z"/>
    <body>
    </body>
</html>
"""

webpage_meta_youtube_publish_date = """<html>
 <description>selected meta description</description>
 <meta property="og:description" content="selected og:description" />
 <meta itemprop="datePublished" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="uploadDate" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="genre" content="Science &amp; Technology">
    <body>
    </body>
</html>
"""


webpage_links = """<html>
 <TITLE>This is a upper case title</TITLE>
    <body>
 <a custom-peroperty="custom-property-value" href="http://otherpage1.net" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="https://otherpage2.net" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test1" class="contentLink  hero--img -first">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test2.html" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test3.htm" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test4.js" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="/test/test5/" class="class">
   <picture></picture>
   </a>
 <a custom-peroperty="custom-property-value" href="//test6.domain.com/" class="class">
   <picture></picture>
   </a>
    </body>
</html>
"""

webpage_rss_links = """<html>
 <head>
 <TITLE>This is a upper case title</TITLE>
 <link rel="alternate" type="application/rss+xml" title="9to5Google &raquo; Feed" href="http://your-site.com/your-feed1.rss" />
 <link rel="alternate" type="application/rss+xml" title="9to5Google &raquo; Feed" href="http://your-site.com/your-feed2.rss" />
 <link rel="alternate" type="application/rss+xml" title="9to5Google &raquo; Feed" href="http://your-site.com/your-feed3.rss" />

 </head>
 <body>
 page body
 </body>
"""

webpage_html_favicon = """<html>
 <head>
 <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
 <title>YouTube</title>

 </head>
 <body>
 page body
 </body>
"""

webpage_html_encoded_links = """<html>
 <head>
 <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
 <title>YouTube</title>

 </head>
 <body>
     <a href="https:&#x2F;&#x2F;github.com&#x2F;pyFFTW&#x2F;pyFFTW">https:&#x2F;&#x2F;github.com&#x2F;pyFFTW&#x2F;pyFFTW</a>
     <a href="http:&#x2F;&#x2F;github-help-wanted.com" rel="nofollow">http:&#x2F;&#x2F;github-help-wanted.com</a>
 </body>
"""

webpage_html_meta_charset = """<html>
 <head>
   <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
   <title>YouTube</title>
   <meta charset="shift_jis" />
 </head>
 <body>
     test
 </body>
"""
webpage_html_meta_http_equiv_charset = """<html>
 <head>
   <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
   <title>YouTube</title>
   <meta http-equiv="Content-Type" content = "text/html; charset=shift_jis" />
 </head>
 <body>
     test
 </body>
"""

webpage_html_schema_fields = """
 <head>
<link itemprop="url" href="https://www.youtube.com/watch?v=111"><meta itemprop="name" content="itemprop name"><meta itemprop="description" content="itemprop description"><meta itemprop="requiresSubscription" content="False"><meta itemprop="identifier" content="i4i-79_9Nvw"><meta itemprop="duration" content="PT11M29S"><span itemprop="author" itemscope itemtype="http://schema.org/Person"><link itemprop="url" href="http://www.youtube.com/@TheFridayCheckout"><link itemprop="name" content="The Friday Checkout"></span><script type="application/ld+json" nonce="NhrRFHqHh-kzADLX-U48Fw">{"@context": "http://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "item": {"@id": "http:\/\/www.youtube.com\/@TheFridayCheckout", "name": "The Friday Checkout"}}]}</script><link itemprop="thumbnailUrl" href="https://thumbnailurl.com"><span itemprop="thumbnail" itemscope itemtype="http://schema.org/ImageObject"><link itemprop="url" href="https://i.ytimg.com/vi/i4i-79_9Nvw/maxresdefault.jpg"><meta itemprop="width" content="1280"><meta itemprop="height" content="720"></span><link itemprop="embedUrl" href="https://www.youtube.com/embed/i4i-79_9Nvw"><meta itemprop="playerType" content="HTML5 Flash"><meta itemprop="width" content="1280"><meta itemprop="height" content="720"><meta itemprop="isFamilyFriendly" content="true"><meta itemprop="regionsAllowed" content="AD,AE,AF,AG,AI,AL,AM,AO,AQ,AR,AS,AT,AU,AW,AX,AZ,BA,BB,BD,BE,BF,BG,BH,BI,BJ,BL,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CU,CV,CW,CX,CY,CZ,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GG,GH,GI,GL,GM,GN,GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IM,IN,IO,IQ,IR,IS,IT,JE,JM,JO,JP,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LT,LU,LV,LY,MA,MC,MD,ME,MF,MG,MH,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,PL,PM,PN,PR,PS,PT,PW,PY,QA,RE,RO,RS,RU,RW,SA,SB,SC,SD,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,SS,ST,SV,SX,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,WF,WS,YE,YT,ZA,ZM,ZW"><meta itemprop="interactionCount" content="2032"><meta itemprop="datePublished" content="2024-05-10T09:04:54-07:00"><meta itemprop="uploadDate" content="2024-05-10T09:04:54-07:00"><meta itemprop="genre" content="Science &amp; Technology">
 </head>
 <body>
     test
 </body>
"""

webpage_html_schema_fields_nested = """
 <head>
<div id="watch7-content" class="watch-main-col" itemscope itemid="" itemtype="http://schema.org/VideoObject"><link itemprop="url" href="https://www.youtube.com/watch?v=111"><meta itemprop="name" content="itemprop name"><meta itemprop="description" content="itemprop description"><meta itemprop="requiresSubscription" content="False"><meta itemprop="identifier" content="i4i-79_9Nvw"><meta itemprop="duration" content="PT11M29S"><span itemprop="author" itemscope itemtype="http://schema.org/Person"><link itemprop="url" href="http://www.youtube.com/@someotherchannel"><link itemprop="name" content="The Friday Checkout"></span><script type="application/ld+json" nonce="NhrRFHqHh-kzADLX-U48Fw">{"@context": "http://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "item": {"@id": "http:\/\/www.youtube.com\/@TheFridayCheckout", "name": "The Friday Checkout"}}]}</script><link itemprop="thumbnailUrl" href="https://i.ytimg.com/vi/i4i-79_9Nvw/maxresdefault.jpg"><span itemprop="thumbnail" itemscope itemtype="http://schema.org/ImageObject"><link itemprop="url" href="https://i.ytimg.com/vi/i4i-79_9Nvw/maxresdefault.jpg"><meta itemprop="width" content="1280"><meta itemprop="height" content="720"></span><link itemprop="embedUrl" href="https://www.youtube.com/embed/i4i-79_9Nvw"><meta itemprop="playerType" content="HTML5 Flash"><meta itemprop="width" content="1280"><meta itemprop="height" content="720"><meta itemprop="isFamilyFriendly" content="true"><meta itemprop="regionsAllowed" content="AD,AE,AF,AG,AI,AL,AM,AO,AQ,AR,AS,AT,AU,AW,AX,AZ,BA,BB,BD,BE,BF,BG,BH,BI,BJ,BL,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CU,CV,CW,CX,CY,CZ,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GG,GH,GI,GL,GM,GN,GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IM,IN,IO,IQ,IR,IS,IT,JE,JM,JO,JP,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LT,LU,LV,LY,MA,MC,MD,ME,MF,MG,MH,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,PL,PM,PN,PR,PS,PT,PW,PY,QA,RE,RO,RS,RU,RW,SA,SB,SC,SD,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,SS,ST,SV,SX,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,WF,WS,YE,YT,ZA,ZM,ZW"><meta itemprop="interactionCount" content="2032"><meta itemprop="datePublished" content="2024-05-10T09:04:54-07:00"><meta itemprop="uploadDate" content="2024-05-10T09:04:54-07:00"><meta itemprop="genre" content="Science &amp; Technology"></div>
 </head>
 <body>
     test
 </body>
"""

webpage_progressive_web_app = """<html>
<head>
 <description>selected meta description</description>
 <meta property="og:description" content="selected og:description" />
 <meta itemprop="datePublished" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="uploadDate" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="genre" content="Science &amp; Technology">
 <link rel="manifest" href="test_page_manifest.json" />
 </head>
    <body>
    </body>
</html>
"""

webpage_perfect_contents = """<html lang="pl">
<head>
 <title>title</title>
 <description>selected meta description</description>
 <author>author</author>
 <keywords>nothing else matters</keywords>
 <meta name="title" content="meta title" />
 <meta name="description" content="meta description" />

 <meta property="og:title" content="selected og:title" />
 <meta property="og:description" content="selected og:description" />
 <meta property="og:image" href="https://something-someting.com" />

 <meta itemprop="datePublished" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="uploadDate" content="2024-01-11T09:00:07-00:00">
 <meta itemprop="genre" content="Science &amp; Technology">

 <link rel="manifest" href="test_page_manifest.json" />
</head>
    <body>
    </body>
</html>
"""

webpage_html_canonical_1 = """<html>
 <head>
 <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
 <link rel="canonical" href="https://www.example.com/">
 <title>YouTube</title>

 </head>
 <body>
 page body
 </body>
"""

webpage_html_canonical_2 = """<html>
 <head>
 <link rel="shortcut icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" type="image/x-icon"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png" sizes="32x32"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png" sizes="48x48"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png" sizes="96x96"><link rel="icon" href="https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png" sizes="144x144">
 <link rel="canonical" href="https://www.example.com/">
 <title>YouTube</title>

 </head>
 <body>
 page body
 </body>
"""


class HtmlPageTest(FakeInternetTestCase):
    def test_default_language(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_no_lang)
        self.assertEqual(p.get_language(), "")
        self.assertTrue(p.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_language_it(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_lang_not_default)
        self.assertEqual(p.get_language(), "it")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_no_title(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_no_title)

        # when page has no title, URL is chosen for the title
        self.assertEqual(p.get_title(), None)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_title_lowercase(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_title_lower)
        self.assertEqual(p.get_title(), "This is a lower case title")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_title_uppercase(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_title_upper)
        self.assertEqual(p.get_title(), "This is a upper case title")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_title_head(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_title_head)
        self.assertEqual(p.get_title(), "selected title")
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_title_meta(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_title_meta)
        self.assertEqual(p.get_title(), "selected meta title")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_title_meta_og(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_title_meta_og)
        self.assertEqual(p.get_title(), "selected og:title")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_description_head(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_description_head)
        self.assertEqual(p.get_description(), "selected description")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_description_meta(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_description_meta)
        self.assertEqual(p.get_description(), "selected meta description")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_description_meta_og(self):
        MockRequestCounter.mock_page_requests = 0

        # default language
        p = HtmlPage("https://linkedin.com/test", webpage_description_meta_og)
        self.assertEqual(p.get_description(), "selected og:description")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_links(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage("http://mytestpage.com/test", webpage_links)

        links = p.get_links()

        self.assertTrue("http://otherpage1.net" in links)
        self.assertTrue("https://otherpage2.net" in links)

        self.assertTrue("http://mytestpage.com/test/test1" in links)
        self.assertTrue("http://mytestpage.com/test/test2.html" in links)
        self.assertTrue("http://mytestpage.com/test/test3.htm" in links)
        # java script is not accepted by default
        self.assertTrue("http://mytestpage.com/test/test4.js" not in links)
        self.assertTrue("http://mytestpage.com/test/test5/" in links)
        self.assertTrue("https://test6.domain.com/" in links)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_links_nodomain(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage("http://mytestpage.com/test", webpage_links)

        links = p.get_links()

        self.assertTrue("http://otherpage1.net" in links)
        self.assertTrue("https://otherpage2.net" in links)

        self.assertTrue("http://mytestpage.com/test/test1" in links)
        self.assertTrue("http://mytestpage.com/test/test2.html" in links)
        self.assertTrue("http://mytestpage.com/test/test3.htm" in links)
        # java script is not accepted by default
        self.assertTrue("http://mytestpage.com/test/test4.js" not in links)
        self.assertTrue("http://mytestpage.com/test/test5/" in links)
        self.assertTrue("https://test6.domain.com/" in links)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_rss_url(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage("https://linkedin.com/test", webpage_rss_links)

        rss_url = p.get_rss_url()

        self.assertEqual("http://your-site.com/your-feed1.rss", rss_url)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_rss_urls(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage("https://linkedin.com/test", webpage_rss_links)

        all_rss = p.get_feeds()

        self.assertTrue("http://your-site.com/your-feed1.rss" in all_rss)
        self.assertTrue("http://your-site.com/your-feed2.rss" in all_rss)
        self.assertTrue("http://your-site.com/your-feed3.rss" in all_rss)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_favicons(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage("https://linkedin.com/test", webpage_html_favicon)

        all_favicons = p.get_favicons()

        self.assertTrue(
            "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon.ico" in all_favicons
        )
        self.assertTrue(
            "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_32x32.png"
            in all_favicons
        )
        self.assertTrue(
            "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_48x48.png"
            in all_favicons
        )
        self.assertTrue(
            "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_96x96.png"
            in all_favicons
        )
        self.assertTrue(
            "https://www.youtube.com/s/desktop/e4d15d2c/img/favicon_144x144.png"
            in all_favicons
        )
        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_date_published_article_date(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage(
            "https://linkedin.com/test",
            webpage_meta_article_date,
        )

        date = p.get_date_published()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-09T21:26:00+00:00")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_date_published_music_date(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage(
            "https://linkedin.com/test",
            webpage_meta_music_release_date,
        )

        date = p.get_date_published()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-09T21:26:00+00:00")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_date_published_youtube(self):
        MockRequestCounter.mock_page_requests = 0

        p = HtmlPage(
            "https://linkedin.com/test",
            webpage_meta_youtube_publish_date,
        )

        date = p.get_date_published()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-11T09:00:07+00:00")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_contents_body_hash(self):
        MockRequestCounter.mock_page_requests = 0

        reader = HtmlPage(
            "https://linkedin.com/test", webpage_meta_youtube_publish_date
        )
        hash = reader.get_contents_body_hash()
        bodytext = str(reader.get_body_text())

        self.assertTrue(bodytext)
        self.assertTrue(bodytext != "")

        self.assertEqual(hash, calculate_hash(bodytext))

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_links_encoded(self):
        MockRequestCounter.mock_page_requests = 0

        reader = HtmlPage("https://linkedin.com/test", webpage_html_encoded_links)
        links = sorted(list(reader.get_links()))

        self.assertEqual(links[0], "http://github-help-wanted.com")
        self.assertEqual(links[1], "https://github.com/pyFFTW/pyFFTW")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_meta_charset(self):
        MockRequestCounter.mock_page_requests = 0

        reader = HtmlPage("https://linkedin.com/test", webpage_html_meta_charset)
        self.assertEqual(reader.get_charset(), "shift_jis")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_meta_http_equiv_charset(self):
        MockRequestCounter.mock_page_requests = 0

        reader = HtmlPage(
            "https://linkedin.com/test", webpage_html_meta_http_equiv_charset
        )
        self.assertEqual(reader.get_charset(), "shift_jis")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_schema_field(self):
        reader = HtmlPage("https://linkedin.com/test", webpage_html_schema_fields)
        self.assertEqual(
            reader.get_schema_field("url"), "https://www.youtube.com/watch?v=111"
        )
        self.assertEqual(reader.get_schema_field("name"), "itemprop name")
        self.assertEqual(reader.get_schema_field("description"), "itemprop description")
        self.assertEqual(
            reader.get_schema_field("thumbnailUrl"), "https://thumbnailurl.com"
        )

    def test_get_schema_field_ex(self):
        reader = HtmlPage(
            "https://linkedin.com/test", webpage_html_schema_fields_nested
        )
        self.assertEqual(
            reader.get_schema_field_ex("http://schema.org/VideoObject", "url"),
            "https://www.youtube.com/watch?v=111",
        )
        self.assertEqual(
            reader.get_schema_field_ex("http://schema.org/Person", "url"),
            "http://www.youtube.com/@someotherchannel",
        )

    def test_is_pwa(self):
        page = HtmlPage("https://linkedin.com/test", webpage_progressive_web_app)

        self.assertTrue(page.is_pwa())

        page = HtmlPage("https://linkedin.com/test", webpage_html_schema_fields_nested)

        self.assertFalse(page.is_pwa())

    def test_get_pwa_manifest(self):
        page = HtmlPage("https://linkedin.com/test", webpage_progressive_web_app)

        self.assertEqual(page.get_pwa_manifest(), "test_page_manifest.json")

    def test_get_page_rating__perfect(self):
        page = HtmlPage("https://perfect.com", webpage_perfect_contents)

        # call tested function
        rating_100 = page.get_page_rating()

        self.assertEqual(rating_100, 100)

        page = HtmlPage("https://www.perfect.com", webpage_perfect_contents)

        # call tested function
        rating_1 = page.get_page_rating()

        self.assertLess(rating_1, rating_100)

        page = HtmlPage("https://something.www.perfect.com", webpage_perfect_contents)

        # call tested function
        rating_2 = page.get_page_rating()

        self.assertLess(rating_2, rating_1)

    def test_get_thumbnail__schema_meta_icon(self):
        web = """<!doctype html><html itemscope="" itemtype="http://schema.org/WebPage" lang="pl"><head><meta charset="UTF-8"><meta content="origin" name="referrer"><meta content="/images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>Google</title><script nonce="WDUp12mzuYwOMOCAENBRFg">window._hst=Date.now();pe</script></head></html>"""

        page = HtmlPage("https://google.com", web)

        schema_image = page.get_schema_field("image")

        self.assertEqual(
            schema_image,
            "/images/branding/googleg/1x/googleg_standard_color_128dp.png",
        )

        # call tested function
        thumbnail = page.get_thumbnail()

        self.assertEqual(
            thumbnail,
            "https://google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png",
        )

    def test_get_canonical_url(self):
        contents = webpage_html_canonical_1

        page = HtmlPage("https://google.com", contents)

        # call tested function
        link = page.get_canonical_url()

        self.assertEqual(link, "https://www.example.com")

        contents = webpage_html_canonical_2

        page = HtmlPage("https://google.com", contents)

        # call tested function
        link = page.get_canonical_url()

        self.assertEqual(link, "https://www.example.com")
