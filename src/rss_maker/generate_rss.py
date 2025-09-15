from __future__ import annotations

import xml.dom.minidom
from typing import List, Mapping, NotRequired, Optional, Required, Sequence, TypedDict
from urllib.parse import urljoin

import feedgenerator  # type: ignore[reportMissingTypeStubs]
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class ChannelInfoBase(TypedDict):
    title: str
    description: str


class ChannelInfo(ChannelInfoBase):
    link: str


class Article(TypedDict):
    title: Required[str]
    url: Required[str]
    thumbnail: Required[Optional[str]]
    description: NotRequired[str]


def _attr_to_str(val: object) -> Optional[str]:
    """BeautifulSoupの属性値（str or list[str]など）を安全にstrへ正規化する。"""
    if isinstance(val, list):
        return "".join(str(x) for x in val)
    if isinstance(val, str):
        return val
    return None


def get_html(url: str) -> str:
    """指定されたURLからHTMLコンテンツを取得します。"""
    response = requests.get(url)
    response.raise_for_status()  # エラーがあれば例外を発生させる
    return response.text


def parse_channel_info_from_audee_page(html: str) -> ChannelInfoBase:
    """AuDeeの番組ページHTMLからチャンネル情報を抽出します。"""
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("meta[property='og:title']")
    description_tag = soup.select_one("meta[name='description']")

    title_val = title_tag.get("content") if title_tag else "タイトル不明"
    desc_val = description_tag.get("content") if description_tag else "概要不明"

    # beautifulsoupの型定義により、contentがリストを返す可能性があるため、文字列に変換
    title = "".join(title_val) if isinstance(title_val, list) else str(title_val)
    description = "".join(desc_val) if isinstance(desc_val, list) else str(desc_val)

    return {
        "title": title,
        "description": description.strip(),
    }


def parse_articles_from_audee_page(html: str) -> List[Article]:
    """AuDeeの番組ページHTMLから記事リストを抽出します。"""
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Article] = []
    # 「コンテンツ一覧」の中の「すべて」タブのセクションに限定して検索
    content_section = soup.select_one("#content_tab_all")
    if not content_section:
        return []

    # CSSセレクタで記事要素をすべて取得
    for item in content_section.select(".box-article-item"):
        link_tag = item.select_one("a")
        img_tag = item.select_one("a img.lazy")
        title_tag = item.select_one("a p.txt-article")

        if not (
            isinstance(link_tag, Tag)
            and isinstance(img_tag, Tag)
            and isinstance(title_tag, Tag)
        ):
            continue

        href = _attr_to_str(link_tag.get("href"))
        thumb_val = _attr_to_str(img_tag.get("data-original"))
        title_text = title_tag.get_text(strip=True)
        if not (href and title_text):
            continue
        url = href
        if not url.startswith("http"):
            url = f"https://audee.jp{url}"

        art: Article = {"title": title_text, "url": url, "thumbnail": thumb_val}
        articles.append(art)
    return articles


def generate_rss_feed(
    channel_info: Mapping[str, object],
    articles: Sequence[Mapping[str, object]],
) -> str:
    """チャンネル情報と記事リストからRSSフィードを生成します。"""
    # 値型を厳密に縛らないが、実際には文字列で運用する
    title = str(channel_info["title"])  # type: ignore[index]
    link = str(channel_info["link"])  # type: ignore[index]
    description = str(channel_info["description"])  # type: ignore[index]
    feed = feedgenerator.Rss201rev2Feed(title=title, link=link, description=description)

    for article in articles:
        enclosures: List[object] = []
        thumb_obj = article.get("thumbnail")
        thumb = str(thumb_obj) if isinstance(thumb_obj, str) else None
        if thumb:
            enclosures = [
                feedgenerator.Enclosure(url=thumb, length="0", mime_type="image/jpeg")
            ]
        item_title = str(article["title"])  # type: ignore[index]
        item_link = str(article["url"])  # type: ignore[index]
        desc_obj = article.get("description")
        item_desc = str(desc_obj) if isinstance(desc_obj, str) else ""
        feed.add_item(
            title=item_title,
            link=item_link,
            description=item_desc,
            enclosures=enclosures,
        )

    return feed.writeString("utf-8")


