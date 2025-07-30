# rss-maker
RSSが提供されていないサイトでRSSを自作したい

## `mise`のセットアップ

```bash
takashi@Mac rss-maker % cat <<EOF > mise.toml
[tools]
python = "3.13"

[env]
_.python.venv = { path = ".venv", create = true }
SAMPLE = "Hello, sample!"
EOF
takashi@Mac rss-maker % mise trust
# install uv
takashi@Mac rss-maker % mise exec -- pip install uv
takashi@Mac rss-maker % uv --version
uv 0.8.3 (7e78f54e7 2025-07-24)
```

## project setup

```bash
(.venv) takashi@Mac rss-maker % uv init --no-cache --lib
```

## package install

```bash
(.venv) takashi@Mac rss-maker % uv add requests==2.32.4
(.venv) takashi@Mac rss-maker % uv add beautifulsoup4==4.13.4
(.venv) takashi@Mac rss-maker % uv add feedgenerator==2.2.0
```
