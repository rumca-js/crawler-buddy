"""
Yt-dlp crawler implementation.
@note works only for youtube contents!

https://github.com/yt-dlp/yt-dlp
"""
from webtoolkit import (
    CrawlerInterface,
    PageResponseObject,
    HTTP_STATUS_UNKNOWN,
    HTTP_STATUS_OK,
    HTTP_STATUS_USER_AGENT,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
    HTTP_STATUS_CODE_CONNECTION_ERROR,
    HTTP_STATUS_CODE_TIMEOUT,
    HTTP_STATUS_CODE_FILE_TOO_BIG,
    HTTP_STATUS_CODE_PAGE_UNSUPPORTED,
    HTTP_STATUS_CODE_SERVER_ERROR,
)


class YtdlpCrawler(CrawlerInterface):
    """
    yt-dlp crawler implementation
    """

    def run(self):
        """
        Run crawler
        """
        from utils.programwrappers import ytdlp

        self.response = PageResponseObject(
            self.request.url,
            text=None,
            status_code=HTTP_STATUS_CODE_SERVER_ERROR,
            request_url=self.request.url,
        )

        yt = ytdlp.YTDLP(self.request.url)
        text = yt.download_data()

        headers = {}

        if yt.is_valid():
            headers["Content-Type"] = "text/json"

            self.response = PageResponseObject(
                url=self.request.url,
                text=yt.stdout,
                status_code=200 + yt.returncode,
                encoding="utf-8",
                headers=headers,
                binary=None,
                request_url=self.request.url,
            )
        else:
            headers["Content-Type"] = "text"

            self.response = PageResponseObject(
                url=self.request.url,
                text=str(yt.stdout) + " " + str(self.stderr),
                status_code=400 + yt.returncode,
                encoding="utf-8",
                headers=headers,
                binary=None,
                request_url=self.request.url,
            )

        return self.response

    def is_valid(self) -> bool:
        """
        Returns indication if crawler is available
        """
        try:
            from utils.programwrappers import ytdlp
            return True
        except Exception as E:
            return False
