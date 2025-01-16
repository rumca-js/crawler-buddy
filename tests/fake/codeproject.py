from utils.dateutils import DateUtils


webpage_code_project_rss = """
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>CodeProject Latest News</title>
    <link>https://www.codeproject.com</link>
    <description>Latest News from CodeProject</description>
    <language>en-us</language>
    <image>
      <title>CodeProject Latest News</title>
      <url>https://www.codeproject.com/App_Themes/Std/Img/logo100x30.gif</url>
      <link>https://www.codeproject.com</link>
      <width>100</width>
      <height>30</height>
      <description>CodeProject</description>
    </image>
    <copyright>Copyright  CodeProject, 1999-2023</copyright>
    <webMaster>Webmaster@codeproject.com (Webmaster)</webMaster>
    <lastBuildDate>{}</lastBuildDate>
    <ttl>20</ttl>
    <generator>C# Hand-coded goodness</generator>
    <item>
      <title>Apple is now banned from selling its latest Apple Watches in the US</title>
      <description>Time to start smuggling Apples across the border?</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63692</link>
      <pubDate>{}</pubDate>
      <source url="https://www.theverge.com/2023/12/26/24012382/apple-import-ban-watch-series-9-ultra-2">The Verge</source>
      <category>§Industry News</category>
      <subject>Apple is now banned from selling its latest Apple Watches in the US</subject>
    </item>
    <item>
      <title>Quantum batteries could provide a new kind of energy storage by messing with time</title>
      <description>When in doubt, slap a "quantum" on it. That solves everything.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63693</link>
      <pubDate>{}</pubDate>
      <source url="https://www.sciencealert.com/quantum-batteries-could-provide-a-new-kind-of-energy-storage-by-messing-with-time">Science Alert</source>
      <category>§Science And Technology</category>
      <subject>Quantum batteries could provide a new kind of energy storage by messing with time</subject>
    </item>
    <item>
      <title>How software engineering will evolve in 2024</title>
      <description>File, New &gt; Year</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63694</link>
      <pubDate>{}</pubDate>
      <source url="https://www.infoworld.com/article/3711801/how-software-engineering-will-evolve-in-2024.html">Infoworld</source>
      <category>§Developer News</category>
      <category>#Headliner</category>
      <subject>How software engineering will evolve in 2024</subject>
    </item>
    <item>
      <title>Writing code is the same thing as writing prose</title>
      <description>Once upon a time, there was a variable named 'i'...</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63695</link>
      <pubDate>{}</pubDate>
      <source url="https://www.gybe.ca/writing-code-is-the-same-thing-as-writing-prose/">Michael Hart</source>
      <category>§Developer News</category>
      <subject>Writing code is the same thing as writing prose</subject>
    </item>
    <item>
      <title>Physics, AI and music all share a common thread. You just have to look closely enough</title>
      <description>Something, something, something, quantum!</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63696</link>
      <pubDate>{}</pubDate>
      <source url="https://www.sciencefocus.com/apple-news-ingest/physics-ai-music-common">Science Focus</source>
      <category>§Science And Technology</category>
      <subject>Physics, AI and music all share a common thread. You just have to look closely enough</subject>
    </item>
    <item>
      <title>The eternal struggle between open source and proprietary software</title>
      <description>Many hands make light work, but many eyes don't guarantee fewer bugs</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63697</link>
      <pubDate>{}</pubDate>
      <source url="https://techcrunch.com/2023/12/26/the-eternal-struggle-between-open-source-and-proprietary-software/">Techcrunch</source>
      <category>§Industry News</category>
      <subject>The eternal struggle between open source and proprietary software</subject>
    </item>
    <item>
      <title>Modern C++ programming</title>
      <description>#include &lt;future&gt;</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63698</link>
      <pubDate>{}</pubDate>
      <source url="https://github.com/federico-busato/Modern-CPP-Programming">Federico Busato</source>
      <category>§Developer News</category>
      <subject>Modern C++ programming</subject>
    </item>
    <item>
      <title>Burger King giving discounts if facial recognition thinks you're hungover</title>
      <description>Time for brunch</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63699</link>
      <pubDate>{}</pubDate>
      <source url="https://gizmodo.com/burger-king-giving-discounts-if-facial-recognition-thin-1851124496">Gizmodo</source>
      <category>§Industry News</category>
      <subject>Burger King giving discounts if facial recognition thinks you're hungover</subject>
    </item>
    <item>
      <title>I think Amazon is losing the plot</title>
      <description>People who had that opinion also had this opinion of Amazon...</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63700</link>
      <pubDate>{}</pubDate>
      <source url="https://www.codeproject.com/Messages/5979507/I-think-Amazon-is-losing-the-plot">CodeProject</source>
      <category>§Hot Threads</category>
      <subject>I think Amazon is losing the plot</subject>
    </item>
    <item>
      <title>WebGPU now available for testing in Safari Technology Preview</title>
      <description>WebGPU is a new standards-compliant API that enables high-performance 3D graphics and general-purpose computations on the Web.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63678</link>
      <pubDate>{}</pubDate>
      <source url="https://webkit.org/blog/14879/webgpu-now-available-for-testing-in-safari-technology-preview/">WebKit</source>
      <category>§Tips and Tools</category>
      <subject>WebGPU now available for testing in Safari Technology Preview</subject>
    </item>
    <item>
      <title>Is Blazor the Future of Everything Web?</title>
      <description>In this article we’ll learn how .NET 8 has changed Blazor’s position in the market with features that have modernized and future-proofed the framework for years to come.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63679</link>
      <pubDate>{}</pubDate>
      <source url="https://www.telerik.com/blogs/is-blazor-future-everything-web">Telerik</source>
      <category>§Tips and Tools</category>
      <category>#Headliner</category>
      <subject>Is Blazor the Future of Everything Web?</subject>
    </item>
    <item>
      <title>Did anyone try using smart glasses for writing code?</title>
      <description>Now in 3-D!</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63680</link>
      <pubDate>{}</pubDate>
      <source url="https://www.codeproject.com/Messages/5979276/Did-anyone-try-using-smart-glasses-for-writing-cod">CodeProject</source>
      <category>§Hot Threads</category>
      <subject>Did anyone try using smart glasses for writing code?</subject>
    </item>
    <item>
      <title>I was sent this, and..</title>
      <description>"Bring him home, our wise Odysseus, home at last!"</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63681</link>
      <pubDate>{}</pubDate>
      <source url="https://www.codeproject.com/Messages/5979168/I-was-sent-this-and">CodeProject</source>
      <category>§Hot Threads</category>
      <subject>I was sent this, and..</subject>
    </item>
    <item>
      <title>New AI can predict people’s time of death with high degree of accuracy, study finds</title>
      <description>Especially if it's the one planning your death</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63682</link>
      <pubDate>{}</pubDate>
      <source url="https://www.independent.co.uk/tech/deathbot-ai-predict-life-death-b2466988.html">Independent</source>
      <category>§Science And Technology</category>
      <subject>New AI can predict people’s time of death with high degree of accuracy, study finds</subject>
    </item>
    <item>
      <title>Windows 11 Moment 5 is allegedly coming February 2024</title>
      <description>Just a moment</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63683</link>
      <pubDate>{}</pubDate>
      <source url="https://www.neowin.net/news/windows-11-moment-5-is-allegedly-coming-february-2024/">Neowin</source>
      <category>§Industry News</category>
      <subject>Windows 11 Moment 5 is allegedly coming February 2024</subject>
    </item>
    <item>
      <title>We have used too many levels of abstractions and now the future looks bleak</title>
      <description>Time to bring back realism? Surrealism?</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63684</link>
      <pubDate>{}</pubDate>
      <source url="https://unixsheikh.com/articles/we-have-used-too-many-levels-of-abstractions-and-now-the-future-looks-bleak.html">Unix Sheikh</source>
      <category>§Developer News</category>
      <category>#Headliner</category>
      <subject>We have used too many levels of abstractions and now the future looks bleak</subject>
    </item>
    <item>
      <title>Alternate Futures for “Web Components”</title>
      <description>It seems like Web Components are always just on the cusp of finally catching on.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63685</link>
      <pubDate>{}</pubDate>
      <source url="https://blog.carlana.net/post/2023/web-component-alternative-futures/">The Ethically-Trained Programmer</source>
      <category>§Tips and Tools</category>
      <subject>Alternate Futures for “Web Components”</subject>
    </item>
    <item>
      <title>The 4 metrics every engineering manager should track</title>
      <description>Missing KLoC/fortnight</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63686</link>
      <pubDate>{}</pubDate>
      <source url="https://shiftmag.dev/the-4-metrics-every-engineering-manager-should-track-1329/">Shift magazine</source>
      <category>§Developer News</category>
      <subject>The 4 metrics every engineering manager should track</subject>
    </item>
    <item>
      <title>Microsoft just paid $76 million for a Wisconsin pumpkin farm</title>
      <description>"The Great Pumpkin will appear and I'll be waiting for him!"</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63687</link>
      <pubDate>{}</pubDate>
      <source url="https://www.theverge.com/2023/12/22/24012534/microsoft-wisconsin-pumpkin-farm-foxconn-76-million-mount-pleasant">The Verge</source>
      <category>§Industry News</category>
      <subject>Microsoft just paid $76 million for a Wisconsin pumpkin farm</subject>
    </item>
    <item>
      <title>Google is testing an 'AI support assistant' for questions about Google services</title>
      <description>It just returns, "that's cancelled" for every query</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63688</link>
      <pubDate>{}</pubDate>
      <source url="https://www.androidcentral.com/apps-software/google-ai-support-assistant">Android Central</source>
      <category>§Industry News</category>
      <subject>Google is testing an 'AI support assistant' for questions about Google services</subject>
    </item>
    <item>
      <title>Android malware Chameleon disables Fingerprint Unlock to steal PINs</title>
      <description>Good olde 'password' deemed secure</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63689</link>
      <pubDate>{}</pubDate>
      <source url="https://www.bleepingcomputer.com/news/security/android-malware-chameleon-disables-fingerprint-unlock-to-steal-pins/">Bleeping Computer</source>
      <category>§Industry News</category>
      <subject>Android malware Chameleon disables Fingerprint Unlock to steal PINs</subject>
    </item>
    <item>
      <title>Lawrence Livermore National Lab simulates ‘Armageddon’-style nuclear asteroid deflection</title>
      <description>* Bruce Willis not included</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63690</link>
      <pubDate>{}</pubDate>
      <source url="https://techcrunch.com/2023/12/21/national-lab-simulates-armageddon-style-nuclear-asteroid-deflection/amp/">Techcrunch</source>
      <category>§Science And Technology</category>
      <subject>Lawrence Livermore National Lab simulates ‘Armageddon’-style nuclear asteroid deflection</subject>
    </item>
    <item>
      <title>What’s new in our code coverage tooling?</title>
      <description>"Shut the door and cover me"</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63691</link>
      <pubDate>{}</pubDate>
      <source url="https://devblogs.microsoft.com/dotnet/whats-new-in-our-code-coverage-tooling/">.NET</source>
      <category>§Developer News</category>
      <subject>What’s new in our code coverage tooling?</subject>
    </item>
    <item>
      <title>Auth0 Templates for .NET: A New Powerful Version Released</title>
      <description>A new version of the Auth0 Templates for .NET package has been released: discover the new powerful features.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63668</link>
      <pubDate>{}</pubDate>
      <source url="https://auth0.com/blog/auth0-templates-for-dotnet-powerful-version/">Auth0</source>
      <category>§Tips and Tools</category>
      <subject>Auth0 Templates for .NET: A New Powerful Version Released</subject>
    </item>
    <item>
      <title>v0</title>
      <description>v0 is a generative user interface system by Vercel powered by AI. It generates copy-and-paste friendly React code based on shadcn/ui and Tailwind CSS that people can use in their projects.</description>
      <author>Kent Sharkey</author>
      <link>https://www.codeproject.com/script/News/View.aspx?nwid=63669</link>
      <pubDate>{}</pubDate>
      <source url="https://v0.dev/faq">Vercel</source>
      <category>§Tips and Tools</category>
      <subject>v0</subject>
    </item>
  </channel>
</rss>
""".replace(
    "{}", DateUtils.get_datetime_now_iso()
)
