#!/usr/bin/env python3
"""
インタラクティブ記事作成支援ツール
ユーザーの入力に基づいてAIがサポートしながら高品質な記事を作成
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from dotenv import load_dotenv
from openai import OpenAI
import yaml
from PIL import Image
from io import BytesIO
import inquirer
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

class InteractivePostCreator:
    def __init__(self):
        self.post_data = {
            'title': '',
            'outline': [],
            'content': '',
            'categories': [],
            'tags': [],
            'images': [],
            'thumbnail': None,
            'meta_description': ''
        }
        self.templates = self.load_templates()
        self.image_optimizer = ImageOptimizer(max_width=1000, quality=85)
    
    def load_templates(self) -> Dict:
        """記事構成テンプレートを読み込み"""
        templates = {
            'how-to': {
                'name': 'ハウツー記事',
                'structure': [
                    '導入（読者の課題・悩みに共感）',
                    '概要（この記事で得られること）',
                    'ステップ1（具体的な手順）',
                    'ステップ2（具体的な手順）',
                    'ステップ3（具体的な手順）',
                    '注意点・よくある失敗',
                    'まとめ（次のアクション）'
                ]
            },
            'listicle': {
                'name': 'リスト記事',
                'structure': [
                    '導入（なぜこのリストが重要か）',
                    'ポイント1（詳細説明）',
                    'ポイント2（詳細説明）',
                    'ポイント3（詳細説明）',
                    'ポイント4（詳細説明）',
                    'ポイント5（詳細説明）',
                    'まとめ（実践のためのアドバイス）'
                ]
            },
            'case-study': {
                'name': 'ケーススタディ',
                'structure': [
                    '導入（背景説明）',
                    '課題・問題点',
                    '解決策の検討',
                    '実施内容',
                    '結果・成果',
                    '学んだこと・教訓',
                    '読者へのアドバイス'
                ]
            },
            'comparison': {
                'name': '比較記事',
                'structure': [
                    '導入（比較の必要性）',
                    '比較項目の説明',
                    '選択肢1の詳細',
                    '選択肢2の詳細',
                    '選択肢3の詳細',
                    '比較表・まとめ',
                    '選び方のポイント',
                    '推奨事項'
                ]
            },
            'custom': {
                'name': 'カスタム構成',
                'structure': []
            }
        }
        return templates
    
    def display_header(self):
        """ヘッダー表示"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}📝 インタラクティブ記事作成ツール")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def get_basic_info(self):
        """基本情報の入力"""
        print(f"{Fore.YELLOW}📌 ステップ1: 基本情報の入力")
        
        # タイトルの入力
        print(f"\n{Fore.GREEN}記事のタイトルを入力してください（後で修正可能）:")
        self.post_data['title'] = input("> ").strip()
        
        # カテゴリの選択
        categories = [
            '起業', 'AI', 'マーケティング', '経営', 
            'フリーランス', '資金調達', 'テクノロジー'
        ]
        questions = [
            inquirer.Checkbox('categories',
                            message='カテゴリを選択してください（複数選択可）',
                            choices=categories)
        ]
        answers = inquirer.prompt(questions)
        self.post_data['categories'] = answers['categories']
        
        # タグの入力
        print(f"\n{Fore.GREEN}タグを入力してください（カンマ区切り）:")
        tags_input = input("> ").strip()
        self.post_data['tags'] = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    def choose_template(self):
        """記事構成テンプレートの選択"""
        print(f"\n{Fore.YELLOW}📐 ステップ2: 記事構成の選択")
        
        choices = [(v['name'], k) for k, v in self.templates.items()]
        questions = [
            inquirer.List('template',
                         message='記事の構成テンプレートを選択してください',
                         choices=choices)
        ]
        answers = inquirer.prompt(questions)
        
        template_key = answers['template']
        
        if template_key == 'custom':
            # カスタム構成の作成
            print(f"\n{Fore.GREEN}カスタム構成を作成します。セクションを入力してください（空行で終了）:")
            sections = []
            while True:
                section = input(f"セクション{len(sections)+1}: ").strip()
                if not section:
                    break
                sections.append(section)
            self.post_data['outline'] = sections
        else:
            self.post_data['outline'] = self.templates[template_key]['structure'].copy()
            
            # 構成の確認と編集
            print(f"\n{Fore.CYAN}選択された構成:")
            for i, section in enumerate(self.post_data['outline'], 1):
                print(f"  {i}. {section}")
            
            if input(f"\n{Fore.GREEN}この構成を編集しますか？ (y/n): ").lower() == 'y':
                self.edit_outline()
    
    def edit_outline(self):
        """アウトラインの編集"""
        while True:
            print(f"\n{Fore.CYAN}現在の構成:")
            for i, section in enumerate(self.post_data['outline'], 1):
                print(f"  {i}. {section}")
            
            print(f"\n{Fore.GREEN}編集オプション:")
            print("  1. セクションを追加")
            print("  2. セクションを削除")
            print("  3. セクションを編集")
            print("  4. 完了")
            
            choice = input("選択してください (1-4): ").strip()
            
            if choice == '1':
                section = input("新しいセクション: ").strip()
                if section:
                    self.post_data['outline'].append(section)
            elif choice == '2':
                idx = int(input("削除するセクション番号: ")) - 1
                if 0 <= idx < len(self.post_data['outline']):
                    del self.post_data['outline'][idx]
            elif choice == '3':
                idx = int(input("編集するセクション番号: ")) - 1
                if 0 <= idx < len(self.post_data['outline']):
                    new_section = input(f"新しい内容 (現在: {self.post_data['outline'][idx]}): ").strip()
                    if new_section:
                        self.post_data['outline'][idx] = new_section
            elif choice == '4':
                break
    
    def write_content(self):
        """コンテンツの作成"""
        print(f"\n{Fore.YELLOW}✍️  ステップ3: コンテンツの作成")
        
        content_sections = []
        
        for i, section in enumerate(self.post_data['outline'], 1):
            print(f"\n{Fore.CYAN}セクション {i}/{len(self.post_data['outline'])}: {section}")
            print(f"{Fore.GREEN}このセクションの内容を入力してください（AIサポートが必要な場合は'AI'と入力）:")
            
            user_input = input("> ").strip()
            
            if user_input.lower() == 'ai':
                # AIによる執筆支援
                print(f"{Fore.GREEN}どのような内容を書きたいか、キーワードや要点を入力してください:")
                prompt_input = input("> ").strip()
                
                ai_content = self.generate_section_content(section, prompt_input)
                print(f"\n{Fore.CYAN}AIが生成した内容:")
                print(ai_content)
                
                if input(f"\n{Fore.GREEN}この内容を使用しますか？ (y/n/edit): ").lower() == 'edit':
                    print("内容を編集してください（Ctrl+Dで終了）:")
                    edited_content = []
                    try:
                        while True:
                            line = input()
                            edited_content.append(line)
                    except EOFError:
                        pass
                    content_sections.append(f"## {section}\n\n" + '\n'.join(edited_content))
                elif input().lower() == 'y':
                    content_sections.append(f"## {section}\n\n" + ai_content)
                else:
                    # 手動で入力
                    print("内容を入力してください（Ctrl+Dで終了）:")
                    manual_content = []
                    try:
                        while True:
                            line = input()
                            manual_content.append(line)
                    except EOFError:
                        pass
                    content_sections.append(f"## {section}\n\n" + '\n'.join(manual_content))
            else:
                # 手動入力された内容を使用
                print("続きを入力してください（Ctrl+Dで終了）:")
                manual_content = [user_input]
                try:
                    while True:
                        line = input()
                        manual_content.append(line)
                except EOFError:
                    pass
                content_sections.append(f"## {section}\n\n" + '\n'.join(manual_content))
        
        self.post_data['content'] = '\n\n'.join(content_sections)
    
    def generate_section_content(self, section: str, keywords: str) -> str:
        """AIによるセクションコンテンツ生成"""
        prompt = f"""
「{self.post_data['title']}」という記事の「{section}」セクションを書いてください。

キーワード・要点: {keywords}

読者: 起業家、経営者、フリーランス
文体: プロフェッショナルで親しみやすい「です・ます調」
長さ: 300-500文字程度（全体で2000文字以上になるように）

以下を必ず含めてください：
- 具体的な事例やデータ
- 実践的なアドバイス
- 読者が今すぐ実行できるアクション
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはビジネスブログの執筆をサポートするライターです。読者に価値を提供する充実した内容を書きます。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    def add_images(self):
        """画像の追加"""
        print(f"\n{Fore.YELLOW}🖼️  ステップ4: 画像の追加")
        
        # 画像追加方法の選択
        print(f"\n{Fore.GREEN}画像の追加方法を選択してください:")
        choices = [
            ('Unsplashから検索', 'unsplash'),
            ('ローカルファイルから選択', 'local'),
            ('スキップ', 'skip')
        ]
        questions = [
            inquirer.List('method',
                         message='画像の追加方法',
                         choices=choices)
        ]
        answer = inquirer.prompt(questions)
        
        if answer['method'] == 'skip':
            return
        
        # サムネイル画像の設定
        print(f"\n{Fore.CYAN}サムネイル画像の設定")
        if answer['method'] == 'unsplash':
            print(f"{Fore.GREEN}検索キーワードを入力してください:")
            thumbnail_query = input("> ").strip()
            if thumbnail_query:
                thumbnail = self.search_and_select_image(thumbnail_query, is_thumbnail=True)
                if thumbnail:
                    self.post_data['thumbnail'] = thumbnail
        else:
            # ローカルファイルから選択
            print(f"{Fore.GREEN}サムネイル画像のパスを入力してください（ドラッグ&ドロップ可）:")
            thumbnail_path = input("> ").strip().replace("'", "").replace('"', '')
            if thumbnail_path and os.path.exists(thumbnail_path):
                self.post_data['thumbnail'] = {
                    'type': 'local',
                    'path': thumbnail_path,
                    'alt': input(f"{Fore.GREEN}alt属性のテキストを入力してください: ").strip()
                }
        
        # 本文内画像の追加
        if input(f"\n{Fore.GREEN}本文内に画像を追加しますか？ (y/n): ").lower() == 'y':
            while True:
                if answer['method'] == 'unsplash':
                    print(f"\n{Fore.GREEN}画像の検索キーワードを入力してください（空行で終了）:")
                    query = input("> ").strip()
                    
                    if not query:
                        break
                    
                    image = self.search_and_select_image(query, is_thumbnail=False)
                else:
                    print(f"\n{Fore.GREEN}画像ファイルのパスを入力してください（空行で終了）:")
                    image_path = input("> ").strip().replace("'", "").replace('"', '')
                    
                    if not image_path:
                        break
                    
                    if os.path.exists(image_path):
                        image = {
                            'type': 'local',
                            'path': image_path,
                            'alt': input(f"{Fore.GREEN}alt属性のテキストを入力してください: ").strip()
                        }
                    else:
                        print(f"{Fore.RED}ファイルが見つかりません: {image_path}")
                        continue
                
                if image:
                    # どのセクションの後に挿入するか選択
                    print(f"\n{Fore.CYAN}画像を挿入する位置を選択してください:")
                    for i, section in enumerate(self.post_data['outline'], 1):
                        print(f"  {i}. {section}の後")
                    
                    position = int(input("番号を選択: ")) - 1
                    if 0 <= position < len(self.post_data['outline']):
                        image['position'] = position
                        self.post_data['images'].append(image)
    
    def search_and_select_image(self, query: str, is_thumbnail: bool = False) -> Optional[Dict]:
        """Unsplash画像の検索と選択"""
        if not UNSPLASH_ACCESS_KEY:
            print(f"{Fore.RED}Unsplash APIキーが設定されていません。")
            return None
        
        print(f"{Fore.CYAN}画像を検索中...")
        
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 5,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('results'):
                print(f"{Fore.RED}画像が見つかりませんでした。")
                return None
            
            # 画像の選択肢を表示
            print(f"\n{Fore.CYAN}検索結果:")
            choices = []
            for i, photo in enumerate(data['results'], 1):
                description = photo.get('description') or photo.get('alt_description', '説明なし')
                choice_text = f"{i}. {description[:50]}... (by {photo['user']['name']})"
                choices.append((choice_text, i-1))
            choices.append(("キャンセル", -1))
            
            questions = [
                inquirer.List('selection',
                             message='使用する画像を選択してください',
                             choices=choices)
            ]
            answer = inquirer.prompt(questions)
            
            if answer['selection'] == -1:
                return None
            
            selected_photo = data['results'][answer['selection']]
            
            # 画像情報を整理
            image_info = {
                'url': selected_photo['urls']['regular'],
                'download_url': selected_photo['links']['download_location'],
                'author': selected_photo['user']['name'],
                'author_url': selected_photo['user']['links']['html'],
                'description': selected_photo.get('description', selected_photo.get('alt_description', '')),
                'width': selected_photo['width'],
                'height': selected_photo['height']
            }
            
            if is_thumbnail:
                # サムネイル用の処理
                print(f"{Fore.GREEN}alt属性のテキストを入力してください:")
                image_info['alt'] = input("> ").strip() or image_info['description']
            
            return image_info
            
        except Exception as e:
            print(f"{Fore.RED}画像検索エラー: {e}")
            return None
    
    def review_and_optimize(self):
        """レビューと最適化"""
        print(f"\n{Fore.YELLOW}🔍 ステップ5: レビューと最適化")
        
        # AI文章校正
        if input(f"\n{Fore.GREEN}AI文章校正を実行しますか？ (y/n): ").lower() == 'y':
            print(f"{Fore.CYAN}文章を分析中...")
            suggestions = self.ai_proofreading()
            
            if suggestions:
                print(f"\n{Fore.CYAN}改善提案:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
        
        # SEOメタディスクリプション生成
        print(f"\n{Fore.GREEN}メタディスクリプションを生成します...")
        self.post_data['meta_description'] = self.generate_meta_description()
        print(f"{Fore.CYAN}生成されたメタディスクリプション:")
        print(self.post_data['meta_description'])
        
        custom_desc = input(f"\n{Fore.GREEN}カスタマイズしますか？ (Enter でスキップ): ").strip()
        if custom_desc:
            self.post_data['meta_description'] = custom_desc
        
        # タイトルの最適化提案
        print(f"\n{Fore.GREEN}タイトルの最適化提案を生成しています...")
        title_suggestions = self.suggest_optimized_titles()
        
        print(f"\n{Fore.CYAN}タイトル最適化提案:")
        print(f"現在のタイトル: {self.post_data['title']}")
        for i, title in enumerate(title_suggestions, 1):
            print(f"{i}. {title}")
        
        choice = input(f"\n{Fore.GREEN}タイトルを変更しますか？ (番号を選択、Enterでスキップ): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(title_suggestions):
            self.post_data['title'] = title_suggestions[int(choice)-1]
    
    def ai_proofreading(self) -> List[str]:
        """AI文章校正"""
        prompt = f"""
