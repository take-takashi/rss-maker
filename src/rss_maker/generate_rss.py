import requests
from bs4 import BeautifulSoup
import feedgenerator

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
            href = link_tag.get('href')
            if isinstance(href, str):
                # URLはドメインからの絶対パスではない場合があるので、完全なURLに組み立てる
                url = href
                if not url.startswith('http'):
                    url = f"https://audee.jp{url}"
                
                articles.append({
                    "title": title_tag.get_text(strip=True),
                    "url": url,
                    "thumbnail": img_tag["data-original"],
                })
    return articles

def generate_rss_feed(channel_info: dict, articles: list[dict]) -> str:
    """チャンネル情報と記事リストからRSSフィードを生成します。"""
    feed = feedgenerator.Rss201rev2Feed(
        title=channel_info["title"],
        link=channel_info["link"],
        description=channel_info["description"],
    )

    for article in articles:
        feed.add_item(
            title=article["title"],
            link=article["url"],
            description="",  # 概要は今回利用しない
            enclosures=[
                feedgenerator.Enclosure(url=article["thumbnail"], length="0", mime_type="image/jpeg"),
            ]
        )
    
    return feed.writeString('utf-8')

import xml.dom.minidom

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
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)