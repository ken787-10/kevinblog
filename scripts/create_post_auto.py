#!/usr/bin/env python3
"""
全自動記事作成ツール
概要だけを入力すると、AIが完全な記事を生成
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
import re
from dotenv import load_dotenv
from openai import OpenAI
import random
from PIL import Image
from io import BytesIO
from colorama import Fore, Back, Style, init
from image_optimizer import ImageOptimizer

# カラー出力の初期化
init(autoreset=True)

# .envファイルから環境変数を読み込み
load_dotenv()

# OpenAI クライアントの初期化
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

# Unsplash APIの設定
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

class AutoPostCreator:
    def __init__(self):
        self.post_data = {}
        self.image_optimizer = ImageOptimizer(max_width=1000, quality=85)
    
    def display_header(self):
        """ヘッダー表示"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🤖 全自動記事作成ツール")
        print(f"{Fore.CYAN}{'='*60}\n")
        print(f"{Fore.GREEN}概要だけ入力すれば、AIが完全な記事を作成します。")
    
    def get_overview(self):
        """概要の入力"""
        print(f"\n{Fore.YELLOW}📝 記事の概要を教えてください")
        print(f"{Fore.GREEN}以下の内容を含めて、記事について簡潔に説明してください:")
        print("• どのようなテーマの記事か")
        print("• 誰に向けた記事か")
        print("• どのような価値・情報を提供したいか")
        print("• 特に含めたいポイントがあれば")
        print("・上記質問で書き足りなかったり修正すべき点があれば書いてください")
        
        overview = input(f"\n{Fore.GREEN}概要: ").strip()
        
        if not overview:
            print(f"{Fore.RED}概要が入力されていません。")
            sys.exit(1)
        
        return overview
    
    def get_additional_info(self, title: str, overview: str, structure: List[str]) -> Dict:
        """記事の質を高めるための追加情報を収集"""
        print(f"\n{Fore.YELLOW}🎯 記事の精度を高めるための追加質問")
        print(f"{Fore.CYAN}予想記事タイトル: {title}")
        print(f"{Fore.CYAN}予想構成: {' → '.join(structure)}")
        
        additional_info = {}
        
        # 1. 想定読者の詳細化
        print(f"\n{Fore.GREEN}1. 読者をより具体的に教えてください:")
        print("   例: 創業3年以内のスタートアップCEO、副業を検討中のサラリーマンなど")
        target_reader = input("   > ").strip()
        if target_reader:
            additional_info['target_reader'] = target_reader
        
        # 2. 具体的なデータや事例の要望
        print(f"\n{Fore.GREEN}2. 含めたい具体的なデータ・統計・事例はありますか？:")
        print("   例: 市場規模、成功率、具体的な企業名、個人的な体験談など")
        data_examples = input("   > ").strip()
        if data_examples:
            additional_info['data_examples'] = data_examples
        
        # 3. 避けたい内容・注意点
        print(f"\n{Fore.GREEN}3. 避けたい内容や注意すべき点はありますか？:")
        print("   例: 特定の業界への偏見、過度な楽観論、リスクの軽視など")
        avoid_content = input("   > ").strip()
        if avoid_content:
            additional_info['avoid_content'] = avoid_content
        
        # 4. 記事の独自性・差別化ポイント
        print(f"\n{Fore.GREEN}4. この記事の独自性や差別化したいポイントは？:")
        print("   例: テック業界での実体験、最新のAIツール活用、海外事例の紹介など")
        unique_point = input("   > ").strip()
        if unique_point:
            additional_info['unique_point'] = unique_point
        
        # 5. 読者に期待する行動
        print(f"\n{Fore.GREEN}5. 記事を読んだ読者に最終的にどのような行動を取ってほしいですか？:")
        print("   例: サービスへの問い合わせ、SNSでのシェア、具体的なツールの試用など")
        desired_action = input("   > ").strip()
        if desired_action:
            additional_info['desired_action'] = desired_action
        
        return additional_info
    
    def generate_complete_article(self, overview: str) -> Dict:
        """概要から完全な記事を生成"""
        print(f"\n{Fore.CYAN}🤖 AIが記事を生成中...")
        
        # 記事構成の生成
        print("  📋 記事構成を生成中...")
        structure = self.generate_article_structure(overview)
        
        # タイトル生成
        print("  📝 タイトルを生成中...")
        title = self.generate_title(overview, structure)
        
        # カテゴリ・タグ生成
        print("  🏷️ カテゴリとタグを生成中...")
        categories, tags = self.generate_categories_and_tags(overview)
        
        # 追加情報の収集
        additional_info = self.get_additional_info(title, overview, structure)
        
        # 本文生成
        print("  ✍️ 本文を生成中...")
        content = self.generate_full_content(title, overview, structure, additional_info)
        
        # メタディスクリプション生成
        print("  📋 メタディスクリプションを生成中...")
        meta_description = self.generate_meta_description(title, content[:500])
        
        # 画像キーワード生成
        print("  🖼️ 画像キーワードを生成中...")
        image_keywords = self.generate_image_keywords(title, overview)
        
        return {
            'title': title,
            'structure': structure,
            'content': content,
            'categories': categories,
            'tags': tags,
            'meta_description': meta_description,
            'image_keywords': image_keywords
        }
    
    def generate_article_structure(self, overview: str) -> List[str]:
        """記事構成を生成"""
        prompt = f"""
以下の概要から、テック系起業家の視点で価値を提供する記事構成を作成してください。

概要: {overview}

要件:
• 読者: テック業界の起業家・経営者・CTOレベルの人材
• 構成: 5-8個のセクションで論理的に構成
• 内容の質: コピーライティングの編集を通過するレベルの高品質
• 実践性: すぐに実行できる具体的なアクション項目を含む
• データ重視: 定量的な情報・統計・市場データを含める構成
• 差別化: ありきたりでない、独自の視点や最新トレンドを含める
• 結論: 明確な行動喚起で終わる

テック系起業家が「これは価値がある」と思う構成にしてください。
構成の各セクション名を1行ずつ出力してください。番号や記号は不要です。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテック業界に精通したシニアエディターです。Y Combinator、Andreessen Horowitz等の一流VCブログや、TechCrunch、The Information等のメディアでコンテンツを手がけ、起業家向けの高品質記事を数多く執筆してきました。データドリブンで実践的な構成作りが得意です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        content = response.choices[0].message.content.strip()
        structure = [line.strip() for line in content.split('\n') if line.strip()]
        return structure
    
    def generate_title(self, overview: str, structure: List[str]) -> str:
        """タイトルを生成"""
        prompt = f"""
