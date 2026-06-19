from scraper.cleaner import clean_html


def test_clean_html_removes_script_tags():
    html = "<html><head><script>var x=1;</script></head><body><p>Hello</p></body></html>"
    assert clean_html(html) == "Hello"