def create_audee_rss_file(url: str, output_path: str) -> None:
    """AuDeeの番組ページのRSSフィードを作成し、ファイルに保存します。"""
    html = get_html(url)

    base_info = parse_channel_info_from_audee_page(html)
    channel_info: ChannelInfo = {
        "title": base_info["title"],
        "description": base_info["description"],
        "link": url,
    }

    articles = parse_articles_from_audee_page(html)
    rss_xml = generate_rss_feed(channel_info, articles)

    # 生成されたXMLを整形する
    dom = xml.dom.minidom.parseString(rss_xml)
    pretty_xml = dom.toprettyxml(indent="  ")
    # 空白行を削除
    pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)


# ---------------- Bitfan (伊集院光のタネ まとめ聴き) ----------------
def parse_channel_info_from_bitfan_updates_page(html: str) -> ChannelInfoBase:
    """Bitfanの更新ページHTMLからチャンネル情報を抽出します。"""
    soup = BeautifulSoup(html, "html.parser")

    # タイトルと説明はogタグ or 通常のmetaから取得
    title_tag = soup.select_one("meta[property='og:title']") or soup.find("title")
    desc_tag = soup.select_one("meta[property='og:description']") or soup.select_one(
        "meta[name='description']"
    )

    if isinstance(title_tag, Tag):
        raw_title = (
            title_tag.get("content")
            if title_tag.has_attr("content")
            else title_tag.string
        )
    else:
        raw_title = "タイトル不明"

    if isinstance(desc_tag, Tag):
        raw_desc = desc_tag.get("content") if desc_tag.has_attr("content") else ""
    else:
        raw_desc = ""

    title = _attr_to_str(raw_title) or str(raw_title or "")
    description = _attr_to_str(raw_desc) or str(raw_desc or "")

    return {
        "title": title.strip() if title else "タイトル不明",
        "description": description.strip(),
    }


def parse_articles_from_bitfan_updates_page(html: str, base_url: str) -> List[Article]:
    """Bitfanの更新ページHTMLから記事リストを抽出します。

    対象は `section.p-clubSection` 配下のみ。各アイテムは
    `a.p-clubMedia__inner[href*="/contents/"]` を記事として扱います。
    タイトルは `.p-clubMedia__name` のテキスト（NEW等のラベル除去）、
    サムネイルは `.p-clubMedia__icon img[src]` を使用します。
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Article] = []

    container = soup.select_one("section.p-clubSection")
    if not container:
        return []

    seen: set[str] = set()
    for a in container.select("a.p-clubMedia__inner[href*='/contents/']"):
        if not isinstance(a, Tag):
            continue
        href_raw = _attr_to_str(a.get("href"))
        if not href_raw:
            continue
        abs_url = urljoin(base_url, href_raw)
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # タイトル抽出（NEWラベルなどのspanは除去）
        name_tag = a.select_one(".p-clubMedia__name")
        title = ""
        if isinstance(name_tag, Tag):
            for span in name_tag.find_all("span"):
                span.decompose()
            title = name_tag.get_text(strip=True)
        if not title:
            # フォールバック：アンカー全体のテキスト
            title = a.get_text(strip=True)

        # サムネイル
        thumb_url: Optional[str] = None
        img_tag = a.select_one(".p-clubMedia__icon img[src]")
        if not isinstance(img_tag, Tag):
            img_tag = a.find("img")
        if isinstance(img_tag, Tag):
            src_val = _attr_to_str(img_tag.get("src"))
            if src_val:
                thumb_url = urljoin(base_url, src_val)

        art: Article = {"title": title, "url": abs_url, "thumbnail": thumb_url}
        articles.append(art)

    return articles


def create_bitfan_updates_rss_file(url: str, output_path: str) -> None:
    """Bitfanの更新ページからRSSフィードを作成し、ファイルに保存します。"""
    html = get_html(url)

    base_info = parse_channel_info_from_bitfan_updates_page(html)
    channel_info: ChannelInfo = {
        "title": base_info["title"],
        "description": base_info["description"],
        "link": url,
    }

    articles = parse_articles_from_bitfan_updates_page(html, base_url=url)
    rss_xml = generate_rss_feed(channel_info, articles)

    # 生成されたXMLを整形する
    dom = xml.dom.minidom.parseString(rss_xml)
    pretty_xml = dom.toprettyxml(indent="  ")
    # 空白行を削除
    pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
