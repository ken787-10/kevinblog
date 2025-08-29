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
import requests

# .envファイルから環境変数を読み込み
load_dotenv()

# OpenAI クライアントの初期化
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

# Unsplash APIの設定
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

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
{theme}について、ビジネスブログの記事タイトルを作ってください。

読者は起業家やフリーランスの方々です。
彼らが「これは読みたい！」と思うような、実践的で役立ちそうなタイトルにしてください。

タイトルは20〜40文字くらいで、日本語でお願いします。
タイトルだけを出力してください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはビジネスブログの経験豊富な編集者です。読者にとって魅力的なタイトルを作るのが得意です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=100
    )
    
    content = response.choices[0].message.content.strip()
    # ```markdown で囲まれている場合は除去
    if content.startswith('```markdown') and content.endswith('```'):
        content = content[11:-3].strip()
    elif content.startswith('```') and content.endswith('```'):
        content = content[3:-3].strip()
    return content

def generate_article_content(title: str, theme: str, categories: List[str], tags: List[str]) -> str:
    """記事本文を生成"""
    prompt = f"""
「{title}」というタイトルで、{theme}についてのブログ記事を書いてください。

この記事を読む人は、起業家、経営者、フリーランスの方々です。
彼らが実際に使える具体的なアドバイスや方法を教えてあげてください。

記事の長さは1000〜1500文字くらいでお願いします。

以下のような構成で書いてください：
1. 最初に読者の共感を得る導入文
2. 本文は3〜4つのセクションに分けて
3. 具体的な例やケーススタディを入れる
4. 実践的なアクションプランやTipsを含める
5. 最後に次のステップを示すまとめ

文体は、プロフェッショナルだけど堅すぎず、親しみやすい感じで。
「です・ます調」で書いてください。

Markdownで書いてください。見出しは##（H2）から始めてください。
タイトルは既に決まっているので、本文には入れないでください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはビジネス経験が豊富なライターです。難しいことをわかりやすく説明し、読者がすぐに実践できるアドバイスを伝えるのが得意です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content.strip()
    # ```markdown で囲まれている場合は除去
    if content.startswith('```markdown') and content.endswith('```'):
        content = content[11:-3].strip()
    elif content.startswith('```') and content.endswith('```'):
        content = content[3:-3].strip()
    return content

def create_filename(title: str) -> str:
    """ファイル名を生成"""
    # 日付を取得
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # シンプルなファイル名生成（日本語を避ける）
    # タイトルの最初の単語を使うか、ランダムIDを生成
    words = re.findall(r'[a-zA-Z]+', title)
    if words:
        # 最初の3単語を使う
        clean_title = '-'.join(words[:3]).lower()
    else:
        # 英単語がない場合はランダムID
        clean_title = f"article-{random.randint(1000, 9999)}"
    
    # 最大30文字に制限
    clean_title = clean_title[:30]
    
    return f"{date_str}-{clean_title}.md"

def save_article(title: str, content: str, categories: List[str], tags: List[str], image_path: str = None, image_info: Dict = None) -> str:
    """記事をMarkdownファイルとして保存"""
    # フロントマター
    frontmatter_dict = {
        "layout": "post",
        "title": title,
        "categories": categories,
        "tags": tags,
        "author": "Kevin",
        "date": datetime.now().strftime('%Y-%m-%d')
    }
    
    # 画像がある場合はフロントマターに追加
    if image_path:
        frontmatter_dict["image"] = image_path
        if image_info:
            frontmatter_dict["image_credit"] = f'Photo by <a href="{image_info["author_url"]}?utm_source=unsplash&utm_medium=referral">{image_info["author"]}</a> on <a href="https://unsplash.com?utm_source=unsplash&utm_medium=referral">Unsplash</a>'
            if image_info.get('description'):
                frontmatter_dict["image_alt"] = image_info['description']
    
    # フロントマターを作成
    frontmatter = "---\n"
    for key, value in frontmatter_dict.items():
        if isinstance(value, list):
            frontmatter += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
        else:
            frontmatter += f'{key}: "{value}"\n' if isinstance(value, str) and key != "image_credit" else f"{key}: {value}\n"
    frontmatter += "---\n\n"
    
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
            
            # 画像を取得（オプション）
            image_info = None
            image_path = None
            if UNSPLASH_ACCESS_KEY:
                print("Unsplash画像を検索中...")
                image_info = fetch_unsplash_image(title, topic["theme"])
                if image_info:
                    # ファイル名を先に生成
                    filename = create_filename(title)
                    image_path = download_and_save_image(image_info, filename)
            
            # ファイルに保存
            filepath = save_article(
                title,
                content,
                topic["categories"],
                topic["tags"],
                image_path,
                image_info
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

def fetch_unsplash_image(query: str, theme: str) -> Dict:
    """Unsplash APIから画像を取得"""
    if not UNSPLASH_ACCESS_KEY:
        print("Unsplash APIキーが設定されていないため、画像は追加されません。")
        return None
    
    # 日本語クエリを英語に変換するための簡単なマッピング
    keyword_map = {
        "AI×スタートアップ": "artificial intelligence startup technology",
        "経営戦略とリーダーシップ": "business leadership strategy meeting",
        "個人事業とフリーランス": "freelance work laptop coffee",
        "起業の資金調達": "startup funding investment meeting",
        "デジタルマーケティング": "digital marketing social media analytics"
    }
    
    # テーマに基づいたキーワードを取得、なければクエリを使用
    search_query = keyword_map.get(theme, query)
    
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": search_query,
            "per_page": 5,
            "orientation": "landscape"
        }
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            # ランダムに1つ選択
            photo = random.choice(data['results'])
            return {
                'url': photo['urls']['regular'],
                'download_url': photo['links']['download_location'],
                'author': photo['user']['name'],
                'author_url': photo['user']['links']['html'],
                'description': photo.get('description', photo.get('alt_description', ''))
            }
    except Exception as e:
        print(f"Unsplash画像の取得中にエラーが発生しました: {e}")
    
    return None

def download_and_save_image(image_info: Dict, filename: str) -> str:
    """画像をダウンロードして保存"""
    if not image_info:
        return None
    
    try:
        # Unsplashのダウンロードトリガー（利用規約に従う）
        if UNSPLASH_ACCESS_KEY and 'download_url' in image_info:
            requests.get(
                image_info['download_url'],
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            )
        
        # 画像をダウンロード
        response = requests.get(image_info['url'])
        response.raise_for_status()
        
        # assetsディレクトリを作成
        assets_dir = os.path.join('assets', 'img', 'posts')
        os.makedirs(assets_dir, exist_ok=True)
        
        # ファイル名を生成
        image_filename = f"{filename.replace('.md', '')}.jpg"
        image_path = os.path.join(assets_dir, image_filename)
        
        # 画像を保存
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"画像を保存しました: {image_path}")
        return f"/assets/img/posts/{image_filename}"
        
    except Exception as e:
        print(f"画像の保存中にエラーが発生しました: {e}")
    
    return None

# 将来の拡張ポイント:

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