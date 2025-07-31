import requests
from bs4 import BeautifulSoup
import feedgenerator

def get_html(url: str) -> str:
    """指定されたURLからHTMLコンテンツを取得します。"""
    response = requests.get(url)
    response.raise_for_status()  # エラーがあれば例外を発生させる
    return response.text

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

def create_audee_rss_file(url: str, output_path: str):
    """AuDeeの番組ページのRSSフィードを作成し、ファイルに保存します。"""
    html = get_html(url)
    
    # TODO: HTMLから動的にチャンネル情報を取得する
    channel_info = {
        "title": "伊藤沙莉のsaireek channel",
        "link": url,
        "description": "俳優、伊藤沙莉によるラジオ番組「saireek channel」の非公式RSSフィードです。"
    }

    articles = parse_articles_from_audee_page(html)
    rss_xml = generate_rss_feed(channel_info, articles)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rss_xml)