以下の記事概要と構成から、テック系起業家が思わずクリックしたくなるタイトルを作成してください。

概要: {overview}
構成: {', '.join(structure)}

要件:
• 文字数: 28-35文字（SEO最適）
• ターゲット: テック業界の起業家・CTO・技術責任者
• クリック率最大化: 具体的な数字、ROI、成長率、効率化などを含める
• SEO対策: 検索ボリュームの多いキーワードを自然に配置
• 権威性: 「実証済み」「データで検証」「成功事例」等の表現
• 緊急性: 「2024年版」「最新」「今すぐ」等のタイムリー要素
• 差別化: 一般的な記事タイトルと差をつける独自性

例: 「SaaSスタートアップが ARR を3倍にした 5つの成長戦略【2024年実証済み】」

タイトルのみを出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテック業界専門のコピーライターです。TechCrunch、VentureBeat、Hacker News等で高いエンゲージメントを獲得するタイトル作成に精通しており、テック起業家の心理を深く理解しています。数字とデータで効果を裏付けるタイトル作りが得意です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_categories_and_tags(self, overview: str) -> tuple:
        """カテゴリとタグを生成"""
        available_categories = ['起業', 'AI', 'マーケティング', '経営', 'フリーランス', '資金調達', 'テクノロジー', '働き方']
        
        prompt = f"""
以下の記事概要に最適なカテゴリとタグを選択・生成してください。

概要: {overview}

利用可能なカテゴリ: {', '.join(available_categories)}

要件:
• カテゴリ: 上記から1-3個選択
• タグ: 記事内容に関連する具体的なキーワード5-8個

以下の形式で出力してください:
カテゴリ: カテゴリ1, カテゴリ2
タグ: タグ1, タグ2, タグ3, タグ4, タグ5
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはコンテンツ分類の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        categories = []
        tags = []
        
        for line in content.split('\n'):
            if line.startswith('カテゴリ:'):
                categories = [cat.strip() for cat in line.replace('カテゴリ:', '').split(',') if cat.strip()]
            elif line.startswith('タグ:'):
                tags = [tag.strip() for tag in line.replace('タグ:', '').split(',') if tag.strip()]
        
        return categories, tags
    
    def generate_full_content(self, title: str, overview: str, structure: List[str], additional_info: Dict) -> str:
        """完全な記事本文を生成（追加情報を活用）"""
        sections = []
        
        # 追加情報を文章に組み込む
        additional_context = ""
        if additional_info.get('target_reader'):
            additional_context += f"具体的読者: {additional_info['target_reader']}\n"
        if additional_info.get('data_examples'):
            additional_context += f"含めるべきデータ・事例: {additional_info['data_examples']}\n"
        if additional_info.get('unique_point'):
            additional_context += f"差別化ポイント: {additional_info['unique_point']}\n"
        if additional_info.get('avoid_content'):
            additional_context += f"避けるべき内容: {additional_info['avoid_content']}\n"
        if additional_info.get('desired_action'):
            additional_context += f"期待する読者の行動: {additional_info['desired_action']}\n"
        
        # 導入文を生成
        intro_prompt = f"""
