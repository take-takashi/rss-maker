from src.rss_maker.generate_rss import create_audee_rss_file

# --- 設定 ---
# ここにRSSフィードを作成したいAuDeeの番組ページのURLを入力してください
# 例: 伊藤沙莉のsaireek channel
url = "https://audee.jp/program/show/40889"

# 出力するファイル名
output_path = "docs/audee_rss.xml"
# --- 設定ここまで ---

if __name__ == "__main__":
    print(f"AuDee番組ページのRSSフィードを作成します。")
    print(f"URL: {url}")
    print(f"出力先: {output_path}")
    try:
        create_audee_rss_file(url, output_path)
        print("✅ RSSフィードの作成が完了しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
