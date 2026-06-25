
def v_info(request):
    id = request.args.get("id")
    if not configuration.is_allowed(id):
        return get_html(id=id, body="Cannot access this view", title="Error")

    text = """
    <h1>Crawlers</h1>
    """

    text += get_crawler_text()

    text += "<h2>Default user agent</h2>"
    text += "<div>Default user agent:{}</div>".format(
        webtools.crawlers.default_user_agent
    )

    text += "<h2>Default headers</h2>"
    for key, value in webtools.crawlers.default_headers.items():
        text += "<div>{}:{}</div>".format(key, value)

    text += "<h2>Data</h2>"
    for key, value in configuration.data.items():
        text += "<div>{}:{}</div>".format(key, value)

    return get_html(id=id, body=text, title="Configuration")
