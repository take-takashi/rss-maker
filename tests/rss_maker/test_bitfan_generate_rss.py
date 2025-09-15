import xml.etree.ElementTree as ET
from pathlib import Path

from rss_maker.generate_rss import (
    generate_rss_feed,
    parse_articles_from_bitfan_updates_page,
    parse_channel_info_from_bitfan_updates_page,
)


def load_fixture() -> str:
    path = Path(__file__).parent.parent / "fixtures" / "ij-matome_program_page.html"
    return path.read_text(encoding="utf-8")


def test_parse_articles_from_bitfan_updates_page_scoped_to_club_section():
    html = load_fixture()
    base_url = "https://ij-matome.bitfan.id/updates"

    articles = parse_articles_from_bitfan_updates_page(html, base_url)

    # 期待件数（p-clubSection内の contents へのリンク数）
    assert len(articles) == 12

    first = articles[0]
    assert first["url"] == "https://ij-matome.bitfan.id/contents/301773"
    assert (
        first["thumbnail"]
        == "https://bitfan-id.s3.ap-northeast-1.amazonaws.com/store/935a56bf1608a8f58948884898390a24.jpg"
    )
    assert first["title"] == (
        "第401回～第404回 2025年9月9日～9月12日放送『70.ファミコンメモリー』"
        "『117.夏の推し麺』『114.復活希望』『37.鉄道マニアに言わせれば』"
    )


def test_generate_rss_feed_from_bitfan_parsed_data():
    html = load_fixture()
    base_url = "https://ij-matome.bitfan.id/updates"
    channel = parse_channel_info_from_bitfan_updates_page(html)
    channel["link"] = base_url
    articles = parse_articles_from_bitfan_updates_page(html, base_url)

    rss_xml = generate_rss_feed(channel, articles)
    root = ET.fromstring(rss_xml)
    assert root.tag == "rss"
    channel_el = root.find("channel")
    assert channel_el is not None
    assert channel_el.find("title") is not None
    items = channel_el.findall("item")
    assert len(items) == len(articles)