「{title}」という記事の導入文を書いてください。

記事概要: {overview}

{additional_context}

要件（テック系起業家向け高品質記事）:
• 読者の痛みポイントに深く共感し、解決への期待を高める
• データや統計を使って問題の深刻さを裏付ける
• この記事だけが提供する独自価値を明確に示す
• 180-250文字程度（一般記事より情報密度を高く）
• テック業界の最新トレンドや専門用語を適切に使用
• 「コピーライティングの編集を通過するレベル」の品質

導入文のみを出力してください。見出しは不要です。
"""
        
        intro_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテック業界のエディトリアルディレクターです。Forbes、Harvard Business Review、McKinsey等の一流メディアで執筆経験があり、データドリブンで説得力のある導入文作りに定評があります。"},
                {"role": "user", "content": intro_prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        sections.append(intro_response.choices[0].message.content.strip())
        
        # 各セクションの本文を生成
        for i, section_title in enumerate(structure):
            section_content = self.generate_section_content(title, overview, section_title, i+1, len(structure), additional_info)
            sections.append(f"## {section_title}\n\n{section_content}")
        
        return "\n\n".join(sections)
    
    def generate_section_content(self, title: str, overview: str, section_title: str, section_num: int, total_sections: int, additional_info: Dict = None) -> str:
        """各セクションの内容を生成（追加情報を活用）"""
        # セクションの役割を判定
        section_role = self.determine_section_role(section_title, section_num, total_sections)
        
        # 追加情報を文脈に組み込む
        additional_context = ""
        if additional_info:
            if additional_info.get('data_examples'):
                additional_context += f"参考にすべきデータ・事例: {additional_info['data_examples']}\n"
            if additional_info.get('unique_point'):
                additional_context += f"強調すべき独自性: {additional_info['unique_point']}\n"
            if additional_info.get('target_reader'):
                additional_context += f"具体的読者像: {additional_info['target_reader']}\n"
            if additional_info.get('desired_action') and section_num == total_sections:
                additional_context += f"促すべき行動: {additional_info['desired_action']}\n"
        
        prompt = f"""
