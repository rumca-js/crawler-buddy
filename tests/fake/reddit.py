from utils.dateutils import DateUtils


reddit_rss_text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
  <category term="rss" label="r/rss"/>
  <updated>{date}</updated>
  <icon>https://www.redditstatic.com/icon.png/</icon>
  <id>/r/rss/.rss</id>
  <link rel="self" href="https://www.reddit.com/r/rss/.rss" type="application/atom+xml"/>
  <link rel="alternate" href="https://www.reddit.com/r/rss/" type="text/html"/>
  <title>RSS - Really Simple Syndication</title>
  <entry>
    <author>
      <name>/u/still-standing</name>
      <uri>https://www.reddit.com/user/still-standing</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;original post &lt;a href="https://www.reddit.com/r/rss/comments/fvg3ed/i_built_a_better_rss_feed_for_reddit/"&gt;https://www.reddit.com/r/rss/comments/fvg3ed/i_built_a_better_rss_feed_for_reddit/&lt;/a&gt;&lt;/p&gt; &lt;p&gt;I&amp;#39;ve noticed many of the users of my improved rss feed for reddit are using it for... videos, gifs, and images.&lt;/p&gt; &lt;p&gt;I&amp;#39;ve made some improvements in this department.&lt;/p&gt; &lt;p&gt;&lt;a href="https://i.imgur.com/w85gSGM.png"&gt;grid view&lt;/a&gt; // &lt;a href="https://i.imgur.com/EvjfqhY.png"&gt;post view&lt;/a&gt;&lt;/p&gt; &lt;ol&gt; &lt;li&gt;Now it try&amp;#39;s to detect image and video content and embed it into feedly!&lt;/li&gt; &lt;li&gt;If your feed reader supports iframes (feedly does) it will even embed gfycat and &lt;a href="https://v.redd.it"&gt;v.redd.it&lt;/a&gt; content.&lt;/li&gt; &lt;li&gt;If there are other popular video formats you want me to try and embed let me know.&lt;/li&gt; &lt;/ol&gt; &lt;p&gt;If you are interested in using it to you:&lt;/p&gt; &lt;ol&gt; &lt;li&gt;Go to a subreddit or meta feed you like example: &lt;a href="https://www.reddit.com/r/aww/"&gt;https://www.reddit.com/r/aww/&lt;/a&gt;&lt;/li&gt; &lt;li&gt;Add .json onto the end: &lt;a href="https://www.reddit.com/r/aww.json"&gt;https://www.reddit.com/r/aww.json&lt;/a&gt;&lt;/li&gt; &lt;li&gt;Change the domain name to, &lt;a href="https://reddit.0qz.fun/"&gt;reddit.0qz.fun&lt;/a&gt; like: &lt;a href="https://reddit.0qz.fun/r/aww.json"&gt;https://reddit.0qz.fun/r/aww.json&lt;/a&gt;&lt;/li&gt; &lt;li&gt;Subscribe to ^^^ that url in your favorite feed reader.&lt;/li&gt; &lt;/ol&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/still-standing"&gt; /u/still-standing &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/galitc/my_improved_reddit_rss_feed_now_support_videos/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/galitc/my_improved_reddit_rss_feed_now_support_videos/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_galitc</id>
    <link href="https://www.reddit.com/r/rss/comments/galitc/my_improved_reddit_rss_feed_now_support_videos/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>My improved reddit rss feed now support videos, gifs, and images</title>
  </entry>
  <entry>
    <author>
      <name>/u/Info-Tube-Mario</name>
      <uri>https://www.reddit.com/user/Info-Tube-Mario</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Info-Tube-Mario"&gt; /u/Info-Tube-Mario &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="/r/rss/comments/1fez2d4/seeking_feedback_on_my_aipowered_rss_reader/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fozr6j/in_the_previous_post_some_showed_interest_in_this/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fozr6j</id>
    <link href="https://www.reddit.com/r/rss/comments/1fozr6j/in_the_previous_post_some_showed_interest_in_this/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>In the previous post, some showed interest in this concept. Now ready a tool for it. It allows filtering by natural language, request daily from RSS. It's an online service. Try if interested : checka.ai</title>
  </entry>
  <entry>
    <author>
      <name>/u/Low-Association-2174</name>
      <uri>https://www.reddit.com/user/Low-Association-2174</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I&amp;#39;m currently working on a project that scrapes news from various platforms, and I&amp;#39;m curious if RSS feeds can be relied on to fetch news in real-time. Does anyone have experience with this? I&amp;#39;m particularly interested in understanding how RSS works, as I&amp;#39;m not very familiar with it. Also, if anyone knows the best way to capture new articles from news platform like &lt;em&gt;The Guardian&lt;/em&gt; as soon as they&amp;#39;re published, that would be helpful.&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Low-Association-2174"&gt; /u/Low-Association-2174 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fnmeq0/can_rss_feeds_be_used_for_realtime_news_scraping/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fnmeq0/can_rss_feeds_be_used_for_realtime_news_scraping/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fnmeq0</id>
    <link href="https://www.reddit.com/r/rss/comments/1fnmeq0/can_rss_feeds_be_used_for_realtime_news_scraping/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Can RSS Feeds Be Used for Real-Time News Scraping? Seeking Advice</title>
  </entry>
  <entry>
    <author>
      <name>/u/Much-Mud7869</name>
      <uri>https://www.reddit.com/user/Much-Mud7869</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Does anyone know of an RSS generator that works with this damn site?&lt;a href="https://fcbayern.com/de/tag/news"&gt;https://fcbayern.com/de/tag/news&lt;/a&gt; I&amp;#39;ve tried many generators, but none have been effective with this difficult user interface.&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Much-Mud7869"&gt; /u/Much-Mud7869 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmr5a1/generating_rss_for_a_difficult_site/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmr5a1/generating_rss_for_a_difficult_site/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fmr5a1</id>
    <link href="https://www.reddit.com/r/rss/comments/1fmr5a1/generating_rss_for_a_difficult_site/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Generating RSS for a difficult site</title>
  </entry>
  <entry>
    <author>
      <name>/u/eyal8r</name>
      <uri>https://www.reddit.com/user/eyal8r</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Just started using rss.app. I notice that when I set a keyword in the blacklist, it doesn&amp;#39;t save it permanently. It only keeps the keyword while I&amp;#39;m on that preview page. I&amp;#39;ve saved it, created a new bundle after I input the keywords but nothing seems to work. Any suggestions?&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/eyal8r"&gt; /u/eyal8r &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmu73v/rssapp_keyword_filters_dont_save/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmu73v/rssapp_keyword_filters_dont_save/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fmu73v</id>
    <link href="https://www.reddit.com/r/rss/comments/1fmu73v/rssapp_keyword_filters_dont_save/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>rss.app - Keyword Filters Don't Save?</title>
  </entry>
  <entry>
    <author>
      <name>/u/International_Swan_1</name>
      <uri>https://www.reddit.com/user/International_Swan_1</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hey all,&lt;/p&gt; &lt;p&gt;New here &amp;amp; this is a genuine query. &lt;/p&gt; &lt;p&gt;I&amp;#39;m thinking of building a chrome extension that turns my browser&amp;#39;s &amp;quot;new tab&amp;quot; into a clean, slick feedly-like feed reader, without looking crowded. Similar to firefox&amp;#39;s new tab articles list, for example. I like my new tabs clean, simple &amp;amp; fast. &lt;/p&gt; &lt;p&gt;The idea being it&amp;#39;ll keep me updated on the latest, passively, without any extra effort on my part to remember to go to a website/feed reader. Plus the articles / headlines are always at the corner of my eye as i open new tabs, so even if I don&amp;#39;t actually click on anything, subconsciously I still stay updated. &lt;/p&gt; &lt;p&gt;I&amp;#39;m wondering :&lt;br/&gt; 1. If this is something worth building and publishing to the store, for you all ? &lt;/p&gt; &lt;ol&gt; &lt;li&gt;&lt;p&gt;If so, what features would you like to see in it ? &amp;amp; What should I absolutely avoid ? &lt;/p&gt;&lt;/li&gt; &lt;li&gt;&lt;p&gt;Would you pay an LTD for it ? if yes, how much is reasonable ?&lt;/p&gt;&lt;/li&gt; &lt;/ol&gt; &lt;p&gt;PS - If anyone&amp;#39;s interested in the extn, please feel free to DM, because i don&amp;#39;t want to spam any links here, unless it&amp;#39;s by popular demand.&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/International_Swan_1"&gt; /u/International_Swan_1 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmapo9/im_thinking_of_publishing_a_freeltd_feed_reader/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fmapo9/im_thinking_of_publishing_a_freeltd_feed_reader/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fmapo9</id>
    <link href="https://www.reddit.com/r/rss/comments/1fmapo9/im_thinking_of_publishing_a_freeltd_feed_reader/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>I'm thinking of publishing a free/ltd feed reader chrome extn, but not sure</title>
  </entry>
  <entry>
    <author>
      <name>/u/Laeryth_</name>
      <uri>https://www.reddit.com/user/Laeryth_</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hello everyone, I have a noobie question :&lt;/p&gt; &lt;p&gt;Does anyone have a basic RSS feed that just sends the very important basic news (like 1 or 2 weekly) ?&lt;/p&gt; &lt;p&gt;By &amp;quot;important basic news&amp;quot;, I mean news like the riots in London, the the assassination attempt on Trump, the Paris olympic games, elections in foreign countries, begining of demonstration/riots/wars...&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Laeryth_"&gt; /u/Laeryth_ &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fm6xt4/weekly_general_news_rss_feed/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fm6xt4/weekly_general_news_rss_feed/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fm6xt4</id>
    <link href="https://www.reddit.com/r/rss/comments/1fm6xt4/weekly_general_news_rss_feed/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Weekly general news rss feed</title>
  </entry>
  <entry>
    <author>
      <name>/u/Slow_Independent5321</name>
      <uri>https://www.reddit.com/user/Slow_Independent5321</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Enter a link to get an rss&lt;/p&gt; &lt;p&gt;view &lt;a href="https://web2rss.cc"&gt;web2rss.cc&lt;/a&gt;&lt;/p&gt; &lt;p&gt;privatization &lt;a href="https://github.com/weekend-project-space/web2rss"&gt;github-web2rss&lt;/a&gt;&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Slow_Independent5321"&gt; /u/Slow_Independent5321 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1flxuy0/input_site_output_rss/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1flxuy0/input_site_output_rss/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1flxuy0</id>
    <link href="https://www.reddit.com/r/rss/comments/1flxuy0/input_site_output_rss/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>input site output rss</title>
  </entry>
  <entry>
    <author>
      <name>/u/Consumermicrosystems</name>
      <uri>https://www.reddit.com/user/Consumermicrosystems</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Consumermicrosystems"&gt; /u/Consumermicrosystems &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="/r/feedly/comments/1fkm6ln/does_anyone_know_how_to_use_feedly_as_a_proxy/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fkm9r6/does_anyone_know_how_to_use_feedly_as_a_proxy/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fkm9r6</id>
    <link href="https://www.reddit.com/r/rss/comments/1fkm9r6/does_anyone_know_how_to_use_feedly_as_a_proxy/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Does anyone know how to use Feedly as a proxy similar to the way Feedburner generates proxy feeds?</title>
  </entry>
  <entry>
    <author>
      <name>/u/One_Function_6668</name>
      <uri>https://www.reddit.com/user/One_Function_6668</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hello,&lt;/p&gt; &lt;p&gt;I&amp;#39;m looking to expand my collection of RSS feeds related to Tax, Accounting, Wealth, Estate and other relevant financial topics.&lt;/p&gt; &lt;p&gt;I already have the following feeds:&lt;/p&gt; &lt;pre&gt;&lt;code&gt;(&amp;quot;https://finance.yahoo.com/news/rssindex&amp;quot;, &amp;quot;Yahoo! - Finance&amp;quot;), (&amp;quot;https://tax.thomsonreuters.com/blog/feed/&amp;quot;, &amp;quot;Thomson Reuters - Tax &amp;amp; Accounting&amp;quot;), (&amp;quot;https://feeds.bloomberg.com/wealth/news.rss&amp;quot;, &amp;quot;Bloomberg - Wealth&amp;quot;), (&amp;quot;https://feeds.bloomberg.com/markets/news.rss&amp;quot;, &amp;quot;Bloomberg - Markets&amp;quot;), (&amp;quot;https://www.thetaxadviser.com/content/tta-home/news.xml/&amp;quot;, &amp;quot;The Tax Adviser News&amp;quot;), (&amp;quot;https://www.taxpolicycenter.org/topic/individual-taxes/rss.xml&amp;quot;, &amp;quot;Tax Policy Center - Individual Taxes&amp;quot;), (&amp;quot;https://www.taxpolicycenter.org/topic/business-taxes/rss.xml&amp;quot;, &amp;quot;Tax Policy Center - Business Taxes&amp;quot;), (&amp;quot;https://taxfoundation.org/feed/&amp;quot;, &amp;quot;Tax Foundation&amp;quot;), (&amp;quot;https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&amp;amp;id=10001054&amp;quot;, &amp;quot;CNBC - Wealth&amp;quot;), (&amp;quot;https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&amp;amp;id=10000664&amp;quot;, &amp;quot;CNBC - Economy&amp;quot;), (&amp;quot;https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&amp;amp;id=15839069&amp;quot;, &amp;quot;CNBC - Investing&amp;quot;), (&amp;quot;https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB&amp;quot;, &amp;quot;Google News - Business&amp;quot;), (&amp;quot;https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE&amp;quot;, &amp;quot;Google News - U.S.&amp;quot;), (&amp;quot;https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB&amp;quot;, &amp;quot;Google News - World&amp;quot;), (&amp;quot;https://feeds.bbci.co.uk/news/business/rss.xml?edition=us&amp;quot;, &amp;quot;BBC News - Business (U.S.)&amp;quot;), (&amp;quot;https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml&amp;quot;, &amp;quot;BBC News - U.S. &amp;amp; Canada&amp;quot;) (&amp;quot;https://www.wealthmanagement.com/rss.xml&amp;quot;, &amp;quot;Wealth Management - Latest&amp;quot;), (&amp;quot;https://www.financial-planning.com/feed?rss=true&amp;quot;, &amp;quot;Financial Planning Magazine - Latest&amp;quot;), (&amp;quot;https://www.fa-mag.com/advice/estate-planning/rss&amp;quot;, &amp;quot;Financial Advisor Magazine - Estate Planning&amp;quot;), &lt;/code&gt;&lt;/pre&gt; &lt;p&gt;Do you have any recommendations for other RSS feeds I can add to my list?&lt;/p&gt; &lt;p&gt;Also if there are any official (U.S.) government feeds or other industry publications available I&amp;#39;d also love to hear about them.&lt;/p&gt; &lt;p&gt;TIA!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/One_Function_6668"&gt; /u/One_Function_6668 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fi0qnj/seeking_tax_accounting_wealth_and_estate_rss/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fi0qnj/seeking_tax_accounting_wealth_and_estate_rss/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fi0qnj</id>
    <link href="https://www.reddit.com/r/rss/comments/1fi0qnj/seeking_tax_accounting_wealth_and_estate_rss/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Seeking Tax, Accounting, Wealth, and Estate RSS Feeds (U.S.)</title>
  </entry>
  <entry>
    <author>
      <name>/u/Ill_Connection_3017</name>
      <uri>https://www.reddit.com/user/Ill_Connection_3017</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;It&amp;#39;s great to see the continued development of the new Reeder app. In the latest TestFlight update, a few new features were introduced, including support for folders.&lt;/p&gt; &lt;p&gt;As much as I want to use the new Reeder, the current home screen layout feels suboptimal. I think users should have the option to disable the default &amp;#39;category/type&amp;#39; view (e.g., Podcasts, YouTube, Mastodon) and instead rely solely on folders. Right now, having both folders and different feed categories makes navigation cumbersome. However, the developer mentioned that folder support is still in its early stages, so hopefully, we&amp;#39;ll see improvements in the coming weeks!&lt;/p&gt; &lt;p&gt;Video example: &lt;a href="https://dropover.cloud/9dd779"&gt;https://dropover.cloud/9dd779&lt;/a&gt; &lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Ill_Connection_3017"&gt; /u/Ill_Connection_3017 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fi0f4p/folders_are_a_welcome_addition_in_the_new_reeder/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fi0f4p/folders_are_a_welcome_addition_in_the_new_reeder/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fi0f4p</id>
    <link href="https://www.reddit.com/r/rss/comments/1fi0f4p/folders_are_a_welcome_addition_in_the_new_reeder/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Folders are a welcome addition in the new Reeder, but needs serious work to be useful.</title>
  </entry>
  <entry>
    <author>
      <name>/u/MonsterGreen_</name>
      <uri>https://www.reddit.com/user/MonsterGreen_</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hello Reddit community! I&amp;#39;m currently exploring ways to integrate RSS feeds with Make.com for automation purposes. While RSS.com is a popular choice, it requires a subscription. I&amp;#39;m looking for any free alternatives that are reliable and compatible with Make.com. Does anyone have experience with free RSS generators that work well for automating tasks on Make.com as free? Any recommendations or advice would be greatly appreciated!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/MonsterGreen_"&gt; /u/MonsterGreen_ &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhz99v/seeking_advice_free_alternatives_for_rss/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhz99v/seeking_advice_free_alternatives_for_rss/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fhz99v</id>
    <link href="https://www.reddit.com/r/rss/comments/1fhz99v/seeking_advice_free_alternatives_for_rss/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Seeking Advice: Free Alternatives for RSS Generators Compatible with Make.com</title>
  </entry>
  <entry>
    <author>
      <name>/u/el_piqo</name>
      <uri>https://www.reddit.com/user/el_piqo</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hi there,&lt;br/&gt; I just pushed &lt;a href="https://github.com/piqoni/cast-text"&gt;CAST-Text&lt;/a&gt; - a very simple to use (only arrows or hjkl is all you need) terminal app to read articles in full. It&amp;#39;s also very fast, not only because its a terminal app, but also it prefetches the adjacent articles, so everything is instant. By default it will open BBC, but you can pass any rss/atom feed to it. &lt;/p&gt; &lt;p&gt;Let me know what you think, or if you think of a good feature that I can add.&lt;br/&gt; Thanks. &lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/el_piqo"&gt; /u/el_piqo &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhg3nf/casttext_a_zerolatency_fulltext_article_reader_in/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhg3nf/casttext_a_zerolatency_fulltext_article_reader_in/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fhg3nf</id>
    <link href="https://www.reddit.com/r/rss/comments/1fhg3nf/casttext_a_zerolatency_fulltext_article_reader_in/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>CAST-text: A zero-latency, full-text article reader in terminal.</title>
  </entry>
  <entry>
    <author>
      <name>/u/eyal8r</name>
      <uri>https://www.reddit.com/user/eyal8r</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I have a blog site I want to search for a specific term, and turn the results into an RSS url. I am then using the RSS URL inside notion/make in order to do some further automations with it. I&amp;#39;ve tried &lt;a href="http://rss.app"&gt;rss.app&lt;/a&gt; and rsseverything, but it won&amp;#39;t work. HOWEVER, feedly will turn it into a feed, but I don&amp;#39;t know how to get an RSS url out of feedly. Can anyone help me figure out a way to do this?&lt;br/&gt; URL: &lt;a href="https://mouthbysouthwest.com/?s=Gilbert"&gt;https://mouthbysouthwest.com/?s=Gilbert&lt;/a&gt;&lt;/p&gt; &lt;p&gt;Thank you!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/eyal8r"&gt; /u/eyal8r &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhpvss/need_help_creating_an_rss_from_search_results_on/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fhpvss/need_help_creating_an_rss_from_search_results_on/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fhpvss</id>
    <link href="https://www.reddit.com/r/rss/comments/1fhpvss/need_help_creating_an_rss_from_search_results_on/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Need Help Creating an RSS from Search Results on a Blog Site</title>
  </entry>
  <entry>
    <author>
      <name>/u/MerrilyAshes</name>
      <uri>https://www.reddit.com/user/MerrilyAshes</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;A few years ago, I bought Reeder 5 for MacBook but haven’t used it much. Now, I’m hoping to start using it to build a personal knowledge hub (including videos, podcasts, journals, and magazines). I plan to use it across both iOS and MacBook.&lt;/p&gt; &lt;p&gt;I saw that Reeder’s latest version just launched, and it looks great, though it seems like its features still need some polishing. &lt;/p&gt; &lt;p&gt;Should I spend $5 to buy Reeder 5 for iOS, or is it better to subscribe to the new Reeder version for $10 a year and get cross-platform access? Would love to hear from anyone who&amp;#39;s used either one!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/MerrilyAshes"&gt; /u/MerrilyAshes &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fh8wyf/new_reeder_or_classical/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fh8wyf/new_reeder_or_classical/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fh8wyf</id>
    <link href="https://www.reddit.com/r/rss/comments/1fh8wyf/new_reeder_or_classical/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>New Reeder or Classical?</title>
  </entry>
  <entry>
    <author>
      <name>/u/_Floydimus</name>
      <uri>https://www.reddit.com/user/_Floydimus</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I am looking for reliable, factual, and unbiased sources to stay updated in&lt;/p&gt; &lt;ol&gt; &lt;li&gt;Tech as a) open source, b) privacy, c) Linux (and Ubuntu), and d) general tech advancement&lt;/li&gt; &lt;li&gt;Art as a) modern/contemporary art, b) artists, c) art movements, and d) historic stuff as well&lt;/li&gt; &lt;li&gt;News preference a) economy, b) policies, c) finance, etc. I would like to avoid a) war, b) crime, c) violence, d) death or anything that is disturbing&lt;/li&gt; &lt;/ol&gt; &lt;p&gt;Any suggestions would be appreciated. Thank you!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/_Floydimus"&gt; /u/_Floydimus &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fh6poh/looking_for_reliable_factual_and_unbiased_sources/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fh6poh/looking_for_reliable_factual_and_unbiased_sources/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fh6poh</id>
    <link href="https://www.reddit.com/r/rss/comments/1fh6poh/looking_for_reliable_factual_and_unbiased_sources/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Looking for reliable, factual, and unbiased sources in tech, art, and news</title>
  </entry>
  <entry>
    <author>
      <name>/u/brygada_sfm</name>
      <uri>https://www.reddit.com/user/brygada_sfm</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I don&amp;#39;t have any specific knowledge about the RSS technology or the IT in general, I am a complete layman. I use Inoreader for both existing feeds and the ones that I create myself via MoRSS.it, FetchRSS.com and FiveFilters.org. I have found out so far about the importance of a keyword that follows the &amp;quot;class=&amp;quot; in an article element in the source code of the page, it has helped me to create some feeds via FiveFilters.org. For example I was able to make a feed from &amp;quot;&lt;a href="https://wyborcza.pl/0,128956.html?autor=Dominika+Wielowieyska"&gt;https://wyborcza.pl/0,128956.html?autor=Dominika+Wielowieyska&lt;/a&gt;&amp;quot; knowing the class value of an article is &amp;quot;index--headline&amp;quot;.&lt;/p&gt; &lt;p&gt;But sometimes this knowledge isn&amp;#39;t enough. When it comes to the &amp;quot;&lt;a href="https://wydarzenia.interia.pl/autor/kamila-baranowska"&gt;https://wydarzenia.interia.pl/autor/kamila-baranowska&lt;/a&gt;&amp;quot; website I am unable to parse it correctly, even though I know that the class value of an article is &amp;quot;sc-blmETK.gYzDaV&amp;quot;. I have read a bit about the Java Script or something like that which might be the cause of it, I don&amp;#39;t know.&lt;/p&gt; &lt;p&gt;The thing is there&amp;#39;s an extra paid version of Inoreader that allows you to create your own feeds inside the app, you just put the website address, you choose the parsing that suits your interest and you get a feed. I don&amp;#39;t have to pay though to see how it works, so I was able to see if Inoreder was able to parse the &amp;quot;&lt;a href="https://wydarzenia.interia.pl/autor/kamila-baranowska"&gt;https://wydarzenia.interia.pl/autor/kamila-baranowska&lt;/a&gt;&amp;quot; correctly and, as it seems, it could. Here is a link to the screen picture where I marked the option with the articles extracted properly from the page: &lt;a href="https://drive.google.com/file/d/1PUXg4-I7FczfZtetodk4RNw11DxKZ1wp/view"&gt;https://drive.google.com/file/d/1PUXg4-I7FczfZtetodk4RNw11DxKZ1wp/view&lt;/a&gt;&lt;/p&gt; &lt;p&gt;My questions is as follows: are there any free options to create such a feed with articles properly extracted from the page? If Inoreader can do it, why can&amp;#39;t anyone else? Can someone explain to me, a layman, what exactly is the problem with &amp;quot;&lt;a href="https://wydarzenia.interia.pl/autor/kamila-baranowska"&gt;https://wydarzenia.interia.pl/autor/kamila-baranowska&lt;/a&gt;&amp;quot;? What&amp;#39;s the difference between this page and the other mentioned that I could easly parse knowing the class value of an article?&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/brygada_sfm"&gt; /u/brygada_sfm &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fgmmp6/an_rss_feed_from_the_website_that_seems_to_be/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fgmmp6/an_rss_feed_from_the_website_that_seems_to_be/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fgmmp6</id>
    <link href="https://www.reddit.com/r/rss/comments/1fgmmp6/an_rss_feed_from_the_website_that_seems_to_be/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>An RSS feed from the website that seems to be "unRSSable"</title>
  </entry>
  <entry>
    <author>
      <name>/u/eric-pierce</name>
      <uri>https://www.reddit.com/user/eric-pierce</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/eric-pierce"&gt; /u/eric-pierce &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="/r/selfhosted/comments/1fg4uf9/release_freshrss_google_reader_api_plugin_for/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fg4v0q/release_freshrss_google_reader_api_plugin_for/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fg4v0q</id>
    <link href="https://www.reddit.com/r/rss/comments/1fg4v0q/release_freshrss_google_reader_api_plugin_for/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Release: FreshRSS / Google Reader API Plugin for Tiny-Tiny RSS</title>
  </entry>
  <entry>
    <author>
      <name>/u/zer0h0t</name>
      <uri>https://www.reddit.com/user/zer0h0t</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hey Reddit! I&amp;#39;m excited to introduce you all to &lt;a href="https://blueapplespace.top/"&gt;Blue Apple Space&lt;/a&gt;, a new platform that brings you closer to the news you care about! 🚀📰&lt;/p&gt; &lt;p&gt;&lt;a href="https://blueapplespace.top/"&gt;https://blueapplespace.top/&lt;/a&gt;&lt;/p&gt; &lt;p&gt;We&amp;#39;re building something unique—a place where news meets innovation, and where your interests always stay in the spotlight. 🎯📈&lt;/p&gt; &lt;p&gt;🔍 Why choose Blue Apple Space?&lt;/p&gt; &lt;ul&gt; &lt;li&gt;&lt;strong&gt;Personalized Feeds:&lt;/strong&gt; Tailor your news experience based on what matters to you.&lt;/li&gt; &lt;li&gt;&lt;strong&gt;Real-Time Updates:&lt;/strong&gt; Stay updated with the latest and greatest in real time.&lt;/li&gt; &lt;li&gt;&lt;strong&gt;AI-Driven Insights:&lt;/strong&gt; Dive deeper with AI-powered summaries and topic exploration.&lt;/li&gt; &lt;/ul&gt; &lt;p&gt;But that’s not all! We want to make this platform YOUR go-to for daily insights. 🌟&lt;/p&gt; &lt;p&gt;🤔 &lt;strong&gt;We need your help!&lt;/strong&gt;&lt;/p&gt; &lt;ul&gt; &lt;li&gt;What features do you absolutely need in your ideal news aggregator?&lt;/li&gt; &lt;li&gt;How can AI enhance your reading experience? Any specific tools or functionalities you&amp;#39;re excited about?&lt;/li&gt; &lt;/ul&gt; &lt;p&gt;This is going to be absolutely FREE for our early supporters. 🎉&lt;/p&gt; &lt;p&gt;Let&amp;#39;s shape the future of news together! Drop your suggestions in the comments below or visit us at &lt;a href="https://blueapplespace.top/"&gt;blueapplespace.top&lt;/a&gt; to get started.&lt;/p&gt; &lt;p&gt;Can&amp;#39;t wait to see what we build together! 💬🌍&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/zer0h0t"&gt; /u/zer0h0t &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fg1jem/discover_the_universe_of_news_with_blue_apple/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fg1jem/discover_the_universe_of_news_with_blue_apple/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fg1jem</id>
    <link href="https://www.reddit.com/r/rss/comments/1fg1jem/discover_the_universe_of_news_with_blue_apple/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>🌌✨ Discover the Universe of News with Blue Apple Space! ✨🌌</title>
  </entry>
  <entry>
    <author>
      <name>/u/Info-Tube-Mario</name>
      <uri>https://www.reddit.com/user/Info-Tube-Mario</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hey everyone,&lt;/p&gt; &lt;p&gt;I&amp;#39;ve been using RSS readers on and off for years, but I always struggle to stick with them long-term. I think I&amp;#39;ve finally figured out why:&lt;/p&gt; &lt;ol&gt; &lt;li&gt;I tend to subscribe to too many sources, leading to an overwhelming backlog of unread content.&lt;/li&gt; &lt;li&gt;It&amp;#39;s time-consuming and difficult to sift through all that content to find what I&amp;#39;m actually interested in.&lt;/li&gt; &lt;/ol&gt; &lt;p&gt;I feel like these issues might be pretty common, so I&amp;#39;ve started working on my own RSS reader to address them. Here&amp;#39;s what I&amp;#39;m thinking:&lt;/p&gt; &lt;ul&gt; &lt;li&gt;Using AI to help filter content based on my interests. For example, I could say &amp;quot;news about Trump&amp;quot; and select sources like NYT and Yahoo, then only see relevant articles.&lt;/li&gt; &lt;li&gt;Maintaining a curated list of RSS sources (some scraped) that users can choose from, similar to Feedly.&lt;/li&gt; &lt;li&gt;Having GPT generate summaries to make reading more efficient.&lt;/li&gt; &lt;/ul&gt; &lt;p&gt;I&amp;#39;m building this primarily to solve my own problems, but I&amp;#39;m curious:&lt;/p&gt; &lt;ol&gt; &lt;li&gt;Do others struggle with similar issues when using RSS readers?&lt;/li&gt; &lt;li&gt;Would a tool like this be useful to anyone else, or am I alone in wanting something like this?&lt;/li&gt; &lt;/ol&gt; &lt;p&gt;I&amp;#39;d really appreciate any thoughts or feedback. Thanks!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Info-Tube-Mario"&gt; /u/Info-Tube-Mario &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fez2d4/seeking_feedback_on_my_aipowered_rss_reader/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fez2d4/seeking_feedback_on_my_aipowered_rss_reader/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fez2d4</id>
    <link href="https://www.reddit.com/r/rss/comments/1fez2d4/seeking_feedback_on_my_aipowered_rss_reader/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Seeking Feedback on My AI-Powered RSS Reader Concept</title>
  </entry>
  <entry>
    <author>
      <name>/u/russell1256</name>
      <uri>https://www.reddit.com/user/russell1256</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Does USA Today have RSS feeds? I cannot find them(or know how to make them).&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/russell1256"&gt; /u/russell1256 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1ff1wfy/usa_today_feeds/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1ff1wfy/usa_today_feeds/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1ff1wfy</id>
    <link href="https://www.reddit.com/r/rss/comments/1ff1wfy/usa_today_feeds/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>USA Today feeds?</title>
  </entry>
  <entry>
    <author>
      <name>/u/ritalin_hum</name>
      <uri>https://www.reddit.com/user/ritalin_hum</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I have sought in vain for an Android RSS reader that fits my use case. I may wind up self hosting at some point in the future, but am I missing an obvious choice?&lt;/p&gt; &lt;p&gt;Here’s my use case: when I travel, I want to download my feeds in full text and read them without an internet connection on long flights.&lt;/p&gt; &lt;p&gt;There is at least one option on iOS (Unread) that would allow for this. Is there such a thing on Android? I see plenty of RSS readers with various levels of UI polish, and some which will fetch full articles if connected at the time of reading. Are there any that will allow me to download articles in full text in advance (even better if it will grab images as well) and cache them for offline reading without an active internet connection? Free or paid, I don’t care. I remember Press would allow this way back in the day but sadly it is no more, and feeds seem to be truncated intentionally more often nowadays which I suppose presents a problem that requires a parser to solve on the modern web.&lt;/p&gt; &lt;p&gt;Readers I have tried: Feeder Read You Twine Feed Me Feedly Pluma (almost there but buggy) …and many others I can no longer recall. Where is this unicorn app?&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/ritalin_hum"&gt; /u/ritalin_hum &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fed0zv/android_rss_with_offline_and_full_article_caching/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fed0zv/android_rss_with_offline_and_full_article_caching/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fed0zv</id>
    <link href="https://www.reddit.com/r/rss/comments/1fed0zv/android_rss_with_offline_and_full_article_caching/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Android RSS with offline and full article caching?</title>
  </entry>
  <entry>
    <author>
      <name>/u/eyal8r</name>
      <uri>https://www.reddit.com/user/eyal8r</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;I am trying to create a collection of news feeds from numerous other feeds. I then want to feed this collection (via RSS url) into an AI Automation to interpret and summarize all the articles inside that feed.&lt;/p&gt; &lt;p&gt;Can FreshRSS (or any other free service) create a collection of rss feeds, and combine it into a single RSS feed output/url?&lt;/p&gt; &lt;p&gt;Thank you!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/eyal8r"&gt; /u/eyal8r &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fejidn/freshrss_or_other_create_new_rss_from_collection/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fejidn/freshrss_or_other_create_new_rss_from_collection/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fejidn</id>
    <link href="https://www.reddit.com/r/rss/comments/1fejidn/freshrss_or_other_create_new_rss_from_collection/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>FreshRSS (or other) - Create New RSS from Collection of other feeds for AI Bot?</title>
  </entry>
  <entry>
    <author>
      <name>/u/wowsuchlinuxkernel</name>
      <uri>https://www.reddit.com/user/wowsuchlinuxkernel</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;A few months ago I read a post somewhere on the internet about some person who felt like their RSS reader was bombarding them with new entries to read, not skimming every single entry was like missing out, it felt like a second inbox next to your email that you had to clear out rather than a place to relax and read interesting stuff. That post really resonated with me. To combat this, they started developing their own RSS reader meant to meet their own needs. And it sounds like their needs overlap with mine. Unfortunately I can&amp;#39;t find that post anymore, does anybody know what I&amp;#39;m talking about?&lt;/p&gt; &lt;p&gt;If you don&amp;#39;t know the post I&amp;#39;m talking about, please share in the comments which RSS reader you&amp;#39;re using and whether you experience the reading as &amp;quot;calm&amp;quot; (whatever that means to you). I know that some readers have the option to disable unread counts on the feeds, but that&amp;#39;s just one piece of the puzzle imho. Does your reader have other features that make the reading experience less demanding?&lt;/p&gt; &lt;p&gt;Thanks!&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/wowsuchlinuxkernel"&gt; /u/wowsuchlinuxkernel &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fe7xar/looking_for_a_calm_rss_reader/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fe7xar/looking_for_a_calm_rss_reader/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fe7xar</id>
    <link href="https://www.reddit.com/r/rss/comments/1fe7xar/looking_for_a_calm_rss_reader/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Looking for a calm RSS reader</title>
  </entry>
  <entry>
    <author>
      <name>/u/llsrnmtkn</name>
      <uri>https://www.reddit.com/user/llsrnmtkn</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;what is their history? I can&amp;#39;t find any info on them and nothing in Wikipedia&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/llsrnmtkn"&gt; /u/llsrnmtkn &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1feinku/who_owns_blogtrottr/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1feinku/who_owns_blogtrottr/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1feinku</id>
    <link href="https://www.reddit.com/r/rss/comments/1feinku/who_owns_blogtrottr/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>Who owns Blogtrottr?</title>
  </entry>
  <entry>
    <author>
      <name>/u/salty-bois</name>
      <uri>https://www.reddit.com/user/salty-bois</uri>
    </author>
    <category term="rss" label="r/rss"/>
    <content type="html">&lt;!-- SC_OFF --&gt;&lt;div class="md"&gt;&lt;p&gt;Hi all,&lt;/p&gt; &lt;p&gt;Trying to figure out the best way to get multiple articles onto my Kindle, currently playing around with Calibre.&lt;/p&gt; &lt;p&gt;Anyway, I&amp;#39;m on a news site, and have the RSS feed showing on Feedly. That just gives me like 10 of the most recent articles.&lt;/p&gt; &lt;p&gt;However, the site has seperate sections - &amp;quot;News&amp;quot;, &amp;quot;Opinion&amp;quot;, &amp;quot;Essays&amp;quot;, &amp;quot;Analysis&amp;quot;, etc. What I want is the &amp;quot;Essays&amp;quot; feed, so that I can send all the essays, going back over a couple of years, to my kindle, without having to send them individually.&lt;/p&gt; &lt;p&gt;I don&amp;#39;t know if there&amp;#39;s a way to see specific sections like this with RSS, or if you just have to accept whatever shows up when you add &amp;quot;/feed&amp;quot; to the end of a site&amp;#39;s address.&lt;/p&gt; &lt;p&gt;Help appreciated!&lt;/p&gt; &lt;p&gt;Thanks.&lt;/p&gt; &lt;/div&gt;&lt;!-- SC_ON --&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/salty-bois"&gt; /u/salty-bois &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fecavk/rss_question_regarding_feeds/"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/rss/comments/1fecavk/rss_question_regarding_feeds/"&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
    <id>t3_1fecavk</id>
    <link href="https://www.reddit.com/r/rss/comments/1fecavk/rss_question_regarding_feeds/"/>
    <updated>{date}</updated>
    <published>{date}</published>
    <title>RSS Question Regarding Feeds</title>
  </entry>
