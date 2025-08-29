# Kevin's AI-Powered Blog

JekyllとAI（OpenAI API）を使った自動記事生成ブログシステムです。

## 機能

- 毎日朝5時（JST）に3記事を自動生成
- 記事は `_drafts/` フォルダに保存され、レビュー後に公開
- GitHub Actionsによる完全自動化
- Pull Request経由でのレビューフロー

## セットアップ手順

### 1. リポジトリの準備

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd <your-repo-name>

# Jekyllをインストール
gem install bundler jekyll
bundle install

# 必要なディレクトリを作成
mkdir -p _drafts _posts assets/img
```

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

### トピックの追加

`scripts/generate_post.py` の `TOPICS` リストに新しいテーマを追加:

```python
{
    "theme": "新しいテーマ",
    "categories": ["カテゴリ1", "カテゴリ2"],
    "tags": ["タグ1", "タグ2", "タグ3"]
}
```

### 生成記事数の変更

`scripts/generate_post.py` の以下の部分を修正:

```python
for i in range(3):  # この数字を変更
```

### 実行時間の変更

`.github/workflows/generate.yml` のcron設定を修正:

```yaml
- cron: '0 20 * * *'  # UTC時間で設定（JSTから-9時間）
```

## トラブルシューティング

### OpenAI APIエラー

- APIキーが正しく設定されているか確認
- APIの利用制限に達していないか確認

### GitHub Actionsが動かない

- GitHub Secretsが正しく設定されているか確認
- Actionsが有効になっているか確認（Settings > Actions）

## 今後の拡張予定

- [ ] Unsplash APIでアイキャッチ画像を自動取得
- [ ] YouTube台本の同時生成
- [ ] SNS（X、LinkedIn）への自動投稿
- [ ] 記事の品質評価機能
- [ ] カテゴリ別の生成頻度調整