「{title}」という記事の「{section_title}」セクションを執筆してください。

記事概要: {overview}
セクション位置: {section_num}/{total_sections}
セクションの役割: {section_role}

{additional_context}

要件（テック系起業家向け高品質記事）:
• 読者: テック業界の起業家、CTO、技術責任者レベル
• 文体: 権威性があり信頼できる専門的な「です・ます調」
• 長さ: 500-800文字（情報密度を高く）
• 必須要素:
  - 具体的なデータ、統計、調査結果の引用
  - 実在する企業・サービスの成功事例
  - 今すぐ実行可能な具体的アクション（3-5項目）
  - ROI や効果の定量的指標
  - 最新のテック業界トレンドの言及
• フォーマット: 適切な箇条書き、番号付きリスト、引用を使用
• 品質: 「コピーライティングの編集を通過するレベル」
• 専門性: テック業界の専門用語を適切に使用（必要に応じて簡潔な説明を付加）

{section_role}としての役割を果たしつつ、上記要件を満たす高品質なコンテンツを作成してください。
見出し（##）は不要です。本文のみを出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテック業界で10年以上の経験を持つシニアライターです。Y Combinator、Andreessen Horowitz、Sequoia Capital等のトップティアVCブログや、TechCrunch、The Information等で記事を執筆しており、データドリブンで実践的な記事作成に定評があります。McKinsey、BCG等のコンサルティングファーム出身で、ビジネス戦略とテクノロジーの両方に精通しています。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1200
        )
        
        return response.choices[0].message.content.strip()
    
    def determine_section_role(self, section_title: str, section_num: int, total_sections: int) -> str:
        """セクションの役割を判定"""
        section_title_lower = section_title.lower()
        
        if section_num == 1:
            return "記事の主題を明確に説明し、読者の理解を深める導入的役割"
        elif section_num == total_sections:
            return "記事全体をまとめ、読者の次の行動を促す結論的役割"
        elif "方法" in section_title or "ステップ" in section_title or "手順" in section_title:
            return "具体的な実行方法を段階的に解説する手順説明的役割"
        elif "ポイント" in section_title or "重要" in section_title:
            return "重要な要素を整理して読者の理解を深める要点整理的役割"
        elif "注意" in section_title or "失敗" in section_title or "課題" in section_title:
            return "リスクや注意点を説明し、読者の失敗を防ぐ警告的役割"
        elif "事例" in section_title or "例" in section_title or "ケース" in section_title:
            return "具体的な成功例や実例を紹介し、読者の理解を具体化する事例紹介的役割"
        else:
            return "記事の流れに沿って必要な情報を詳しく説明する説明的役割"
    
    def generate_meta_description(self, title: str, content_sample: str) -> str:
        """メタディスクリプションを生成"""
        prompt = f"""
以下の記事のメタディスクリプションを作成してください。

タイトル: {title}
本文冒頭: {content_sample}

要件:
• 120-155文字
• 記事の価値を明確に伝える
• 読者がクリックしたくなる魅力的な内容
• 主要キーワードを含める
• 検索結果で目立つ表現

メタディスクリプションのみを出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはSEOとクリック率最適化の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_image_keywords(self, title: str, overview: str) -> List[str]:
        """画像検索用のキーワードを生成"""
        prompt = f"""
以下の記事に適した画像のキーワードを生成してください。

タイトル: {title}
概要: {overview}

要件:
• Unsplashで検索できる英語キーワード
• 記事のテーマに関連する視覚的なイメージ
• プロフェッショナルでビジネス向けの画像
• 3-5個のキーワードセット

