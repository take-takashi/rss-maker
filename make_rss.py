import sys
import traceback

from src.rss_maker.generate_rss import (
    create_bitfan_updates_rss_file,
    create_jfn_pods_rss_file,
)

# --- 設定 ---
# AuDee は移転予定のため更新停止。
# 既存の docs/audee_rss.xml は公開互換性のため残し、
# 生成処理を再開したい場合は以下を戻す。
# from src.rss_maker.generate_rss import create_audee_rss_file
# audee_url = "https://audee.jp/program/show/40889"
# audee_output_path = "docs/audee_rss.xml"

# 例2: 伊集院光のタネ まとめ聴き（Bitfan）UPDATEページ
bitfan_updates_url = "https://ij-matome.bitfan.id/updates"
bitfan_output_path = "docs/ij_matome_updates_rss.xml"

# 例3: 伊藤沙莉のsaireek channel（JFN Pods ポッドキャスト一覧）
jfn_pods_url = "https://jfn-pods.com/program/40889/voice"
jfn_pods_output_path = "docs/jfn_pods_voice_rss.xml"
# --- 設定ここまで ---

if __name__ == "__main__":
    has_error = False

    # AuDee: サイト移転に伴い更新停止中。
    # 既存の docs/audee_rss.xml は凍結して公開を継続する。
    # print("AuDee番組ページのRSSフィードを作成します。")
    # print(f"URL: {audee_url}")
    # print(f"出力先: {audee_output_path}")
    # try:
    #     create_audee_rss_file(audee_url, audee_output_path)
    #     print("✅ AuDee RSSフィードの作成が完了しました。")
    # except Exception as e:
    #     has_error = True
    #     print(f"AuDee RSS作成中にエラーが発生しました: {e}")
    #     traceback.print_exc()

    # Bitfan: 伊集院光のタネ まとめ聴き（UPDATE）
    print("Bitfan UPDATEページのRSSフィードを作成します。")
    print(f"URL: {bitfan_updates_url}")
    print(f"出力先: {bitfan_output_path}")
    try:
        create_bitfan_updates_rss_file(bitfan_updates_url, bitfan_output_path)
        print("✅ Bitfan RSSフィードの作成が完了しました。")
    except Exception as e:
        has_error = True
        print(f"Bitfan RSS作成中にエラーが発生しました: {e}")
        traceback.print_exc()

    # JFN Pods: saireek channel ポッドキャスト一覧
    print("JFN PodsページのRSSフィードを作成します。")
    print(f"URL: {jfn_pods_url}")
    print(f"出力先: {jfn_pods_output_path}")
    try:
        create_jfn_pods_rss_file(jfn_pods_url, jfn_pods_output_path)
        print("✅ JFN Pods RSSフィードの作成が完了しました。")
    except Exception as e:
        has_error = True
        print(f"JFN Pods RSS作成中にエラーが発生しました: {e}")
        traceback.print_exc()

    if has_error:
        sys.exit(1)
