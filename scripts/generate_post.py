#!/usr/bin/env python3
import os
import sys
import json
import random
from datetime import datetime
import openai
from typing import List, Dict
import re
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルから環境変数を読み込み
load_dotenv()

# OpenAI クライアントの初期化
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

# 記事のトピックとカテゴリ
TOPICS = [
    {
        "theme": "AI×スタートアップ",
        "categories": ["起業", "AI", "テクノロジー"],
        "tags": ["スタートアップ", "人工知能", "イノベーション", "ビジネスモデル"]
    },
    {
        "theme": "経営戦略とリーダーシップ",
        "categories": ["経営", "リーダーシップ", "戦略"],
        "tags": ["経営戦略", "組織運営", "意思決定", "チームビルディング"]
    },
    {
        "theme": "個人事業とフリーランス",
        "categories": ["個人事業", "フリーランス", "働き方"],
        "tags": ["独立", "フリーランス", "副業", "リモートワーク"]
    },
    {
        "theme": "起業の資金調達",
        "categories": ["起業", "資金調達", "投資"],
        "tags": ["ベンチャーキャピタル", "エンジェル投資", "クラウドファンディング", "資金調達"]
    },
    {
        "theme": "デジタルマーケティング",
        "categories": ["マーケティング", "デジタル", "戦略"],
        "tags": ["SNSマーケティング", "コンテンツマーケティング", "SEO", "グロースハック"]
    }
]

def generate_article_title(theme: str) -> str:
    """記事タイトルを生成"""
    prompt = f"""
    以下のテーマに関する魅力的なブログ記事のタイトルを1つ生成してください。
    テーマ: {theme}
    
    条件:
    - 20-40文字程度
    - 読者の興味を引く
    - 具体的で実践的
    - 日本語で
    
    タイトルのみを出力してください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはビジネスブログの編集者です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip()

def generate_article_content(title: str, theme: str, categories: List[str], tags: List[str]) -> str:
    """記事本文を生成"""
    prompt = f"""
    以下の条件でブログ記事を作成してください。

    タイトル: {title}
    テーマ: {theme}
    カテゴリ: {', '.join(categories)}
    タグ: {', '.join(tags)}
    
    記事の条件:
    - 文字数: 1000-1500文字
    - 構成: 導入、本文（3-4セクション）、まとめ
    - トーン: プロフェッショナルかつ親しみやすい
    - 実践的なアドバイスやTipsを含める
    - 具体例を交える
    - 読者（起業家、経営者、フリーランス）に価値を提供
    
    Markdown形式で出力してください。見出しは##から始めてください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは起業とビジネスに精通したプロのライターです。読者に実践的な価値を提供する記事を書きます。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content.strip()

def create_filename(title: str) -> str:
    """ファイル名を生成"""
    # 日付を取得
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # タイトルをURLフレンドリーに変換
    # 英数字とハイフンのみ残す
    clean_title = re.sub(r'[^\w\s-]', '', title)
    clean_title = re.sub(r'[-\s]+', '-', clean_title)
    clean_title = clean_title.strip('-').lower()[:50]  # 最大50文字
    
    # 日本語の場合は簡単な英訳を試みる
    if not clean_title or clean_title == '-':
        # フォールバック: ランダムな文字列
        clean_title = f"article-{random.randint(1000, 9999)}"
    
    return f"{date_str}-{clean_title}.md"

def save_article(title: str, content: str, categories: List[str], tags: List[str]) -> str:
    """記事をMarkdownファイルとして保存"""
    # フロントマター
    frontmatter = f"""---
layout: post
title: "{title}"
categories: {json.dumps(categories, ensure_ascii=False)}
tags: {json.dumps(tags, ensure_ascii=False)}
author: "Kevin"
date: {datetime.now().strftime('%Y-%m-%d')}
---

"""
    
    # 完全な記事
    full_article = frontmatter + content
    
    # ファイル名
    filename = create_filename(title)
    filepath = os.path.join('_drafts', filename)
    
    # ディレクトリが存在しない場合は作成
    os.makedirs('_drafts', exist_ok=True)
    
    # ファイルに保存
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_article)
    
    return filepath

def main():
    """メイン処理"""
    if not os.environ.get('OPENAI_API_KEY'):
        print("エラー: OPENAI_API_KEY環境変数が設定されていません。")
        sys.exit(1)
    
    print("AI記事生成を開始します...")
    
    # 3記事生成
    generated_files = []
    
    for i in range(3):
        print(f"\n記事 {i+1}/3 を生成中...")
        
        # ランダムにトピックを選択
        topic = random.choice(TOPICS)
        
        try:
            # タイトル生成
            title = generate_article_title(topic["theme"])
            print(f"タイトル: {title}")
            
            # 本文生成
            content = generate_article_content(
                title, 
                topic["theme"], 
                topic["categories"], 
                topic["tags"]
            )
            
            # ファイルに保存
            filepath = save_article(
                title,
                content,
                topic["categories"],
                topic["tags"]
            )
            
            generated_files.append(filepath)
            print(f"保存完了: {filepath}")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            continue
    
    print("\n記事生成が完了しました。")
    print("生成されたファイル:")
    for file in generated_files:
        print(f"  - {file}")
    
    # GitHub Actionsで使用するための出力
    if generated_files:
        with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
            f.write(f"generated_files={','.join(generated_files)}\n")

# 将来の拡張ポイント:
# TODO: Unsplash APIで記事テーマに合った画像を取得
# def fetch_unsplash_image(theme: str) -> Dict:
#     """Unsplash APIから画像を取得"""
#     pass

# TODO: YouTube台本生成機能
# def generate_youtube_script(article_title: str, article_content: str) -> str:
#     """記事を基にYouTube台本を生成"""
#     pass

# TODO: SNS投稿用の要約生成
# def generate_social_summary(article_content: str) -> Dict[str, str]:
#     """X(Twitter)やLinkedIn用の要約を生成"""
#     pass

if __name__ == "__main__":
    main()