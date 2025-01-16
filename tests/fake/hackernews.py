from utils.dateutils import DateUtils

webpage_hackernews_rss = """
<rss version="2.0">
	<channel>
		<title>Hacker News: Front Page</title>
		<link>https://news.ycombinator.com/</link>
		<description>Hacker News RSS</description>
		<docs>https://hnrss.org/</docs>
		<generator>hnrss v2.1.1</generator>
		<lastBuildDate>Fri, 05 Apr 2024 12:15:37 +0000</lastBuildDate>
		<atom:link href="https://hnrss.org/frontpage" rel="self" type="application/rss+xml"/>
		<item>
			<title>
Deepnote (YC S19) is hiring engineers to build a better Jupyter notebook
</title>
			<description>
				<p>Article URL: 
					<a href="https://deepnote.com/join-us">https://deepnote.com/join-us</a>
				</p>
				<p>Comments URL: 
					<a href="https://news.ycombinator.com/item?id=39941303">https://news.ycombinator.com/item?id=39941303</a>
				</p>
				<p>Points: 0</p>
				<p># Comments: 0</p>
			</description>
			<pubDate>{date}</pubDate>
			<link>https://deepnote.com/join-us</link>
			<dc:creator>Equiet</dc:creator>
			<comments>https://news.ycombinator.com/item?id=39941303</comments>
			<guid isPermaLink="false">https://news.ycombinator.com/item?id=39941303</guid>
		</item>
		<item>
			<title>
Almost no one cares if your site is not on social media
</title>
			<description>
				<p>Article URL: 
					<a href="https://notes.ghed.in/posts/2024/no-one-cares-site-on-social-media/">https://notes.ghed.in/posts/2024/no-one-cares-site-on-social-media/</a>
				</p>
				<p>Comments URL: 
					<a href="https://news.ycombinator.com/item?id=39940922">https://news.ycombinator.com/item?id=39940922</a>
				</p>
				<p>Points: 16</p>
				<p># Comments: 2</p>
			</description>
			<pubDate>{date}</pubDate>
			<link>
https://notes.ghed.in/posts/2024/no-one-cares-site-on-social-media/
</link>
			<dc:creator>rpgbr</dc:creator>
			<comments>https://news.ycombinator.com/item?id=39940922</comments>
			<guid isPermaLink="false">https://news.ycombinator.com/item?id=39940922</guid>
		</item>
		<item>
			<title>
Infrastructure as Code Is Not the Answer – By Luke Shaughnessy
</title>
			<description>
				<p>Article URL: 
					<a href="https://lukeshaughnessy.medium.com/infrastructure-as-code-is-not-the-answer-cfaf4882dcba">https://lukeshaughnessy.medium.com/infrastructure-as-code-is-not-the-answer-cfaf4882dcba</a>
				</p>
				<p>Comments URL: 
					<a href="https://news.ycombinator.com/item?id=39940707">https://news.ycombinator.com/item?id=39940707</a>
				</p>
				<p>Points: 12</p>
				<p># Comments: 11</p>
			</description>
			<pubDate>{date}</pubDate>
			<link>
https://lukeshaughnessy.medium.com/infrastructure-as-code-is-not-the-answer-cfaf4882dcba
</link>
			<dc:creator>scapecast</dc:creator>
			<comments>https://news.ycombinator.com/item?id=39940707</comments>
			<guid isPermaLink="false">https://news.ycombinator.com/item?id=39940707</guid>
		</item>
		<item>
			<title>
Ask HN: I want to put free WiFi in schools in my city, how do I go about it?
</title>
			<description>
				<p>I want to put Wifi in the schools. I wanted to know the technical and equipment requirements and the best way to approach it. I am considering 2 approaches.
					<p>1) Standalone for each school This is perhaps the simpler approach, just put a one strong setup at every school. I would need a splash login page where the student would log in with their student ID and password. The average enrollment at the schools is about 1k, and the area of each school is about a 500 meter radius.
						<p>2) Citywide approach With this one, the major difference is that the students will be able to login at any school in the city, similar to the edu network in the US
							<p>What sort of infrastructure would i need for one school with reliable strength? Any recommendations for actual equipment? What is the price estimate/range for one school in the first approach? Are there any companies that already exist that offer this solution including the login stuff as well?
								<p>What would be the extra requirements to go from standalone setups to the citywide approach?</p>
								<hr>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39940541">https://news.ycombinator.com/item?id=39940541</a>
									</p>
									<p>Points: 17</p>
									<p># Comments: 14</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://news.ycombinator.com/item?id=39940541</link>
								<dc:creator>chirau</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39940541</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39940541</guid>
							</item>
							<item>
								<title>
Proton Mail says Outlook for Windows is Microsoft's new data collection service
</title>
								<description>
									<p>Article URL: 
										<a href="https://www.ghacks.net/2024/01/12/proton-mail-says-that-the-new-outlook-app-for-windows-is-microsofts-new-data-collection-service/">https://www.ghacks.net/2024/01/12/proton-mail-says-that-the-new-outlook-app-for-windows-is-microsofts-new-data-collection-service/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39939363">https://news.ycombinator.com/item?id=39939363</a>
									</p>
									<p>Points: 85</p>
									<p># Comments: 37</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://www.ghacks.net/2024/01/12/proton-mail-says-that-the-new-outlook-app-for-windows-is-microsofts-new-data-collection-service/
</link>
								<dc:creator>quantified</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39939363</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39939363</guid>
							</item>
							<item>
								<title>FFmpeg 7.0 Released</title>
								<description>
									<p>Article URL: 
										<a href="https://ffmpeg.org//index.html#pr7.0">https://ffmpeg.org//index.html#pr7.0</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938703">https://news.ycombinator.com/item?id=39938703</a>
									</p>
									<p>Points: 260</p>
									<p># Comments: 76</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://ffmpeg.org//index.html#pr7.0</link>
								<dc:creator>gyan</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938703</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938703</guid>
							</item>
							<item>
								<title>She slept with a violin on her pillow</title>
								<description>
									<p>Article URL: 
										<a href="https://www.nytimes.com/2024/04/04/arts/violin-italy-antonio-stradivari-ayoung-an.html">https://www.nytimes.com/2024/04/04/arts/violin-italy-antonio-stradivari-ayoung-an.html</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938452">https://news.ycombinator.com/item?id=39938452</a>
									</p>
									<p>Points: 64</p>
									<p># Comments: 56</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://www.nytimes.com/2024/04/04/arts/violin-italy-antonio-stradivari-ayoung-an.html
</link>
								<dc:creator>tintinnabula</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938452</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938452</guid>
							</item>
							<item>
								<title>Google Books Is Indexing AI-Generated Garbage</title>
								<description>
									<p>Article URL: 
										<a href="https://www.404media.co/google-books-is-indexing-ai-generated-garbage/">https://www.404media.co/google-books-is-indexing-ai-generated-garbage/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938126">https://news.ycombinator.com/item?id=39938126</a>
									</p>
									<p>Points: 66</p>
									<p># Comments: 33</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://www.404media.co/google-books-is-indexing-ai-generated-garbage/
</link>
								<dc:creator>marban</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938126</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938126</guid>
							</item>
							<item>
								<title>KDE1 on Debian 13</title>
								<description>
									<p>Article URL: 
										<a href="https://ariasft.github.io/">https://ariasft.github.io/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938125">https://news.ycombinator.com/item?id=39938125</a>
									</p>
									<p>Points: 37</p>
									<p># Comments: 6</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://ariasft.github.io/</link>
								<dc:creator>indigodaddy</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938125</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938125</guid>
							</item>
							<item>
								<title>OpenBSD 7.5 Released</title>
								<description>
									<p>Article URL: 
										<a href="https://www.openbsd.org/75.html">https://www.openbsd.org/75.html</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938072">https://news.ycombinator.com/item?id=39938072</a>
									</p>
									<p>Points: 159</p>
									<p># Comments: 21</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://www.openbsd.org/75.html</link>
								<dc:creator>SoftTalker</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938072</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938072</guid>
							</item>
							<item>
								<title>
Former University of Iowa hospital employee used fake identity for 35 years
</title>
								<description>
									<p>Article URL: 
										<a href="https://www.thegazette.com/crime-courts/former-university-of-iowa-hospital-employee-used-fake-identity-for-35-years/">https://www.thegazette.com/crime-courts/former-university-of-iowa-hospital-employee-used-fake-identity-for-35-years/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39938005">https://news.ycombinator.com/item?id=39938005</a>
									</p>
									<p>Points: 218</p>
									<p># Comments: 212</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://www.thegazette.com/crime-courts/former-university-of-iowa-hospital-employee-used-fake-identity-for-35-years/
</link>
								<dc:creator>Georgelemental</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39938005</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39938005</guid>
							</item>
							<item>
								<title>C++ coroutines do not spark joy (2021)</title>
								<description>
									<p>Article URL: 
										<a href="https://probablydance.com/2021/10/31/c-coroutines-do-not-spark-joy/">https://probablydance.com/2021/10/31/c-coroutines-do-not-spark-joy/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39937762">https://news.ycombinator.com/item?id=39937762</a>
									</p>
									<p>Points: 47</p>
									<p># Comments: 34</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://probablydance.com/2021/10/31/c-coroutines-do-not-spark-joy/
</link>
								<dc:creator>signa11</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39937762</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39937762</guid>
							</item>
							<item>
								<title>Xr0: C but Safe</title>
								<description>
									<p>Article URL: 
										<a href="https://xr0.dev/">https://xr0.dev/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39936291">https://news.ycombinator.com/item?id=39936291</a>
									</p>
									<p>Points: 117</p>
									<p># Comments: 94</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://xr0.dev/</link>
								<dc:creator>synergy20</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39936291</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39936291</guid>
							</item>
							<item>
								<title>Mario meets Pareto</title>
								<description>
									<p>Article URL: 
										<a href="https://www.mayerowitz.io/blog/mario-meets-pareto">https://www.mayerowitz.io/blog/mario-meets-pareto</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39936246">https://news.ycombinator.com/item?id=39936246</a>
									</p>
									<p>Points: 1096</p>
									<p># Comments: 116</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://www.mayerowitz.io/blog/mario-meets-pareto</link>
								<dc:creator>superMayo</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39936246</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39936246</guid>
							</item>
							<item>
								<title>Tool Use (function calling)</title>
								<description>
									<p>Article URL: 
										<a href="https://docs.anthropic.com/claude/docs/tool-use">https://docs.anthropic.com/claude/docs/tool-use</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39936048">https://news.ycombinator.com/item?id=39936048</a>
									</p>
									<p>Points: 147</p>
									<p># Comments: 47</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://docs.anthropic.com/claude/docs/tool-use</link>
								<dc:creator>akadeb</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39936048</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39936048</guid>
							</item>
							<item>
								<title>
Language models as compilers: Simulating pseudocode execution
</title>
								<description>
									<p>Article URL: 
										<a href="https://arxiv.org/abs/2404.02575">https://arxiv.org/abs/2404.02575</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39934956">https://news.ycombinator.com/item?id=39934956</a>
									</p>
									<p>Points: 145</p>
									<p># Comments: 43</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://arxiv.org/abs/2404.02575</link>
								<dc:creator>milliondreams</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39934956</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39934956</guid>
							</item>
							<item>
								<title>
Understanding and managing the impact of machine learning models on the web
</title>
								<description>
									<p>Article URL: 
										<a href="https://www.w3.org/reports/ai-web-impact/">https://www.w3.org/reports/ai-web-impact/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39934584">https://news.ycombinator.com/item?id=39934584</a>
									</p>
									<p>Points: 108</p>
									<p># Comments: 25</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://www.w3.org/reports/ai-web-impact/</link>
								<dc:creator>kaycebasques</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39934584</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39934584</guid>
							</item>
							<item>
								<title>The design philosophy of Great Tables</title>
								<description>
									<p>Article URL: 
										<a href="https://posit-dev.github.io/great-tables/blog/design-philosophy/">https://posit-dev.github.io/great-tables/blog/design-philosophy/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39933833">https://news.ycombinator.com/item?id=39933833</a>
									</p>
									<p>Points: 416</p>
									<p># Comments: 73</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://posit-dev.github.io/great-tables/blog/design-philosophy/
</link>
								<dc:creator>randyzwitch</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39933833</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39933833</guid>
							</item>
							<item>
								<title>XDP for game programmers</title>
								<description>
									<p>Article URL: 
										<a href="https://mas-bandwidth.com/xdp-for-game-programmers/">https://mas-bandwidth.com/xdp-for-game-programmers/</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39933660">https://news.ycombinator.com/item?id=39933660</a>
									</p>
									<p>Points: 80</p>
									<p># Comments: 67</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>
https://mas-bandwidth.com/xdp-for-game-programmers/
</link>
								<dc:creator>gafferongames</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39933660</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39933660</guid>
							</item>
							<item>
								<title>
JetMoE: Reaching LLaMA2 performance with 0.1M dollars
</title>
								<description>
									<p>Article URL: 
										<a href="https://research.myshell.ai/jetmoe">https://research.myshell.ai/jetmoe</a>
									</p>
									<p>Comments URL: 
										<a href="https://news.ycombinator.com/item?id=39933076">https://news.ycombinator.com/item?id=39933076</a>
									</p>
									<p>Points: 240</p>
									<p># Comments: 84</p>
								</description>
								<pubDate>{date}</pubDate>
								<link>https://research.myshell.ai/jetmoe</link>
								<dc:creator>gyre007</dc:creator>
								<comments>https://news.ycombinator.com/item?id=39933076</comments>
								<guid isPermaLink="false">https://news.ycombinator.com/item?id=39933076</guid>
							</item>
						</channel>
					</rss>
""".replace(
    "{date}", DateUtils.get_datetime_now_iso()
)


hacker_news_item = """
{
  "by" : "Aissen",
  "descendants" : 18,
  "id" : 42728015,
  "kids" : [ 42728465, 42729529, 42730235, 42729635, 42729995, 42728975, 42730347, 42728406, 42728327 ],
  "score" : 93,
  "time" : 1737047587,
  "title" : "GitHub Linux ARM64 hosted runners now available for free in public repositories",
  "type" : "story",
  "url" : "https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/"
}
"""
