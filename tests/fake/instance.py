from utils.dateutils import DateUtils


"""
################################################################################
Instance data
"""

instance_entries_json = """
{
  "links": [
    {
      "source_url": "https://www.lemonde.fr/en/rss/une.xml",
      "title": "Yotam Ottolenghi: 'A cuisine is never static'",
      "description": "The British-Israeli chef",
      "link": "https://www.lemonde.fr/en/lifestyle/article/2024/01/03/yotam-ottolenghi-a-cuisine-is-never-static_6398241_37.html",
      "date_published": "{0}",
      "permanent": false,
      "bookmarked": false,
      "dead": false,
      "author": "Le Monde",
      "album": "Le Monde",
      "user": null,
      "language": "en-US",
      "thumbnail": null,
      "age": null,
      "page_rating_contents": 0,
      "page_rating_votes": 0,
      "page_rating_visits": 0,
      "page_rating": 0,
      "tags": [
        "testtag1",
        "testtag2"
      ],
      "vote": 10,
      "comments": [
         {"comment": "test", "user": "testuser", "date_published": "2024-02-25T11:35:31.382590+00:00", "date_edited": "2024-02-25T11:35:31.382590+00:00", "reply_id": null
         }
      ]
    },
    {
      "source_url": "https://moxie.foxnews.com/google-publisher/latest.xml",
      "title": "Next hot thing in hot wings, 'trashed' or 'dirty,' breaks the rules of America's favorite bar food",
      "description": "Double-fried wings, called trash wings in Missouri and dirt wings in Connecticut, have been a regional phenomenon for decades and are poised to become a national trend.",
      "link": "https://www.foxnews.com/lifestyle/next-hot-thing-hot-wings-trashed-dirty-breaks-rules-americas-favorite-bar-food",
      "date_published": "{0}",
      "permanent": false,
      "bookmarked": false,
      "dead": false,
      "author": "Fox News",
      "album": "Fox News",
      "user": null,
      "language": "en-US",
      "thumbnail": "https://global.fncstatic.com/static/orion/styles/img/fox-news/logos/fox-news-desktop.png",
      "age": null,
      "page_rating_contents": 0,
      "page_rating_votes": 0,
      "page_rating_visits": 0,
      "page_rating": 0,
      "tags": [],
      "vote": 20,
      "comments": []
    }
  ]
}
""".replace(
    "{0}", DateUtils.get_datetime_now_iso()
)

instance_sources_json_empty = """{"sources": []}"""

instance_entries_json_empty = """{"links": []}"""

instance_entries_source_100_json = """
{
  "links": [
    {
      "source_url": "https://www.lemonde.fr/en/rss/une.xml",
      "title": "Yotam Ottolenghi: 'A cuisine is never static'",
      "description": "The British-Israeli chef",
      "link": "https://www.lemonde.fr/first-link.html",
      "date_published": "{0}",
      "permanent": false,
      "bookmarked": false,
      "dead": false,
      "author": "Le Monde",
      "album": "Le Monde",
      "user": null,
      "language": "en-US",
      "thumbnail": null,
      "age": null,
      "page_rating_contents": 0,
      "page_rating_votes": 0,
      "page_rating_visits": 0,
      "page_rating": 0,
      "tags": [
        "testtag1",
        "testtag2"
      ],
      "vote": 0,
      "comments": [
         {"comment": "test", "user": "testuser", "date_published": "2024-02-25T11:35:31.382590+00:00", "date_edited": "2024-02-25T11:35:31.382590+00:00", "reply_id": null
         }
      ]
    }
  ]
}
""".replace(
    "{0}", DateUtils.get_datetime_now_iso()
)

instance_source_100_url = "https://www.lemonde.fr/en/rss/une.xml"
instance_source_100_json = """
{
  "id": 100,
  "url": "https://www.lemonde.fr/en/rss/une.xml",
  "title": "Source100",
  "category_name": "Source 100 Category",
  "subcategory_name": "Source 100 Subcategory",
  "dead": false,
  "export_to_cms": true,
  "remove_after_days": "0",
  "language": "en-US",
  "favicon": "https://yt3.ggpht.com/ytc/AGIKgqMox432cx8APsB9u4UELfpZTjZlzO8nGU_M3PZ_nw=s48-c-k-c0x00ffffff-no-rj",
  "enabled": true,
  "fetch_period": 3600,
  "source_type": "BaseRssPlugin"
}
"""

instance_source_101_json = """
{
  "id": 101,
  "url": "https://3dprinting.com/feed",
  "title": "3DPrinting.com",
  "category_name": "Tech",
  "subcategory_name": "News",
  "dead": false,
  "export_to_cms": true,
  "remove_after_days": "0",
  "language": "en-US",
  "favicon": "https://3dprinting.com/wp-content/uploads/cropped-3dp-site-icon-32x32.png",
  "enabled": true,
  "fetch_period": 1800,
  "source_type": "BaseRssPlugin"
}
"""

instance_source_102_json = """
{
  "id": 102,
  "url": "https://www.404media.co/rss",
  "title": "404 Media",
  "category_name": "New",
  "subcategory_name": "New",
  "dead": false,
  "export_to_cms": false,
  "remove_after_days": "0",
  "language": "en",
  "favicon": "https://www.404media.co/favicon.png",
  "enabled": true,
  "fetch_period": 900,
  "source_type": "BaseRssPlugin"
}
"""

instance_source_103_json = """
{
   "id": 313,
   "url": "https://9to5linux.com/category/news/feed",
   "title": "9to5Linux News",
   "category_name": "Tech",
   "subcategory_name": "Tech",
   "dead": false,
   "export_to_cms": true,
   "remove_after_days": "0",
   "language": "en-US",
   "favicon": "https://i0.wp.com/9to5linux.com/wp-content/uploads/2021/04/cropped-9to5linux-logo-mini-copy.png",
   "enabled": true,
   "fetch_period": 900,
   "source_type": "BaseRssPlugin"
}
"""

instance_source_104_json = """
{
   "id": 104,
   "url": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics",
   "title": "AAAS: Science Robotics: Table of Contents",
   "category_name": "Science",
   "subcategory_name": "Science",
   "dead": false,
   "export_to_cms": true,
   "remove_after_days": "0",
   "language": "en-US",
   "favicon": "https://www.science.org/favicon.ico",
   "enabled": true,
   "fetch_period": 900,
   "source_type": "BaseRssPlugin"
}
"""

instance_source_105_json = """
{
   "id": 105,
   "url": "http://feeds.abcnews.com/abcnews/topstories",
   "title": "ABC News",
   "category_name": "News",
   "subcategory_name": "News",
   "dead": false,
   "export_to_cms": true,
   "remove_after_days": "0",
   "language": "en-US",
   "favicon": "https://abcnews.go.com/favicon.ico",
   "enabled": true,
   "fetch_period": 3600,
   "source_type": "BaseRssPlugin"
}
"""

instance_sources_page_1 = f"""
{{
  "sources": [
    {instance_source_100_json},
    {instance_source_101_json},
    {instance_source_102_json}
  ]
}}
"""

instance_sources_page_2 = f"""
{{
  "sources": [
    {instance_source_103_json},
    {instance_source_104_json},
    {instance_source_105_json}
  ]
}}
"""
