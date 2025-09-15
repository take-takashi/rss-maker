import pytest
import requests
from pathlib import Path
import xml.etree.ElementTree as ET
from rss_maker.generate_rss import (
    get_html,
    parse_articles_from_audee_page,
    generate_rss_feed,
    create_audee_rss_file,
)


# テストフィクスチャとして、テスト用のHTMLファイルを読み込む
@pytest.fixture
def audee_page_html():
    path = Path(__file__).parent.parent / "fixtures" / "audee_program_page.html"
    return path.read_text(encoding="utf-8")


def test_get_html_successfully(mocker):
    """
    指定したURLからHTMLを正常に取得できる場合のテスト
    """
    # --- Arrange ---
    target_url = "https://example.com"
    expected_html = "<html><body><h1>Test Page</h1></body></html>"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = expected_html
    mock_get = mocker.patch(
        "rss_maker.generate_rss.requests.get", return_value=mock_response
    )

    # --- Act ---
    actual_html = get_html(target_url)

    # --- Assert ---
    mock_get.assert_called_once_with(target_url)
    assert actual_html == expected_html


def test_get_html_raises_http_error(mocker):
    """
    HTTPエラーが発生した場合に例外を送出することを確認するテスト
    """
    # --- Arrange ---
    target_url = "https://example.com/notfound"
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_get = mocker.patch(
        "rss_maker.generate_rss.requests.get", return_value=mock_response
    )

    # --- Act & Assert ---
    with pytest.raises(requests.exceptions.HTTPError):
        get_html(target_url)

    mock_get.assert_called_once_with(target_url)


def test_parse_articles_from_audee_page(audee_page_html):
    """
    AuDeeの番組ページHTMLから記事リストを正しく抽出できるかのテスト
    """
    # --- Act ---
    articles = parse_articles_from_audee_page(audee_page_html)

    # --- Assert ---
    assert len(articles) == 9
    first_article = articles[0]
    assert (
        first_article["title"]
        == "（本当に？）いつもよりテンション低めでお送りするサイリークメッセージ読みたおし！vol.195"
    )
    assert first_article["url"] == "https://audee.jp/voice/show/108553"
    assert (
        first_article["thumbnail"]
        == "https://cf.audee.jp/contents/9ruSPlMHU7_thumb.jpg"
    )


def test_generate_rss_feed():
    """
    記事リストからRSSフィードが正しく生成されるかのテスト
    """
    # --- Arrange ---
    channel_info = {
        "title": "Test Channel",
        "link": "https://example.com/channel",
        "description": "This is a test channel.",
    }
    articles = [
        {
            "title": "Article 1",
            "url": "https://example.com/article1",
            "thumbnail": "https://example.com/thumb1.jpg",
        },
        {
            "title": "Article 2",
            "url": "https://example.com/article2",
            "thumbnail": "https://example.com/thumb2.jpg",
        },
    ]

    # --- Act ---
    rss_xml = generate_rss_feed(channel_info, articles)

    # --- Assert ---
    root = ET.fromstring(rss_xml)
    assert root.tag == "rss"
    channel = root.find("channel")
    assert channel is not None

    title_element = channel.find("title")
    assert title_element is not None
    assert title_element.text == channel_info["title"]

    items = channel.findall("item")
    assert len(items) == len(articles)
    first_item = items[0]

    first_title_element = first_item.find("title")
    assert first_title_element is not None
    assert first_title_element.text == articles[0]["title"]

    enclosure = first_item.find("enclosure")
    assert enclosure is not None
    assert enclosure.attrib["url"] == articles[0]["thumbnail"]


def test_create_audee_rss_file(mocker, audee_page_html):
    """
    一連の処理を実行し、最終的にRSSファイルが作成されることをテストする
    """
    # --- Arrange ---
    target_url = "https://audee.jp/program/show/40889"
    output_path = "/tmp/test_feed.xml"

    # get_htmlをモック化
    mocker.patch("rss_maker.generate_rss.get_html", return_value=audee_page_html)

    # openをモック化
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # --- Act ---
    create_audee_rss_file(target_url, output_path)

    # --- Assert ---
    mock_open.assert_called_once_with(output_path, "w", encoding="utf-8")

    written_content = mock_open().write.call_args[0][0]

    root = ET.fromstring(written_content)
    channel = root.find("channel")
    assert channel is not None

    title_element = channel.find("title")
    assert title_element is not None
    assert (
        title_element.text == "伊藤沙莉のsaireek channel|伊藤沙莉|AuDee（オーディー）"
    )
    assert len(channel.findall("item")) == 9