</feed>
""".replace(
    "{date}", DateUtils.get_datetime_now_iso()
)

reddit_entry_json = """
[
  {
    "kind": "Listing",
    "data": {
      "after": null,
      "dist": 1,
      "modhash": "jowsdzzlr71ced4df95d59279ab3f2fb32d773a8b09c7328d8",
      "geo_filter": "",
      "children": [
        {
          "kind": "t3",
          "data": {
            "approved_at_utc": null,
            "subreddit": "webscraping",
            "selftext": "I am a total layman when talking about python or coding in general, but i need to analyze data from reviews in movies social medias for my final paper in History graduation. \n\nAs I need to analyze the reviews, I thought about scraping and using a word2vec model to process the data that i want to use, but I dont know if I can do this with just already made models and codes that I found in the  internet, or if I would need to make something of my own, what I think would be near impossible considering that I'm a total mess in this subjects and I dont have plenty of time because of my part time job as a teacher.\n\nIf anyone knows something, has any advice on what should I do or even considers that it's possible to do what I pretend, please say something, cause I'm feeling a bit lost and I love my research. Drop this theme just because of a technical limitation of mine would be a realy sad thing to happen.\n\nBtw, if any of what I write sound senseless, sorry, I'm brazilian and not used to comunicate in english.\n\n ",
            "user_reports": [],
            "saved": false,
            "mod_reason_title": null,
            "gilded": 0,
            "clicked": false,
            "title": "How to scrape reviews from IMDB or Letterboxd or Rotten?? ",
            "link_flair_richtext": [],
            "subreddit_name_prefixed": "r/webscraping",
            "hidden": false,
            "pwls": 6,
            "link_flair_css_class": null,
            "downs": 0,
            "thumbnail_height": null,
            "top_awarded_type": null,
            "hide_score": false,
            "name": "t3_1hw2l5z",
            "quarantine": false,
            "link_flair_text_color": "dark",
            "upvote_ratio": 0.67,
            "author_flair_background_color": null,
            "subreddit_type": "public",
            "ups": 1,
            "total_awards_received": 0,
            "media_embed": {},
            "thumbnail_width": null,
            "author_flair_template_id": null,
            "is_original_content": false,
            "author_fullname": "t2_5c0i4mceq",
            "secure_media": null,
            "is_reddit_media_domain": false,
            "is_meta": false,
            "category": null,
            "secure_media_embed": {},
            "link_flair_text": null,
            "can_mod_post": false,
            "score": 1,
            "approved_by": null,
            "is_created_from_ads_ui": false,
            "author_premium": false,
            "thumbnail": "self",
            "edited": false,
            "author_flair_css_class": null,
            "author_flair_richtext": [],
            "gildings": {},
            "content_categories": null,
            "is_self": true,
            "mod_note": null,
            "created": 1736285389,
            "link_flair_type": "text",
            "wls": 6,
            "removed_by_category": null,
            "banned_by": null,
            "author_flair_type": "text",
            "domain": "self.webscraping",
            "allow_live_comments": false,
            "selftext_html": "&lt;!-- SC_OFF --&gt;&lt;div class=\"md\"&gt;&lt;p&gt;I am a total layman when talking about python or coding in general, but i need to analyze data from reviews in movies social medias for my final paper in History graduation. &lt;/p&gt;\n\n&lt;p&gt;As I need to analyze the reviews, I thought about scraping and using a word2vec model to process the data that i want to use, but I dont know if I can do this with just already made models and codes that I found in the  internet, or if I would need to make something of my own, what I think would be near impossible considering that I&amp;#39;m a total mess in this subjects and I dont have plenty of time because of my part time job as a teacher.&lt;/p&gt;\n\n&lt;p&gt;If anyone knows something, has any advice on what should I do or even considers that it&amp;#39;s possible to do what I pretend, please say something, cause I&amp;#39;m feeling a bit lost and I love my research. Drop this theme just because of a technical limitation of mine would be a realy sad thing to happen.&lt;/p&gt;\n\n&lt;p&gt;Btw, if any of what I write sound senseless, sorry, I&amp;#39;m brazilian and not used to comunicate in english.&lt;/p&gt;\n&lt;/div&gt;&lt;!-- SC_ON --&gt;",
            "likes": null,
            "suggested_sort": null,
            "banned_at_utc": null,
            "view_count": null,
            "archived": false,
            "no_follow": true,
            "is_crosspostable": true,
            "pinned": false,
            "over_18": false,
            "all_awardings": [],
            "awarders": [],
            "media_only": false,
            "can_gild": false,
            "spoiler": false,
            "locked": false,
            "author_flair_text": null,
            "treatment_tags": [],
            "visited": false,
            "removed_by": null,
            "num_reports": null,
            "distinguished": null,
            "subreddit_id": "t5_318ly",
            "author_is_blocked": false,
            "mod_reason_by": null,
            "removal_reason": null,
            "link_flair_background_color": "",
            "id": "1hw2l5z",
            "is_robot_indexable": true,
            "num_duplicates": 0,
            "report_reasons": null,
            "author": "azhb123",
            "discussion_type": null,
            "num_comments": 0,
            "send_replies": true,
            "media": null,
            "contest_mode": false,
            "author_patreon_flair": false,
            "author_flair_text_color": null,
            "permalink": "/r/webscraping/comments/1hw2l5z/how_to_scrape_reviews_from_imdb_or_letterboxd_or/",
            "stickied": false,
            "url": "https://www.reddit.com/r/webscraping/comments/1hw2l5z/how_to_scrape_reviews_from_imdb_or_letterboxd_or/",
            "subreddit_subscribers": 43636,
            "created_utc": 1736285389,
            "num_crossposts": 0,
            "mod_reports": [],
            "is_video": false
          }
        }
      ],
      "before": null
    }
  },
  {
    "kind": "Listing",
    "data": {
      "after": null,
      "dist": null,
      "modhash": "jowsdzzlr71ced4df95d59279ab3f2fb32d773a8b09c7328d8",
      "geo_filter": "",
      "children": [],
      "before": null
    }
  }
]
"""
