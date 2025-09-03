# SEO設定ガイド

このブログのSEO設定方法について説明します。

## 設定ファイルの場所

### 1. **_config.yml** - 基本設定
```yaml
# サイトの基本情報
title: Kevin's UPGRADE Blog
description: 起業家Kevinが起業、AI、経営戦略、進化に関する実践的な情報を発信
url: "https://kevinblog.vercel.app"
author: Kevin
lang: ja

# SEO関連
twitter:
  username: upgrade-life
  card: summary_large_image

# Google Analytics
google_analytics: "G-XXXXXXXXXX"  # あなたのIDに置き換え
```

### 2. **_data/seo.yml** - SEO詳細設定
- Google Analytics ID
- Google Search Console認証コード
- デフォルトキーワード
- ソーシャルメディアリンク

### 3. **各記事のフロントマター** - 記事ごとのSEO
```yaml
---
title: "記事のタイトル"
excerpt: "記事の説明（OGP description）"
image: "https://example.com/image.jpg"  # OGP画像
tags: ["AI", "起業", "ChatGPT"]  # キーワード
---
```

## Google Analytics設定方法

1. [Google Analytics](https://analytics.google.com/)にアクセス
2. 新しいプロパティを作成
3. 測定IDを取得（G-で始まるID）
4. `_config.yml`の`google_analytics:`に設定

```yaml
google_analytics: "G-XXXXXXXXXX"
```

## Google Search Console設定方法

1. [Google Search Console](https://search.google.com/search-console)にアクセス
2. プロパティを追加
3. 所有権の確認でHTMLタグを選択
4. メタタグの`content`の値をコピー
5. `_config.yml`に追加

```yaml
webmaster_verifications:
  google: "verification_code_here"
```

## OGP（Open Graph Protocol）設定

各記事で設定可能：
- `title`: 記事タイトル
- `excerpt`: 記事の説明
- `image`: サムネイル画像URL

デフォルトでは`/assets/img/posts/channels_profile.jpg`が使用されます。

## サイトマップ

- `/sitemap.xml`に自動生成
- Google Search Consoleに登録推奨

## robots.txt

- `/robots.txt`に設定済み
- 必要に応じてクロール制限を追加

## 確認方法

1. **OGPデバッガー**
   - [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
   - [Twitter Card Validator](https://cards-dev.twitter.com/validator)

2. **構造化データテスト**
   - [Google Rich Results Test](https://search.google.com/test/rich-results)

3. **PageSpeed Insights**
   - [PageSpeed Insights](https://pagespeed.web.dev/)

## 注意事項

- `_config.yml`を変更した場合はJekyllの再起動が必要
- Vercelにデプロイ後、実際のURLで動作確認を推奨
- Google Analyticsは本番環境のみで動作