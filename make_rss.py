from src.rss_maker.generate_rss import (
    create_audee_rss_file,
    create_bitfan_updates_rss_file,
)

# --- 設定 ---
# ここにRSSフィードを作成したいAuDeeの番組ページのURLを入力してください
# 例1: 伊藤沙莉のsaireek channel（AuDee）
audee_url = "https://audee.jp/program/show/40889"
audee_output_path = "docs/audee_rss.xml"

# 例2: 伊集院光のタネ まとめ聴き（Bitfan）UPDATEページ
bitfan_updates_url = "https://ij-matome.bitfan.id/updates"
bitfan_output_path = "docs/ij_matome_updates_rss.xml"
# --- 設定ここまで ---

if __name__ == "__main__":
    # AuDee: saireek channel
    print("AuDee番組ページのRSSフィードを作成します。")
    print(f"URL: {audee_url}")
    print(f"出力先: {audee_output_path}")
    try:
        create_audee_rss_file(audee_url, audee_output_path)
        print("✅ AuDee RSSフィードの作成が完了しました。")
    except Exception as e:
        print(f"AuDee RSS作成中にエラーが発生しました: {e}")

    # Bitfan: 伊集院光のタネ まとめ聴き（UPDATE）
    print("Bitfan UPDATEページのRSSフィードを作成します。")
    print(f"URL: {bitfan_updates_url}")
    print(f"出力先: {bitfan_output_path}")
    try:
        create_bitfan_updates_rss_file(bitfan_updates_url, bitfan_output_path)
        print("✅ Bitfan RSSフィードの作成が完了しました。")
    except Exception as e:
        print(f"Bitfan RSS作成中にエラーが発生しました: {e}")
