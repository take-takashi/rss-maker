import xml.dom.minidom
from urllib.parse import urljoin

import feedgenerator
import requests
from bs4 import BeautifulSoup


def get_html(url: str) -> str:
    """指定されたURLからHTMLコンテンツを取得します。"""
    response = requests.get(url)
    response.raise_for_status()  # エラーがあれば例外を発生させる
    return response.text


def parse_channel_info_from_audee_page(html: str) -> dict:
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


def parse_articles_from_audee_page(html: str) -> list[dict]:
    """AuDeeの番組ページHTMLから記事リストを抽出します。"""
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    # 「コンテンツ一覧」の中の「すべて」タブのセクションに限定して検索
    content_section = soup.select_one("#content_tab_all")
    if not content_section:
        return []

    # CSSセレクタで記事要素をすべて取得
    for item in content_section.select(".box-article-item"):
        link_tag = item.select_one("a")
        img_tag = item.select_one("a img.lazy")
        title_tag = item.select_one("a p.txt-article")

        if link_tag and img_tag and title_tag:
            href = link_tag.get("href")
            if isinstance(href, str):
                # URLはドメインからの絶対パスではない場合があるので、完全なURLに組み立てる
                url = href
                if not url.startswith("http"):
                    url = f"https://audee.jp{url}"

                articles.append(
                    {
                        "title": title_tag.get_text(strip=True),
                        "url": url,
                        "thumbnail": img_tag["data-original"],
                    }
                )
    return articles


def generate_rss_feed(channel_info: dict, articles: list[dict]) -> str:
    """チャンネル情報と記事リストからRSSフィードを生成します。"""
    feed = feedgenerator.Rss201rev2Feed(
        title=channel_info["title"],
        link=channel_info["link"],
        description=channel_info["description"],
    )

    for article in articles:
        enclosures = []
        thumb = article.get("thumbnail")
        if thumb:
            enclosures = [
                feedgenerator.Enclosure(url=thumb, length="0", mime_type="image/jpeg"),
            ]
        feed.add_item(
            title=article["title"],
            link=article["url"],
            description=article.get("description", ""),
            enclosures=enclosures,
        )

    return feed.writeString("utf-8")


def create_audee_rss_file(url: str, output_path: str):
    """AuDeeの番組ページのRSSフィードを作成し、ファイルに保存します。"""
    html = get_html(url)

    channel_info = parse_channel_info_from_audee_page(html)
    channel_info["link"] = url

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
def parse_channel_info_from_bitfan_updates_page(html: str) -> dict:
    """Bitfanの更新ページHTMLからチャンネル情報を抽出します。"""
    soup = BeautifulSoup(html, "html.parser")

    # タイトルと説明はogタグ or 通常のmetaから取得
    title_tag = soup.select_one("meta[property='og:title']") or soup.find("title")
    desc_tag = soup.select_one("meta[property='og:description']") or soup.select_one(
        "meta[name='description']"
    )

    raw_title = (
        title_tag.get("content")
        if title_tag and title_tag.has_attr("content")
        else title_tag.string
        if title_tag
        else "タイトル不明"
    )
    raw_desc = (
        desc_tag.get("content") if desc_tag and desc_tag.has_attr("content") else ""
    )
    title = "".join(raw_title) if isinstance(raw_title, list) else str(raw_title)
    description = "".join(raw_desc) if isinstance(raw_desc, list) else str(raw_desc)

    return {
        "title": title.strip() if title else "タイトル不明",
        "description": description.strip(),
    }


def parse_articles_from_bitfan_updates_page(html: str, base_url: str) -> list[dict]:
    """Bitfanの更新ページHTMLから記事リストを抽出します。

    対象は `section.p-clubSection` 配下のみ。各アイテムは
    `a.p-clubMedia__inner[href*="/contents/"]` を記事として扱います。
    タイトルは `.p-clubMedia__name` のテキスト（NEW等のラベル除去）、
    サムネイルは `.p-clubMedia__icon img[src]` を使用します。
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: list[dict] = []

    container = soup.select_one("section.p-clubSection")
    if not container:
        return []

    seen = set()
    for a in container.select("a.p-clubMedia__inner[href*='/contents/']"):
        href = a.get("href")
        if not href:
            continue
        abs_url = urljoin(base_url, href)
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # タイトル抽出（NEWラベルなどのspanは除去）
        name_tag = a.select_one(".p-clubMedia__name")
        title = ""
        if name_tag:
            for span in name_tag.find_all("span"):
                span.decompose()
            title = name_tag.get_text(strip=True)
        if not title:
            # フォールバック：アンカー全体のテキスト
            title = a.get_text(strip=True)

        # サムネイル
        img = a.select_one(".p-clubMedia__icon img[src]") or a.find("img")
        thumb = img.get("src") if img and img.has_attr("src") else None
        if thumb:
            thumb = urljoin(base_url, thumb)

        articles.append(
            {
                "title": title,
                "url": abs_url,
                "thumbnail": thumb,
            }
        )

    return articles


def create_bitfan_updates_rss_file(url: str, output_path: str):
    """Bitfanの更新ページからRSSフィードを作成し、ファイルに保存します。"""
    html = get_html(url)

    channel_info = parse_channel_info_from_bitfan_updates_page(html)
    channel_info["link"] = url

    articles = parse_articles_from_bitfan_updates_page(html, base_url=url)
    rss_xml = generate_rss_feed(channel_info, articles)

    # 生成されたXMLを整形する
    dom = xml.dom.minidom.parseString(rss_xml)
    pretty_xml = dom.toprettyxml(indent="  ")
    # 空白行を削除
    pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
