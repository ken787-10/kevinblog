# 記事テンプレートの使い方

## ファイル名の規則
記事ファイル名は以下の形式にしてください：
```
YYYY-MM-DD-article-title-in-english.md
```

例：
- `2025-09-03-ai-startup-guide.md`
- `2025-09-04-marketing-strategy.md`

## 必須項目

### Front Matter（記事の設定）
```yaml
---
title: "記事のタイトル"
date: 2025-01-01 10:00:00 +0900
categories: 起業  # AI, 起業, 資金調達, YouTube, マーケティング, 自己成長 から選択
excerpt: "概要文（120文字程度）"
image: https://...  # アイキャッチ画像のURL
---
```

### カテゴリー一覧
- **AI**: AI・機械学習関連の記事
- **起業**: 起業戦略・ビジネス関連
- **資金調達**: 投資・ファンディング関連
- **YouTube**: 動画制作・YouTube戦略
- **マーケティング**: マーケティング・SEO
- **自己成長**: パーソナル成長・スキルアップ

## 画像の取得
Unsplashから無料の高品質画像を使用できます：
https://unsplash.com/

## 記事の公開
1. `_drafts`フォルダで記事を作成
2. 内容を確認後、`_posts`フォルダに移動
3. GitHubにプッシュすると自動的に公開されます