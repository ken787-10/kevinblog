---
layout: page_2col
title: "スタイルテスト - すべてのMarkdown要素"
subtitle: "このページでは、ブログで使用可能なすべてのMarkdown要素とスタイルをテストできます"
permalink: /style-test/
---

## 見出しのテスト

### レベル3の見出し

#### レベル4の見出し

##### レベル5の見出し

###### レベル6の見出し

---

## 段落と強調

これは通常の段落です。段落内では**太字**や*イタリック*、***太字イタリック***を使用できます。また、`インラインコード`も表示できます。

長い段落のテストです。AIとスタートアップの世界は急速に進化しており、起業家にとって新しいチャンスが日々生まれています。このような環境下で成功するためには、最新のトレンドを把握し、実践的なスキルを身につけることが重要です。

---

## リンク

[外部リンク - Google](https://www.google.com)

[内部リンク - ホームページ](/)

[タイトル付きリンク](https://github.com "GitHubへのリンク")

---

## リスト

### 箇条書きリスト

- 第1階層のアイテム
- 第2のアイテム
  - ネストされたアイテム
  - もう一つのネストアイテム
    - さらに深いネスト
- 第3のアイテム

### 番号付きリスト

1. 最初のステップ
2. 次のステップ
   1. サブステップA
   2. サブステップB
3. 最後のステップ

### タスクリスト

- [x] 完了したタスク
- [ ] 未完了のタスク
- [x] もう一つの完了したタスク

---

## 引用

> これは引用ブロックです。
> 複数行にわたる引用も可能です。

> ネストされた引用も可能です。
>> これはネストされた引用です。
>>> さらに深いネスト

---

## コード

### インラインコード

文章の中で`const greeting = "Hello World";`のようにコードを挿入できます。

### コードブロック

```javascript
// JavaScriptの例
function calculateSum(a, b) {
  return a + b;
}

const result = calculateSum(10, 20);
console.log(`結果: ${result}`);
```

```python
# Pythonの例
def generate_blog_post(topic):
    """AIを使ってブログ記事を生成する"""
    prompt = f"次のトピックについて記事を書いてください: {topic}"
    return ai_model.generate(prompt)

# 使用例
article = generate_blog_post("スタートアップの資金調達")
print(article)
```

```yaml
# YAML設定ファイルの例
title: "Kevin's Business Blog"
description: "起業とAIの実践的知識"
plugins:
  - jekyll-feed
  - jekyll-seo-tag
```

---

## テーブル

| カテゴリ | 説明 | 重要度 |
|---------|------|-------|
| AI | 人工知能関連の記事 | ⭐⭐⭐⭐⭐ |
| スタートアップ | 起業に関する情報 | ⭐⭐⭐⭐ |
| 資金調達 | 投資や資金調達の戦略 | ⭐⭐⭐⭐ |
| マーケティング | 集客・販売戦略 | ⭐⭐⭐ |

### 左寄せ、中央寄せ、右寄せ

| 左寄せ | 中央寄せ | 右寄せ |
|:------|:------:|------:|
| テキスト | テキスト | テキスト |
| 100 | 200 | 300 |
| A | B | C |

---

## 画像

![サンプル画像](https://images.unsplash.com/photo-1556075798-4825dfaaf498?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80)

### キャプション付き画像

<figure>
  <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80" alt="チームワークとコラボレーション">
  <figcaption>これは画像のキャプションです - Photo by Annie Spratt on Unsplash</figcaption>
</figure>

---

## 水平線

上記で既に使用していますが、3つ以上のハイフン、アスタリスク、アンダースコアで作成できます。

---

***

___

---

## HTML要素

<div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
  <p style="margin: 0;">これはHTMLで直接スタイリングされたブロックです。</p>
</div>

<details>
<summary>クリックして展開</summary>

隠されたコンテンツがここに表示されます。
- アイテム1
- アイテム2
- アイテム3

</details>

---

## 数式（MathJaxを使用する場合）

インライン数式: $E = mc^2$

ブロック数式:

$$
\frac{n!}{k!(n-k)!} = \binom{n}{k}
$$

---

## 絵文字

:smile: :rocket: :computer: :chart_with_upwards_trend: :bulb:

（注：Jekyllで絵文字プラグインが必要）

---

## 脚注

これは脚注のテストです[^1]。別の脚注もあります[^2]。

[^1]: これが最初の脚注です。
[^2]: これが2番目の脚注です。

---

## 定義リスト

用語1
: 用語1の定義です。

用語2
: 用語2の定義です。
: 同じ用語に複数の定義を持たせることもできます。

---

## キーボードショートカット

<kbd>Cmd</kbd> + <kbd>C</kbd> でコピー

<kbd>Ctrl</kbd> + <kbd>V</kbd> でペースト

---

## 略語

HTML と CSS は Web開発の基本です。

*[HTML]: HyperText Markup Language
*[CSS]: Cascading Style Sheets

---

## まとめ

このページでは、ブログで使用可能なすべてのMarkdown要素とスタイルをテストしました。これらの要素を組み合わせることで、読みやすく魅力的なブログ記事を作成することができます。