キーワードのみを1行ずつ出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは視覚的コンテンツの専門家です。記事に最適な画像を選ぶのが得意です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        keywords = [line.strip() for line in content.split('\n') if line.strip()]
        return keywords[:5]  # 最大5個
    
    def fetch_and_select_images(self, keywords: List[str], article_data: Dict) -> Dict:
        """画像を自動選択"""
        if not UNSPLASH_ACCESS_KEY:
            print(f"{Fore.YELLOW}⚠️ Unsplash APIキーが未設定のため、画像は追加されません。")
            return {}
        
        selected_images = {}
        
        print(f"\n{Fore.CYAN}🖼️ 画像を自動選択中...")
        
        # サムネイル画像の選択
        for keyword in keywords[:2]:  # 最初の2つのキーワードで試行
            thumbnail = self.search_best_image(keyword, "landscape")
            if thumbnail:
                selected_images['thumbnail'] = thumbnail
                print(f"  ✓ サムネイル画像を選択: {keyword}")
                break
        
        # 本文用画像の選択（記事の長さに基づいて1-3枚）
        content_length = len(article_data['content'])
        num_content_images = min(3, max(1, content_length // 1500))  # 1500文字ごとに1枚
        
        content_images = []
        used_keywords = set()
        
        for i in range(num_content_images):
            for keyword in keywords:
                if keyword not in used_keywords:
                    image = self.search_best_image(keyword, "landscape")
                    if image:
                        content_images.append({
                            'image': image,
                            'position': i,
                            'keyword': keyword
                        })
                        used_keywords.add(keyword)
                        print(f"  ✓ 本文画像{i+1}を選択: {keyword}")
                        break
        
        selected_images['content_images'] = content_images
        return selected_images
    
    def search_best_image(self, keyword: str, orientation: str = "landscape") -> Optional[Dict]:
        """最適な画像を検索して選択"""
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": keyword,
                "per_page": 10,
                "orientation": orientation,
                "order_by": "relevance"
            }
            headers = {
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('results'):
                return None
            
            # 最も適切な画像を選択（最初の結果を使用）
            photo = data['results'][0]
            
            return {
                'url': photo['urls']['regular'],
                'download_url': photo['links']['download_location'],
                'author': photo['user']['name'],
                'author_url': photo['user']['links']['html'],
                'description': photo.get('description', photo.get('alt_description', '')),
                'width': photo['width'],
                'height': photo['height']
            }
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ 画像検索エラー ({keyword}): {e}")
            return None
    
    def download_and_optimize_image(self, image_info: Dict, filename_base: str, is_thumbnail: bool = False) -> Optional[str]:
        """画像のダウンロードと最適化"""
        try:
            # Unsplashのダウンロードトリガー
            if UNSPLASH_ACCESS_KEY and 'download_url' in image_info:
                requests.get(
                    image_info['download_url'],
                    headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
                )
            
            # 画像をダウンロード
            response = requests.get(image_info['url'])
            response.raise_for_status()
            
            # PILで画像を開く
            img = Image.open(BytesIO(response.content))
            
            # 画像の最適化
            if is_thumbnail:
                # サムネイルは1200x630に最適化（OGP対応）
                img = self.resize_image_for_thumbnail(img, 1200, 630)
                quality = 85
            else:
                # 本文画像は最大幅1000pxに制限
                if img.width > 1000:
                    ratio = 1000 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1000, new_height), Image.Resampling.LANCZOS)
                quality = 90
            
            # 保存
            assets_dir = os.path.join('assets', 'img', 'posts')
            os.makedirs(assets_dir, exist_ok=True)
            
            if is_thumbnail:
                image_filename = f"{filename_base}-thumb.jpg"
            else:
                timestamp = datetime.now().strftime('%H%M%S')
                random_suffix = random.randint(100, 999)
                image_filename = f"{filename_base}-{timestamp}-{random_suffix}.jpg"
            
            image_path = os.path.join(assets_dir, image_filename)
            
            # RGB変換（RGBA画像の場合）
            if img.mode in ('RGBA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            return f"/assets/img/posts/{image_filename}"
            
        except Exception as e:
            print(f"{Fore.RED}画像の処理中にエラー: {e}")
            return None
    
    def resize_image_for_thumbnail(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """サムネイル用に画像をリサイズ"""
        # アスペクト比を計算
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # 画像が横長すぎる場合
            new_width = int(target_height * img_ratio)
            img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            # 中央からクロップ
            left = (new_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # 画像が縦長すぎる場合
            new_height = int(target_width / img_ratio)
            img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            # 中央からクロップ
            top = (new_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))
        
        return img
    
    def save_complete_article(self, article_data: Dict, images: Dict) -> str:
        """完成した記事を保存"""
        print(f"\n{Fore.CYAN}💾 記事を保存中...")
        
        # ファイル名の生成
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename_base = re.sub(r'[^\w\s-]', '', article_data['title'])
        filename_base = re.sub(r'[-\s]+', '-', filename_base)[:30].lower()
        filename = f"{date_str}-{filename_base}.md"
        
        # フロントマター
        frontmatter = {
            'layout': 'post',
            'title': article_data['title'],
            'categories': article_data['categories'],
            'tags': article_data['tags'],
            'author': 'Kevin',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': article_data['meta_description']
        }
        
        # サムネイル画像の処理
        if images.get('thumbnail'):
            thumbnail_path = self.download_and_optimize_image(
                images['thumbnail'], 
                filename_base, 
                is_thumbnail=True
            )
            if thumbnail_path:
                frontmatter['image'] = thumbnail_path
                frontmatter['image_alt'] = images['thumbnail'].get('description', '')
                frontmatter['image_credit'] = f'Photo by <a href="{images["thumbnail"]["author_url"]}?utm_source=unsplash&utm_medium=referral">{images["thumbnail"]["author"]}</a> on <a href="https://unsplash.com?utm_source=unsplash&utm_medium=referral">Unsplash</a>'
        
        # 本文に画像を挿入
        content_with_images = self.insert_images_into_content(article_data['content'], images.get('content_images', []), filename_base)
        
        # 文字数チェック
        content_length = len(content_with_images)
        print(f"  📊 記事の文字数: {content_length}文字")
        
        if content_length < 2000:
            print(f"  ⚠️ 文字数が少ないため、追加コンテンツを生成中...")
            additional_content = self.generate_additional_content(article_data)
            content_with_images += f"\n\n{additional_content}"
            print(f"  ✓ 追加コンテンツを生成しました（+{len(additional_content)}文字）")
        
        # Markdownファイルの作成
        markdown_content = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, list):
                markdown_content += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
            elif key == 'image_credit':
                markdown_content += f'{key}: {value}\n'
            else:
                markdown_content += f'{key}: "{value}"\n'
        markdown_content += "---\n\n"
        markdown_content += content_with_images
        
        # ファイル保存
        filepath = os.path.join('_drafts', filename)
        os.makedirs('_drafts', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"  ✅ 記事を保存しました: {filepath}")
        return filepath
    
    def insert_images_into_content(self, content: str, content_images: List[Dict], filename_base: str) -> str:
        """コンテンツに画像を挿入"""
        if not content_images:
            return content
        
        sections = content.split('\n\n')
        
        # 画像を均等に配置
        num_sections = len([s for s in sections if s.startswith('##')])
        if num_sections <= 1:
            return content
        
        section_interval = max(1, num_sections // len(content_images))
        
        for i, image_data in enumerate(content_images):
            # 挿入位置を計算
            target_section = min(i * section_interval + 1, num_sections - 1)
            insert_index = self.find_section_end_index(sections, target_section)
            
            # 画像をダウンロードして最適化
            image_path = self.download_and_optimize_image(
                image_data['image'], 
                filename_base, 
                is_thumbnail=False
            )
            
            if image_path:
                image_markdown = f"\n![{image_data['image'].get('description', '')}]({image_path})\n"
                image_markdown += f'*Photo by [{image_data["image"]["author"]}]({image_data["image"]["author_url"]}?utm_source=unsplash&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=unsplash&utm_medium=referral)*\n'
                
                sections.insert(insert_index + 1, image_markdown)
                print(f"  📷 画像を挿入: {image_data['keyword']}")
        
        return '\n\n'.join(sections)
    
    def find_section_end_index(self, sections: List[str], target_section: int) -> int:
        """指定されたセクションの終了インデックスを見つける"""
        section_count = 0
        for i, section in enumerate(sections):
            if section.startswith('##'):
                section_count += 1
                if section_count == target_section:
                    return i
        return len(sections) - 1
    
    def generate_additional_content(self, article_data: Dict) -> str:
        """追加コンテンツを生成（2000文字に満たない場合）"""
        prompt = f"""
「{article_data['title']}」の記事に追加するテック系起業家向け高品質コンテンツを作成してください。

既存の記事構成: {', '.join(article_data['structure'])}

以下のセクションから最も価値の高いものを1つ選んで、詳細な内容を書いてください:
• よくある質問（FAQ）- 実際のCEO/CTOからの質問を想定
• 実装チェックリスト - 段階的に実行できる具体的リスト
• ベンチマーク・KPI設定 - 成功の測定方法
• 失敗回避のポイント - 実際の失敗事例から学ぶ注意点
• ROI計算・効果測定 - 定量的な成果の測り方

要件（テック系起業家向け高品質）:
• 長さ: 400-600文字（情報密度を高く）
• データ重視: 具体的な数字、統計、業界データを含める
• 実践性: すぐに使える具体的なツールやフレームワークを紹介
• 権威性: 実在する企業や調査機関の情報を引用
• 専門性: テック業界の最新トレンドを反映
• 適切な見出し（##）を含める
• 「コピーライティングの編集を通過するレベル」の品質

既存コンテンツと重複しない、読者にとって即座に実践できる価値ある追加情報を提供してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテック業界のコンサルタントで、McKinsey & Company、Boston Consulting Group等で戦略策定に携わった経験があります。データドリブンなアプローチで実践的な価値を提供し、スタートアップから大企業まで幅広いクライアントを支援してきました。記事の価値を最大化する追加コンテンツ作成が得意です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    def run(self):
        """メイン実行"""
        self.display_header()
        
        try:
            # 概要の入力
            overview = self.get_overview()
            
            # 完全な記事を生成
            article_data = self.generate_complete_article(overview)
            
            # 画像を自動選択
            images = self.fetch_and_select_images(article_data['image_keywords'], article_data)
            
            # 記事を保存
            filepath = self.save_complete_article(article_data, images)
            
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}🎉 全自動記事作成が完了しました！")
            print(f"{Fore.GREEN}{'='*60}")
            print(f"\n{Fore.CYAN}📝 生成された記事:")
            print(f"  📄 タイトル: {article_data['title']}")
            print(f"  📂 カテゴリ: {', '.join(article_data['categories'])}")
            print(f"  🏷️ タグ: {', '.join(article_data['tags'])}")
            print(f"  📊 文字数: {len(article_data['content'])}文字")
            print(f"  💾 保存先: {filepath}")
            
            if images.get('thumbnail'):
                print(f"  🖼️ サムネイル: ✓")
            if images.get('content_images'):
                print(f"  📷 本文画像: {len(images['content_images'])}枚")
            
            print(f"\n{Fore.CYAN}プレビューを表示するには:")
            print(f"  bundle exec jekyll serve --drafts")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ 作成を中断しました。")
        except Exception as e:
            print(f"\n{Fore.RED}❌ エラーが発生しました: {e}")

def main():
    """メイン処理"""
    if not os.environ.get('OPENAI_API_KEY'):
        print(f"{Fore.RED}エラー: OPENAI_API_KEY環境変数が設定されていません。")
        sys.exit(1)
    
    creator = AutoPostCreator()
    creator.run()

if __name__ == "__main__":
    main()