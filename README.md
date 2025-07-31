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
