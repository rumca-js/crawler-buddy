from datetime import datetime
import hashlib

from rsshistory.webtools import RssPage, calculate_hash, RssContentReader

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter
from tests.fakeinternetdata import (
    webpage_no_pubdate_rss,
    webpage_old_pubdate_rss,
)
from tests.fake.youtube import (
    webpage_samtime_youtube_rss,  # you
    youtube_channel_rss_linus_tech_tips,  # uses feed
)
from tests.fake.geekwirecom import (
    geekwire_feed,
)
from tests.fake.warhammercommunity import (
    warhammer_community_rss,
)


webpage_rss = """
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
<channel>
    <title><![CDATA[SAMTIME on Odysee]]></title>
    <subtitle><![CDATA[SAMTIME subtitle]]></subtitle>
    <description><![CDATA[SAMTIME channel description]]></description>
    <link>https://odysee.com/@samtime:1</link>
    <image><url>https://thumbnails.lbry.com/UCd6vEDS3SOhWbXZrxbrf_bw</url>
    <title>SAMTIME on Odysee</title>
    <link>https://odysee.com/@samtime:1</link>
    </image>
    <generator>RSS for Node</generator>
    <lastBuildDate>Tue, 28 Nov 2023 13:57:18 GMT</lastBuildDate>
    <atom:link href="https://odysee.com/$/rss/@samtime:1" rel="self" type="application/rss+xml"/>
    <language><![CDATA[ci]]></language>
    <itunes:author>SAMTIME author</itunes:author><itunes:category text="Leisure"></itunes:category><itunes:image href="https://thumbnails.lbry.com/UCd6vEDS3SOhWbXZrxbrf_bw"/><itunes:owner><itunes:name>SAMTIME name</itunes:name><itunes:email>no-reply@odysee.com</itunes:email></itunes:owner><itunes:explicit>no</itunes:explicit>

    <item><title><![CDATA[First entry title]]></title><description><![CDATA[First entry description]]></description><link>https://odysee.com/youtube-apologises-for-slowing-down:bab8f5ed4fa7bb406264152242bab2558037ee12</link><guid isPermaLink="true">https://odysee.com/youtube-apologises-for-slowing-down:bab8f5ed4fa7bb406264152242bab2558037ee12</guid><pubDate>Mon, 27 Nov 2023 18:50:08 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/youtube-apologises-for-slowing-down/bab8f5ed4fa7bb406264152242bab2558037ee12/1698dc.mp4" length="29028604" type="video/mp4"/><itunes:title>YouTube Apologises For Slowing Down AdBlock Users</itunes:title><itunes:author>SAMTIME x</itunes:author><itunes:image href="https://thumbnails.lbry.com/a51RgbcCutk"/><itunes:duration>161</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[I Installed Android Onto My MacBook]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/WwYo84im3Y0" width="480" alt="thumbnail" title="I Installed Android Onto My MacBook" /></p>Buy UGREEN Nexode 300W Charger ($70 OFF, 11/23-11/27)     https://amzn.to/3FXi6xa<br />UGREEN Nexode 100W Charger   (41% OFF, 11/23-11/27)     https://amzn.to/46oW01m<br />UGREEN Black Friday Deals, Up to 50% OFF    https://amzn.to/3u5gAGo<br />Buy on UGREEN Official Store, Up to 50% OFF    https://bit.ly/47aeWCa<br /><br />I just installed Android onto my wife’s MacBook and… no one is happy.<br /><br />-----------------------------------<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />#Ugreen #UgreenNexode300W<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=WwYo84im3Y0]]></description><link>https://odysee.com/i-installed-android-onto-my-macbook:1975c73f65423692d318b6860950f186277519b9</link><guid isPermaLink="true">https://odysee.com/i-installed-android-onto-my-macbook:1975c73f65423692d318b6860950f186277519b9</guid><pubDate>Fri, 24 Nov 2023 18:00:29 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/i-installed-android-onto-my-macbook/1975c73f65423692d318b6860950f186277519b9/e1f8a4.mp4" length="138220717" type="video/mp4"/><itunes:title>I Installed Android Onto My MacBook</itunes:title><itunes:author>SAMTIME y</itunes:author><itunes:image href="https://thumbnails.lbry.com/WwYo84im3Y0"/><itunes:duration>544</itunes:duration><itunes:explicit>no</itunes:explicit>
    </item><item><title><![CDATA[Apple Reacts to Having to Allow Sideloading]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/RZhVgD2fPZg" width="480" alt="thumbnail" title="Apple Reacts to Having to Allow Sideloading" /></p>Apple will allow iPhone users to install apps from outside their App Store in 2024. Apple ain’t happy about it!<br /><br />Apple Explains Why MacBook Only Has 8GB RAM: https://youtu.be/eKm5-jUTRMM<br /><br />Sideloading Article: https://www.macrumors.com/2023/11/13/eu-iphone-app-sideloading-coming-2024/<br />Craig Federighi Talk: https://www.youtube.com/watch?v=f0Gum8UkyoI<br />Jon Prosser video: https://youtu.be/R1J6Qsi_Fsk?si=rJEnQJpXPw_G5zWb<br />Woman hiding in closet: https://www.reddit.com/r/nightvale/comments/x1whrl/homeless_woman_lived_in_a_mans_closet_for_a_year/<br /><br />-----------------------------------<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />#iPhoneSideloading #DigitalMarketsAct #UnhappyApple<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=RZhVgD2fPZg]]></description><link>https://odysee.com/apple-reacts-to-having-to-allow:c1c7e8b36c1519e260e81ca7b71dc855e8c4a480</link><guid isPermaLink="true">https://odysee.com/apple-reacts-to-having-to-allow:c1c7e8b36c1519e260e81ca7b71dc855e8c4a480</guid><pubDate>Wed, 22 Nov 2023 19:52:19 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/apple-reacts-to-having-to-allow/c1c7e8b36c1519e260e81ca7b71dc855e8c4a480/64b55b.mp4" length="53821224" type="video/mp4"/><itunes:title>Apple Reacts to Having to Allow Sideloading</itunes:title><itunes:author>SAMTIME 1</itunes:author><itunes:image href="https://thumbnails.lbry.com/RZhVgD2fPZg"/><itunes:duration>206</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Apple Responds to Crackling iPhone 15 Speaker]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/z06e9QMd60U" width="480" alt="thumbnail" title="Apple Responds to Crackling iPhone 15 Speaker" /></p>Turns out there's another iPhone 15 problem. This time with a rattling earpiece speaker. Now this isn't music to Apple's ears XD<br /><br />MORE iPhone 15 Issues Playlist: https://www.youtube.com/playlist?list=PLHSLJI8oVymwR_Zx8zi_0Ao2iSGSXuytu<br /><br />ARTICLE: https://9to5mac.com/2023/10/03/iphone-15-crackling-sound-speakers/<br /><br />Angry Redditor Clips are Boogie2988: https://www.youtube.com/watch?v=Kwo58m4JqY8<br /><br />-----------------------------------<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=z06e9QMd60U]]></description><link>https://odysee.com/apple-responds-to-crackling-iphone-15:483c58ed5d701eed5622e223803b0736d7cb9c80</link><guid isPermaLink="true">https://odysee.com/apple-responds-to-crackling-iphone-15:483c58ed5d701eed5622e223803b0736d7cb9c80</guid><pubDate>Mon, 20 Nov 2023 18:00:35 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/apple-responds-to-crackling-iphone-15/483c58ed5d701eed5622e223803b0736d7cb9c80/e2cad7.mp4" length="44287318" type="video/mp4"/><itunes:title>Apple Responds to Crackling iPhone 15 Speaker</itunes:title><itunes:author>SAMTIME 2</itunes:author><itunes:image href="https://thumbnails.lbry.com/z06e9QMd60U"/><itunes:duration>181</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[I’m Switching to Windows - GEEKOM Mini IT13]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/6WJyze7WntA" width="480" alt="thumbnail" title="I’m Switching to Windows - GEEKOM Mini IT13" /></p>GEEKOM Mini IT13 USA Official:   https://bit.ly/3qTXFgy<br />US$40 off coupon code:      SAMTIMEIT13<br /><br />GEEKOM Mini IT13 USA Amazon:   https://amzn.to/3skwSe2<br />US$40 off coupon code:   SAMTIMEIT13<br /><br />GEEKOM Mini IT13 UK Official:  https://bit.ly/44yt9Xd<br />£40 off coupon code:    SAMTIMEIT13<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=6WJyze7WntA]]></description><link>https://odysee.com/i%E2%80%99m-switching-to-windows-geekom-mini:b933d8ef9b31522a9210f15d65ef33ca80882901</link><guid isPermaLink="true">https://odysee.com/i%E2%80%99m-switching-to-windows-geekom-mini:b933d8ef9b31522a9210f15d65ef33ca80882901</guid><pubDate>Fri, 17 Nov 2023 18:03:35 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/i’m-switching-to-windows-geekom-mini/b933d8ef9b31522a9210f15d65ef33ca80882901/e3e6cf.mp4" length="156934832" type="video/mp4"/><itunes:title>I’m Switching to Windows - GEEKOM Mini IT13</itunes:title><itunes:author>SAMTIME 3</itunes:author><itunes:image href="https://thumbnails.lbry.com/6WJyze7WntA"/><itunes:duration>503</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Apple Explains Why MacBook Pro Only Has 8GB RAM]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/eKm5-jUTRMM" width="480" alt="thumbnail" title="Apple Explains Why MacBook Pro Only Has 8GB RAM" /></p>Apple used their reality distortion field to explain why 8GB RAM on the new MacBook Pro is actually as good as 16GB.<br /><br />ARTICLE: https://www.macrumors.com/2023/11/08/8gb-ram-m3-macbook-pro-like-16-gb-pc/<br /><br />Max Tech 8GB vs 16GB MacBook Pro Test: https://youtu.be/hmWPd7uEYEY?si=pUzg-KFlhXvYoJKb<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />#MacBookPro #MacBookProBlem<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=eKm5-jUTRMM]]></description><link>https://odysee.com/apple-explains-why-macbook-pro-only-has:cf8f2d2c724a2e2dea05cc9e7b819f926d5acc52</link><guid isPermaLink="true">https://odysee.com/apple-explains-why-macbook-pro-only-has:cf8f2d2c724a2e2dea05cc9e7b819f926d5acc52</guid><pubDate>Wed, 15 Nov 2023 19:27:30 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/apple-explains-why-macbook-pro-only-has/cf8f2d2c724a2e2dea05cc9e7b819f926d5acc52/da9c24.mp4" length="45292390" type="video/mp4"/><itunes:title>Apple Explains Why MacBook Pro Only Has 8GB RAM</itunes:title><itunes:author>SAMTIME 4</itunes:author><itunes:image href="https://thumbnails.lbry.com/eKm5-jUTRMM"/><itunes:duration>227</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[YouTube is Sorry for Banning AdBlock]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/M_2Sh700w_E" width="480" alt="thumbnail" title="YouTube is Sorry for Banning AdBlock" /></p>YouTube is very sorry that they banned AdBlockers… because it made AdBlockers much more powerful!<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />#YouTube #AdBlock #SadBlock<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=M_2Sh700w_E]]></description><link>https://odysee.com/youtube-is-sorry-for-banning-adblock:61f2c4f92c36c76d7e8caf6a26123e79bf0d49eb</link><guid isPermaLink="true">https://odysee.com/youtube-is-sorry-for-banning-adblock:61f2c4f92c36c76d7e8caf6a26123e79bf0d49eb</guid><pubDate>Mon, 13 Nov 2023 17:00:25 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/youtube-is-sorry-for-banning-adblock/61f2c4f92c36c76d7e8caf6a26123e79bf0d49eb/532a85.mp4" length="49293717" type="video/mp4"/><itunes:title>YouTube is Sorry for Banning AdBlock</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/M_2Sh700w_E"/><itunes:duration>174</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[I Try to Fix My Old MacBook]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/l1kCgKwU4Cs" width="480" alt="thumbnail" title="I Try to Fix My Old MacBook" /></p>Get genuine parts to fix your Apple MacBook at https://appleparts.io/<br />Use codeword SAMTIME to get 20% at checkout!!<br /><br />How To Fix Your MacBook Pro on the Cheap: https://youtu.be/C0o5BrBSUSM<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=l1kCgKwU4Cs]]></description><link>https://odysee.com/i-try-to-fix-my-old-macbook:2dd51a62e201d54aa7ce0436e58e20de14f3ddf8</link><guid isPermaLink="true">https://odysee.com/i-try-to-fix-my-old-macbook:2dd51a62e201d54aa7ce0436e58e20de14f3ddf8</guid><pubDate>Thu, 09 Nov 2023 17:24:49 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/i-try-to-fix-my-old-macbook/2dd51a62e201d54aa7ce0436e58e20de14f3ddf8/5bd2d1.mp4" length="181789747" type="video/mp4"/><itunes:title>I Try to Fix My Old MacBook</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/l1kCgKwU4Cs"/><itunes:duration>586</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Tim Cook Finally Answers Hard Questions]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/BeHs9eGzsB8" width="480" alt="thumbnail" title="Tim Cook Finally Answers Hard Questions" /></p>I sat down with Tim Cook to finally make him answer the hard questions<br /><br />MORE INTERVIEWS: https://www.youtube.com/playlist?list=PLHSLJI8oVymzqoJi-_RQGI2K55QqF2ZxI<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />#TimCook #TimApple #TheHardQuestions<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=BeHs9eGzsB8]]></description><link>https://odysee.com/tim-cook-finally-answers-hard-questions:9e8ac9f2879e81ebb07c82e3d6f6795a75fa9451</link><guid isPermaLink="true">https://odysee.com/tim-cook-finally-answers-hard-questions:9e8ac9f2879e81ebb07c82e3d6f6795a75fa9451</guid><pubDate>Tue, 07 Nov 2023 18:32:03 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/tim-cook-finally-answers-hard-questions/9e8ac9f2879e81ebb07c82e3d6f6795a75fa9451/c6c463.mp4" length="65672356" type="video/mp4"/><itunes:title>Tim Cook Finally Answers Hard Questions</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/BeHs9eGzsB8"/><itunes:duration>271</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[M3 MacBook Pro PARODY - “Taking out the Pro”]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/Z5HkmZp-96k" width="480" alt="thumbnail" title="M3 MacBook Pro PARODY - “Taking out the Pro”" /></p>Introducing the all new Apple M3 MacBook Pros. Now available without the “Pro”!!<br /><br />Microsoft Reacts to Apple's New MacBooks: https://youtu.be/dhnozZ_rVJY<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=Z5HkmZp-96k]]></description><link>https://odysee.com/m3-macbook-pro-parody-%E2%80%9Ctaking-out-the:b9b024a3871cc7ba70d46818cd8530917ba6bbde</link><guid isPermaLink="true">https://odysee.com/m3-macbook-pro-parody-%E2%80%9Ctaking-out-the:b9b024a3871cc7ba70d46818cd8530917ba6bbde</guid><pubDate>Tue, 31 Oct 2023 18:44:28 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/m3-macbook-pro-parody-“taking-out-the/b9b024a3871cc7ba70d46818cd8530917ba6bbde/cf42ab.mp4" length="32870166" type="video/mp4"/><itunes:title>M3 MacBook Pro PARODY - “Taking out the Pro”</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/Z5HkmZp-96k"/><itunes:duration>198</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Mac User Installs Windows Vista for First Time]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/I1_f05-lBz4" width="480" alt="thumbnail" title="Mac User Installs Windows Vista for First Time" /></p>Try out the incredible new AI video editing features from @FilmoraWondershare and download Filmora 13 today! <br />Use SENGWF49 to download Filmora with $$ off ⬇️<br />Desktop: https://bit.ly/3Fz76Wl<br />mobile📱: https://bit.ly/3Qa0cMh<br /><br />#Filmora13 #MadewithFilmora<br /><br />Real Apple Mac user installs Windows Vista on his MacBook. It hurt a little!<br />Mac User Installs ARCH LINUX for First Time: https://youtu.be/GDq_S0WlfgU<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=I1_f05-lBz4]]></description><link>https://odysee.com/mac-user-installs-windows-vista-for:52ed55e0b74c77b2ae48709e3f296613067d4e85</link><guid isPermaLink="true">https://odysee.com/mac-user-installs-windows-vista-for:52ed55e0b74c77b2ae48709e3f296613067d4e85</guid><pubDate>Mon, 30 Oct 2023 18:12:19 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/mac-user-installs-windows-vista-for/52ed55e0b74c77b2ae48709e3f296613067d4e85/8211ab.mp4" length="131494194" type="video/mp4"/><itunes:title>Mac User Installs Windows Vista for First Time</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/I1_f05-lBz4"/><itunes:duration>579</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Microsoft Reacts to Apple’s New MacBooks]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/dhnozZ_rVJY" width="480" alt="thumbnail" title="Microsoft Reacts to Apple’s New MacBooks" /></p>Microsoft just bluescreened over Apple’s upcoming M3 MacBook Pros.<br /><br />Subscribe for the Apple M3 event PARODY VIDEO coming this Wednesday!<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=dhnozZ_rVJY]]></description><link>https://odysee.com/microsoft-reacts-to-apple%E2%80%99s-new:95165fbe1687d85ce7e697c652723db677d3d5bd</link><guid isPermaLink="true">https://odysee.com/microsoft-reacts-to-apple%E2%80%99s-new:95165fbe1687d85ce7e697c652723db677d3d5bd</guid><pubDate>Mon, 30 Oct 2023 09:00:10 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/microsoft-reacts-to-apple’s-new/95165fbe1687d85ce7e697c652723db677d3d5bd/e019a6.mp4" length="35376274" type="video/mp4"/><itunes:title>Microsoft Reacts to Apple’s New MacBooks</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/dhnozZ_rVJY"/><itunes:duration>161</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Samsung Reacts to OnePlus Folding Phone]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/heZoeirmqgw" width="480" alt="thumbnail" title="Samsung Reacts to OnePlus Folding Phone" /></p>Samsung responds to the new OnePlus Open folding phone. They’re not impressed!<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=heZoeirmqgw]]></description><link>https://odysee.com/samsung-reacts-to-oneplus-folding-phone:1b185b09135e7ed38965642f0f95f2b26e6331ae</link><guid isPermaLink="true">https://odysee.com/samsung-reacts-to-oneplus-folding-phone:1b185b09135e7ed38965642f0f95f2b26e6331ae</guid><pubDate>Tue, 24 Oct 2023 17:11:56 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/samsung-reacts-to-oneplus-folding-phone/1b185b09135e7ed38965642f0f95f2b26e6331ae/04d025.mp4" length="46183132" type="video/mp4"/><itunes:title>Samsung Reacts to OnePlus Folding Phone</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/heZoeirmqgw"/><itunes:duration>184</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Apple Introduces Apple Pencil With a Cord]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/-1yi7DqDUr8" width="480" alt="thumbnail" title="Apple Introduces Apple Pencil With a Cord" /></p>Apple just introduced the Apple Pencil USB-C. For when wireless charging is just too dang convenient!<br /><br />Yes, this is a real product: https://www.apple.com/shop/product/MUWA3AM/A/apple-pencil-usb-c<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=-1yi7DqDUr8]]></description><link>https://odysee.com/apple-introduces-apple-pencil-with-a:36a5fad1b47e74d2795b7bb33cf084917089fd76</link><guid isPermaLink="true">https://odysee.com/apple-introduces-apple-pencil-with-a:36a5fad1b47e74d2795b7bb33cf084917089fd76</guid><pubDate>Thu, 19 Oct 2023 17:56:02 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/apple-introduces-apple-pencil-with-a/36a5fad1b47e74d2795b7bb33cf084917089fd76/dc4d47.mp4" length="30185132" type="video/mp4"/><itunes:title>Apple Introduces Apple Pencil With a Cord</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/-1yi7DqDUr8"/><itunes:duration>196</itunes:duration><itunes:explicit>no</itunes:explicit></item>
    <item><title><![CDATA[Apple Responds to iPhone 15 Screen Burn In]]></title><description><![CDATA[<p><img src="https://thumbnails.lbry.com/CVUMiyl1GVY" width="480" alt="thumbnail" title="Apple Responds to iPhone 15 Screen Burn In" /></p>Apple responds to the screen burn-in issue on the new iPhone 15 Pro Max. Looks like the phone is turning into an iPhone 15 PROblems!<br /><br />ARTICLE: https://www.dailymail.co.uk/sciencetech/article-12636027/iPhone-15-Pro-Max-screen-burn-issues-image-display-Apple.html<br /><br />Apple Responds to iPhone 15 Pro Bending: https://youtu.be/va9NjxmoyJU<br />Apple Responds to iPhone 15 Pro Overheating: https://youtu.be/75bxg24Od_U<br />Apple Responds to Fine Woven Case Issue: https://youtu.be/eMEahWU4mrM<br /><br />-----------------------------------<br /><br />SUPPORT: https://funkytime.tv/patriot-signup/<br />MERCH: https://funkytime.tv/shop/<br />FUNKY TIME WEBSITE: https://funkytime.tv<br /><br />FACEBOOK: http://www.facebook.com/SamtimeNews<br />TWITTER: http://twitter.com/SamtimeNews<br />INSTAGRAM: http://instagram.com/samtimenews<br /><br />-----------------------------------<br /><br />'Escape the ordinary. Embrace the FUNKY!'<br /><br />-----------------------------------<br /><br />For sponsorship enquiries: samtime@bossmgmtgrp.com<br />For other business enquiries: business@funkytime.tv<br />Copyright FUNKY TIME PRODUCTIONS 2023<br />...<br />https://www.youtube.com/watch?v=CVUMiyl1GVY]]></description><link>https://odysee.com/apple-responds-to-iphone-15-screen-burn:dc3690d028b73fb0026d0610dda41531844d2342</link><guid isPermaLink="true">https://odysee.com/apple-responds-to-iphone-15-screen-burn:dc3690d028b73fb0026d0610dda41531844d2342</guid><pubDate>Tue, 17 Oct 2023 17:40:04 GMT</pubDate><enclosure url="https://player.odycdn.com/api/v3/streams/free/apple-responds-to-iphone-15-screen-burn/dc3690d028b73fb0026d0610dda41531844d2342/0ef216.mp4" length="31056471" type="video/mp4"/><itunes:title>Apple Responds to iPhone 15 Screen Burn In</itunes:title><itunes:author>SAMTIME</itunes:author><itunes:image href="https://thumbnails.lbry.com/CVUMiyl1GVY"/><itunes:duration>147</itunes:duration><itunes:explicit>no</itunes:explicit></item>
</channel>
</rss>
"""


class RssPageTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_title__rss(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)

        # call tested function
        self.assertEqual(reader.get_title(), "SAMTIME on Odysee")
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_title__youtube(self):
        # default language
        reader = RssPage(
            "https://linkedin.com/test", youtube_channel_rss_linus_tech_tips
        )
        self.assertEqual(reader.get_title(), "Linus Tech Tips")
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_description(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)

        # call tested function
        self.assertEqual(reader.get_description(), "SAMTIME channel description")

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_language(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)

        # call tested function
        self.assertEqual(reader.get_language(), "ci")
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_thumbnail(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)

        # call tested function
        self.assertEqual(
            reader.get_thumbnail(),
            "https://thumbnails.lbry.com/UCd6vEDS3SOhWbXZrxbrf_bw",
        )
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_author(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)

        # call tested function
        self.assertEqual(reader.get_author(), "SAMTIME author")
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_entries(self):
        reader = RssPage("https://linkedin.com/test", webpage_rss)
        entries = reader.get_entries()
        entries = list(entries)
        self.assertEqual(len(entries), 15)

        entry = entries[0]
        # call tested function
        self.assertEqual(entry["title"], "First entry title")
        self.assertEqual(entry["description"], "First entry description")
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_entry_old_date(self):
        # default language
        reader = RssPage("https://linkedin.com/test", webpage_old_pubdate_rss)
        entries = reader.get_entries()
        entries = list(entries)
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry["title"], "First entry title")
        self.assertEqual(entry["description"], "First entry description")
        self.assertEqual(entry["date_published"].year, 2020)
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_entry_no_date(self):
        reader = RssPage("https://linkedin.com/test", webpage_no_pubdate_rss)
        entries = reader.get_entries()
        entries = list(entries)

        self.assertEqual(len(entries), 1)

        current_date_time = datetime.now()

        entry = entries[0]
        # call tested function
        self.assertEqual(entry["title"], "First entry title")
        self.assertEqual(entry["description"], "First entry description")
        self.assertEqual(entry["date_published"].year, current_date_time.year)
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_entry_page_rating(self):
        reader = RssPage("https://linkedin.com/test", webpage_no_pubdate_rss)
        entries = reader.get_entries()
        entries = list(entries)

        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertTrue(entry["page_rating"] > 0)

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_valid__true_youtube(self):
        reader = RssPage("https://linkedin.com/test", webpage_samtime_youtube_rss)
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_valid__true(self):
        reader = RssPage("https://linkedin.com/test", webpage_old_pubdate_rss)
        entries = reader.get_entries()

        # call tested function
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_valid__geek_false(self):
        reader = RssPage("https://linkedin.com/test", geekwire_feed)
        entries = reader.get_entries()

        # call tested function
        self.assertFalse(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_is_valid__warhammer_true(self):
        reader = RssPage("https://linkedin.com/test", warhammer_community_rss)
        entries = reader.get_entries()

        # call tested function
        self.assertTrue(reader.is_valid())

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    def test_get_contents_body_hash(self):
        # default language
        reader = RssPage("https://linkedin.com/test", webpage_old_pubdate_rss)

        # call tested function
        hash = reader.get_contents_body_hash()

        entries = str(reader.feed.entries)

        self.assertTrue(entries)
        self.assertTrue(entries != "")
        self.assertEqual(hash, calculate_hash(entries))

        self.assertEqual(MockRequestCounter.mock_page_requests, 0)

    """
    feeder does not parses update time
    def test_rss_old_pubdate(self):
        url = RssPage("https://youtube.com/channel/2020-year-channel/rss.xml")
        date = url.get_date_published()

        self.assertTrue(date)
        self.assertEqual(date.year, 2020)

    def test_rss_no_pubdate(self):
        url = RssPage("https://youtube.com/channel/no-pubdate-channel/rss.xml")
        date = url.get_date_published()

        self.assertTrue(not date)
    """


class RssContentReaderTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_init(self):
        reader = RssContentReader("https://youtube.com", geekwire_feed)

        self.assertTrue(reader.contents.find("<?xml") >= 0)
        self.assertTrue(reader.contents.find("</rss>") >= 0)