以下の記事を校正し、改善提案をしてください：

タイトル: {self.post_data['title']}

本文:
{self.post_data['content'][:2000]}...

以下の観点で分析してください：
1. 文章の読みやすさ
2. 論理的な流れ
3. 専門用語の適切な使用
4. 誤字脱字
5. SEOの観点

改善提案を5個以内でリスト形式で出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはプロの編集者です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        # 改善提案をリスト化
        suggestions = [line.strip() for line in content.split('\n') if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))]
        return suggestions[:5]
    
    def generate_meta_description(self) -> str:
        """メタディスクリプション生成"""
        prompt = f"""
以下の記事のメタディスクリプションを作成してください：

タイトル: {self.post_data['title']}
カテゴリ: {', '.join(self.post_data['categories'])}
本文冒頭: {self.post_data['content'][:500]}

要件：
- 120-155文字
- 記事の内容を的確に要約
- 読者がクリックしたくなる内容
- 主要キーワードを含める

メタディスクリプションのみを出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはSEOスペシャリストです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    def suggest_optimized_titles(self) -> List[str]:
        """最適化されたタイトル候補を提案"""
        prompt = f"""
現在のタイトル「{self.post_data['title']}」をSEO最適化してください。

記事の内容：
{self.post_data['content'][:500]}

