# Kevin起業家VLOG

AI・起業・経営戦略についての情報を発信するブログです。YouTube風のデザインを採用し、テック系起業家向けのコンテンツを提供しています。

## 機能

- YouTube風のデザイン
- カテゴリー別の色分け表示
- おすすめ動画セクション
- プロフィールページ
- レスポンシブデザイン
- AI記事自動生成（GitHub Actions）

## Vercelへのデプロイ

### 1. GitHubへプッシュ

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Vercelでインポート

1. [Vercel](https://vercel.com)にログイン
2. 「Import Project」をクリック
3. GitHubリポジトリを選択
4. 自動的にビルド設定が検出されます
5. 「Deploy」をクリック

## ローカル開発

### 必要な環境
- Ruby 2.6以上
- Bundler

### セットアップ

```bash
# 依存関係をインストール
bundle install

# 開発サーバーを起動
bundle exec jekyll serve --livereload
```

ブラウザで `http://localhost:4000` にアクセス

### 2. GitHub Secretsの設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定:

- `OPENAI_API_KEY`: OpenAI APIキー

### 3. ローカルでのテスト

```bash
# Python依存関係のインストール
pip install -r requirements.txt

# 環境変数を設定してスクリプトを実行
export OPENAI_API_KEY="your-api-key-here"
python scripts/generate_post.py
```

### 4. Jekyllの起動

```bash
# ローカルでJekyllを起動
bundle exec jekyll serve --drafts

# ブラウザで確認
open http://localhost:4000
```

## ワークフロー

1. **自動生成**: 毎朝5時にGitHub Actionsが起動し、3記事を生成
2. **レビュー**: Pull Requestが自動作成されるので内容を確認
3. **編集**: 必要に応じて記事を修正
4. **公開**: 公開したい記事を `_drafts/` から `_posts/` へ移動してマージ

## ディレクトリ構成

```
.
├── _config.yml          # Jekyll設定
├── _drafts/            # 下書き記事（AI生成）
├── _posts/             # 公開記事
├── assets/             # 画像等のアセット
│   └── img/
├── scripts/            # スクリプト
│   └── generate_post.py
├── .github/
│   └── workflows/
│       └── generate.yml # GitHub Actions
└── requirements.txt    # Python依存関係
```

## カスタマイズ

### YouTube設定
`_data/youtube_settings.yml` で以下を設定できます：
- チャンネル情報（サブタイトル、URL）
- おすすめ動画のYouTube URL
- ソーシャルリンク

### 新規記事の追加
`_posts/` ディレクトリに `YYYY-MM-DD-title.md` 形式でファイルを作成：

```markdown
---
title: "記事タイトル"
date: 2025-09-03 10:00:00 +0900
categories: AI
image: https://example.com/image.jpg
excerpt: "記事の概要"
---

記事本文をここに書きます。
```

### カテゴリー
以下のカテゴリーが設定されています：
- AI・機械学習（紫）
- 起業戦略（オレンジ）
- 資金調達（青）
- YouTube（赤）
- マーケティング（緑）
- 自己成長（紫）

## プロジェクト構造

```
├── _layouts/              # レイアウトテンプレート
│   ├── home-youtube-unified.html  # ホームページ
│   ├── post-youtube.html         # 記事ページ
│   └── profile.html              # プロフィールページ
├── _includes/            # 共通コンポーネント
│   ├── youtube-hero.html         # ヒーローセクション
│   └── youtube-styles.html       # 共通スタイル
├── _posts/               # ブログ記事
├── _data/               # 設定データ
│   └── youtube_settings.yml      # YouTube設定
├── assets/              # CSS、画像など
├── profile.md           # プロフィールコンテンツ
├── vercel.json          # Vercel設定
└── package.json         # npm設定
```

## AI記事自動生成について

### GitHub Secretsの設定
GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定:
- `OPENAI_API_KEY`: OpenAI APIキー

### ワークフロー
1. 毎朝5時にGitHub Actionsが起動し、3記事を生成
2. Pull Requestが自動作成されるので内容を確認
3. 必要に応じて記事を修正
4. 公開したい記事を `_drafts/` から `_posts/` へ移動してマージ