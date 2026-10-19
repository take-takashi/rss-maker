# rss-maker
RSSが提供されていないサイトでRSSを自作したい

## `mise`のセットアップ

```bash
rss-maker % cat <<EOF > mise.toml
[tools]
python = "3.13"

[env]
_.python.venv = { path = ".venv", create = true }
SAMPLE = "Hello, sample!"
EOF
rss-maker % mise trust
# install uv
rss-maker % mise exec -- pip install uv
rss-maker % uv --version
uv 0.8.3 (7e78f54e7 2025-07-24)
```

## project setup

```bash
rss-maker % uv init --no-cache --lib
```

## package install

```bash
rss-maker % uv add requests==2.32.4
rss-maker % uv add beautifulsoup4==4.13.4
rss-maker % uv add feedgenerator==2.2.0
rss-maker % uv add pytest --dev
rss-maker % uv add pyright --dev
```


## フィードの運用状態（2026-10）

- **Bitfan（伊集院光のタネ）**: GitHub Actionsで日次更新。
- **JFN Pods（saireek channel）**: 2026-09-25以降、取得先のHTTP 403で更新失敗するため一時停止中（`make_rss.py` の `ENABLE_JFN_PODS = False`）。
- **AuDee**: 以前から生成停止中。
- `docs/` の既存XMLは削除しない。停止中も過去の取得結果を残す。
- JFN Podsの再開時は取得先のアクセス可否とパーサーを検証し、`ENABLE_JFN_PODS = True` に戻す。

### 動作確認

```bash
uv sync
uv run pytest
uv run python make_rss.py
```

`make_rss.py` を直接実行すると `docs/` のBitfan RSSを書き換えるため、実行後は差分を確認する。

### リポジトリを残してRSSの定期生成・公開を一時停止する

1. まずJFN Pods停止の修正をmainにマージする。
2. [Generate and Publish RSS](https://github.com/take-takashi/rss-maker/actions/workflows/publish.yml) の **Run workflow** で実行し、生成ジョブが成功し、BitfanのXML更新が反映されたことを確認する。
3. 同じワークフローのメニューから **Disable workflow** を選択する（定期実行・手動実行を無効化）。
4. [Settings → Pages](https://github.com/take-takashi/rss-maker/settings/pages) で **Unpublish site** を選択し、公開サイトを取り下げる。

**注意**: `Unpublish site` は現在のPagesデプロイを取り下げるだけで、リポジトリやXMLを削除しない。公開リポジトリにあるXMLはGitHubのRaw URLから引き続き参照できる。Pagesは新たなデプロイが発生すると再公開され得るため、先に定期実行を無効化しておくこと。

### 再開するとき

1. 必要ならJFN PodsのHTTP 403を解消し、`ENABLE_JFN_PODS` を `True` に変更する。未解消なら `False` のままBitfanのみで再開可能。
2. 上記GitHub Actionsワークフローの **Enable workflow** を選択する。
3. **Run workflow** で生成成功を確認する。
4. Pagesが再公開されていなければ、[Settings → Pages](https://github.com/take-takashi/rss-maker/settings/pages) の公開元設定を確認し、公開元ブランチへのコミット等で新しいPagesデプロイを作成する。
5. RSS URLの取得・最終更新日を確認する。