要件：
- 25-35文字
- 検索されやすいキーワードを含む
- クリック率を高める要素（数字、メリット、感情的訴求）を含む
- 3つの改善案を提示

改善案のみを1行ずつ出力してください。
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはSEOとコピーライティングの専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        titles = [line.strip() for line in content.split('\n') if line.strip()]
        return titles[:3]
    
    def save_post(self):
        """記事の保存"""
        print(f"\n{Fore.YELLOW}💾 ステップ6: 記事の保存")
        
        # ファイル名の生成
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename_base = re.sub(r'[^\w\s-]', '', self.post_data['title'])
        filename_base = re.sub(r'[-\s]+', '-', filename_base)[:30].lower()
        filename = f"{date_str}-{filename_base}.md"
        
        # フロントマター
        frontmatter = {
            'layout': 'post',
            'title': self.post_data['title'],
            'categories': self.post_data['categories'],
            'tags': self.post_data['tags'],
            'author': 'Kevin',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': self.post_data['meta_description']
        }
        
        # サムネイル画像の処理
        if self.post_data['thumbnail']:
            if self.post_data['thumbnail'].get('type') == 'local':
                # ローカル画像の最適化
                try:
                    _, info = self.image_optimizer.optimize_image(
                        self.post_data['thumbnail']['path'],
                        f"{filename_base}-thumb.jpg",
                        is_thumbnail=True
                    )
                    frontmatter['image'] = info['optimized_path']
                    frontmatter['image_alt'] = self.post_data['thumbnail'].get('alt', '')
                    print(f"{Fore.GREEN}サムネイル画像を最適化しました（圧縮率: {info['compression_ratio']}%）")
                except Exception as e:
                    print(f"{Fore.RED}サムネイル画像の最適化に失敗: {e}")
            else:
                # Unsplash画像のダウンロード
                thumbnail_path = self.download_and_optimize_image(
                    self.post_data['thumbnail'], 
                    filename_base, 
                    is_thumbnail=True
                )
                if thumbnail_path:
                    frontmatter['image'] = thumbnail_path
                    frontmatter['image_alt'] = self.post_data['thumbnail'].get('alt', '')
                    frontmatter['image_credit'] = f'Photo by <a href="{self.post_data["thumbnail"]["author_url"]}?utm_source=unsplash&utm_medium=referral">{self.post_data["thumbnail"]["author"]}</a> on <a href="https://unsplash.com?utm_source=unsplash&utm_medium=referral">Unsplash</a>'
        
        # コンテンツに画像を挿入
        content_with_images = self.insert_images_into_content()
        
        # 文字数チェック
        content_length = len(content_with_images)
        if content_length < 2000:
            print(f"\n{Fore.YELLOW}⚠️  現在の文字数: {content_length}文字（推奨: 2000文字以上）")
            if input(f"{Fore.GREEN}文字数を増やすために追加セクションを作成しますか？ (y/n): ").lower() == 'y':
                self.add_additional_sections()
                content_with_images = self.insert_images_into_content()
        else:
            print(f"\n{Fore.GREEN}✓ 文字数: {content_length}文字")
        
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
        
        print(f"\n{Fore.GREEN}✅ 記事が保存されました: {filepath}")
        
        # プレビューの表示
        print(f"\n{Fore.CYAN}プレビューを表示するには以下のコマンドを実行してください:")
        print(f"bundle exec jekyll serve --drafts")
    
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
                img = self.resize_image(img, 1200, 630)
                quality = 85
            else:
                # 本文画像は最大幅1200pxに制限
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                quality = 90
            
            # 保存
            assets_dir = os.path.join('assets', 'img', 'posts')
            os.makedirs(assets_dir, exist_ok=True)
            
            if is_thumbnail:
                image_filename = f"{filename_base}-thumb.jpg"
            else:
                timestamp = datetime.now().strftime('%H%M%S')
                image_filename = f"{filename_base}-{timestamp}.jpg"
            
            image_path = os.path.join(assets_dir, image_filename)
            
            # RGB変換（RGBA画像の場合）
            if img.mode in ('RGBA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            return f"/assets/img/posts/{image_filename}"
            
        except Exception as e:
            print(f"{Fore.RED}画像の処理中にエラーが発生しました: {e}")
            return None
    
    def resize_image(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """画像を指定サイズにリサイズ（アスペクト比を維持してクロップ）"""
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
    
    def add_additional_sections(self):
        """追加セクションの作成"""
        print(f"\n{Fore.CYAN}追加セクションを作成します。")
        
        suggestions = [
            "よくある質問（FAQ）",
            "実践例・ケーススタディ",
            "チェックリスト・実行ステップ",
            "関連リソース・参考文献",
            "専門家のアドバイス",
            "読者の声・体験談"
        ]
        
        print(f"{Fore.GREEN}追加したいセクションを選んでください（複数選択可、空行で終了）:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        while True:
            choice = input("番号を選択（または独自のセクション名）: ").strip()
            if not choice:
                break
            
            if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                section_name = suggestions[int(choice)-1]
            else:
                section_name = choice
            
            self.post_data['outline'].append(section_name)
            
            print(f"\n{Fore.CYAN}セクション: {section_name}")
            print(f"{Fore.GREEN}内容を入力してください（AIサポートが必要な場合は'AI'と入力）:")
            
            user_input = input("> ").strip()
            
            if user_input.lower() == 'ai':
                print(f"{Fore.GREEN}このセクションで書きたい内容のキーワードを入力してください:")
                prompt_input = input("> ").strip()
                ai_content = self.generate_section_content(section_name, prompt_input)
                print(f"\n{Fore.CYAN}AIが生成した内容:")
                print(ai_content)
                
                if input(f"\n{Fore.GREEN}この内容を使用しますか？ (y/n): ").lower() == 'y':
                    self.post_data['content'] += f"\n\n## {section_name}\n\n{ai_content}"
                else:
                    print("手動で内容を入力してください（Ctrl+Dで終了）:")
                    manual_content = []
                    try:
                        while True:
                            line = input()
                            manual_content.append(line)
                    except EOFError:
                        pass
                    self.post_data['content'] += f"\n\n## {section_name}\n\n" + '\n'.join(manual_content)
            else:
                # 手動入力
                print("続きを入力してください（Ctrl+Dで終了）:")
                manual_content = [user_input] if user_input else []
                try:
                    while True:
                        line = input()
                        manual_content.append(line)
                except EOFError:
                    pass
                self.post_data['content'] += f"\n\n## {section_name}\n\n" + '\n'.join(manual_content)
    
    def insert_images_into_content(self) -> str:
        """コンテンツに画像を挿入"""
        content = self.post_data['content']
        sections = content.split('\n\n')
        
        # 画像を位置順にソート
        sorted_images = sorted(self.post_data['images'], key=lambda x: x.get('position', 999))
        
        # 各画像を適切な位置に挿入
        for i, image in enumerate(sorted_images):
            position = image.get('position', 0)
            # セクションの位置を計算（アウトラインに基づく）
            insert_index = min(position * 2 + 2 + i, len(sections))
            
            if image.get('type') == 'local':
                # ローカル画像の最適化
                try:
                    timestamp = datetime.now().strftime('%H%M%S')
                    title_clean = re.sub(r'[^\w\s-]', '', self.post_data['title'])[:30].lower()
                    filename = f"{title_clean}-{timestamp}-{i:02d}.jpg"
                    _, info = self.image_optimizer.optimize_image(
                        image['path'],
                        filename,
                        is_thumbnail=False
                    )
                    image_markdown = f"\n![{image.get('alt', '')}]({info['optimized_path']})\n"
                    print(f"{Fore.GREEN}画像を最適化しました（圧縮率: {info['compression_ratio']}%）")
                except Exception as e:
                    print(f"{Fore.RED}画像の最適化に失敗: {e}")
                    continue
            else:
                # Unsplash画像のダウンロード
                title_clean = re.sub(r'[^\w\s-]', '', self.post_data['title'])[:30].lower()
                image_path = self.download_and_optimize_image(image, 
                                                             title_clean,
                                                             is_thumbnail=False)
                if image_path:
                    image_markdown = f"\n![{image.get('description', '')}]({image_path})\n"
                    image_markdown += f'*Photo by [{image["author"]}]({image["author_url"]}?utm_source=unsplash&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=unsplash&utm_medium=referral)*\n'
                else:
                    continue
            
            sections.insert(insert_index, image_markdown)
        
        return '\n\n'.join(sections)
    
    def run(self):
        """メイン実行"""
        self.display_header()
        
        try:
            # 各ステップを実行
            self.get_basic_info()
            self.choose_template()
            self.write_content()
            self.add_images()
            self.review_and_optimize()
            self.save_post()
            
            print(f"\n{Fore.GREEN}🎉 記事作成が完了しました！")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  作成を中断しました。")
            if input("途中まで作成した内容を保存しますか？ (y/n): ").lower() == 'y':
                self.save_post()
        except Exception as e:
            print(f"\n{Fore.RED}❌ エラーが発生しました: {e}")

def main():
    """メイン処理"""
    if not os.environ.get('OPENAI_API_KEY'):
        print(f"{Fore.RED}エラー: OPENAI_API_KEY環境変数が設定されていません。")
        sys.exit(1)
    
    creator = InteractivePostCreator()
    creator.run()

if __name__ == "__main__":
    main()