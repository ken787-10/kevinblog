#!/usr/bin/env python3
"""
SEO分析と改善提案ツール
ブログ記事のSEOスコアを分析し、改善提案を生成
"""

import os
import re
import json
import yaml
from typing import Dict, List, Tuple
from datetime import datetime
import frontmatter

class SEOAnalyzer:
    def __init__(self):
        self.seo_keywords = self.load_keywords()
        self.min_word_count = 1000
        self.max_word_count = 3000
        self.ideal_title_length = (25, 35)
        self.ideal_meta_desc_length = (120, 155)
    
    def load_keywords(self) -> Dict:
        """キーワードデータを読み込み"""
        keywords_file = '_data/keywords.yml'
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def analyze_post(self, filepath: str) -> Dict:
        """記事のSEO分析を実行"""
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        content = post.content
        metadata = post.metadata
        
        analysis = {
            'file': filepath,
            'title': metadata.get('title', ''),
            'score': 0,
            'issues': [],
            'suggestions': []
        }
        
        # タイトル分析
        title_score, title_issues = self.analyze_title(metadata.get('title', ''))
        analysis['score'] += title_score
        analysis['issues'].extend(title_issues)
        
        # メタディスクリプション分析
        meta_score, meta_issues = self.analyze_meta_description(metadata.get('description', ''))
        analysis['score'] += meta_score
        analysis['issues'].extend(meta_issues)
        
        # コンテンツ分析
        content_score, content_issues = self.analyze_content(content, metadata)
        analysis['score'] += content_score
        analysis['issues'].extend(content_issues)
        
        # 画像分析
        image_score, image_issues = self.analyze_images(content, metadata)
        analysis['score'] += image_score
        analysis['issues'].extend(image_issues)
        
        # 内部リンク分析
        link_score, link_issues = self.analyze_internal_links(content)
        analysis['score'] += link_score
        analysis['issues'].extend(link_issues)
        
        # 改善提案を生成
        analysis['suggestions'] = self.generate_suggestions(analysis['issues'])
        
        # スコアを100点満点に正規化
        analysis['score'] = min(100, max(0, analysis['score']))
        
        return analysis
    
    def analyze_title(self, title: str) -> Tuple[int, List[str]]:
        """タイトルのSEO分析"""
        score = 20  # 基本スコア
        issues = []
        
        if not title:
            return 0, ["タイトルが設定されていません"]
        
        title_length = len(title)
        
        # 長さチェック
        if title_length < self.ideal_title_length[0]:
            score -= 5
            issues.append(f"タイトルが短すぎます（{title_length}文字）。{self.ideal_title_length[0]}文字以上が推奨です")
        elif title_length > self.ideal_title_length[1]:
            score -= 5
            issues.append(f"タイトルが長すぎます（{title_length}文字）。{self.ideal_title_length[1]}文字以下が推奨です")
        
        # パワーワードチェック
        power_words = ['方法', 'コツ', '完全ガイド', '成功', '戦略', '実践', '解説']
        if any(word in title for word in power_words):
            score += 5
        else:
            issues.append("タイトルにパワーワード（方法、コツ、完全ガイドなど）が含まれていません")
        
        # 数字チェック
        if re.search(r'\d+', title):
            score += 5
        else:
            issues.append("タイトルに数字が含まれていません（例：5つの方法、10のコツ）")
        
        return score, issues
    
    def analyze_meta_description(self, description: str) -> Tuple[int, List[str]]:
        """メタディスクリプションの分析"""
        score = 15
        issues = []
        
        if not description:
            return 0, ["メタディスクリプションが設定されていません"]
        
        desc_length = len(description)
        
        if desc_length < self.ideal_meta_desc_length[0]:
            score -= 5
            issues.append(f"メタディスクリプションが短すぎます（{desc_length}文字）")
        elif desc_length > self.ideal_meta_desc_length[1]:
            score -= 5
            issues.append(f"メタディスクリプションが長すぎます（{desc_length}文字）")
        
        return score, issues
    
    def analyze_content(self, content: str, metadata: Dict) -> Tuple[int, List[str]]:
        """コンテンツのSEO分析"""
        score = 30
        issues = []
        
        # 文字数カウント
        word_count = len(content)
        if word_count < self.min_word_count:
            score -= 10
            issues.append(f"コンテンツが短すぎます（{word_count}文字）。{self.min_word_count}文字以上が推奨です")
        elif word_count > self.max_word_count:
            score -= 5
            issues.append(f"コンテンツが長すぎます（{word_count}文字）。{self.max_word_count}文字以下が推奨です")
        
        # 見出し構造チェック
        h2_count = len(re.findall(r'^##\s', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s', content, re.MULTILINE))
        
        if h2_count < 3:
            score -= 5
            issues.append(f"H2見出しが少なすぎます（{h2_count}個）。3個以上が推奨です")
        
        if h2_count > 0 and h3_count == 0:
            score -= 3
            issues.append("H3見出しが使用されていません。階層構造を作ることが推奨されます")
        
        # キーワード密度チェック
        if metadata.get('categories'):
            main_keyword = metadata['categories'][0]
            keyword_count = content.lower().count(main_keyword.lower())
            content_length = len(content)
            keyword_density = (keyword_count * len(main_keyword)) / content_length * 100
            
            if keyword_density < 0.5:
                score -= 5
                issues.append(f"主要キーワード「{main_keyword}」の出現頻度が低すぎます")
            elif keyword_density > 3:
                score -= 5
                issues.append(f"主要キーワード「{main_keyword}」の出現頻度が高すぎます（キーワードスタッフィング）")
        
        return score, issues
    
    def analyze_images(self, content: str, metadata: Dict) -> Tuple[int, List[str]]:
        """画像のSEO分析"""
        score = 15
        issues = []
        
        # アイキャッチ画像チェック
        if not metadata.get('image'):
            score -= 10
            issues.append("アイキャッチ画像が設定されていません")
        elif not metadata.get('image_alt'):
            score -= 5
            issues.append("アイキャッチ画像のalt属性が設定されていません")
        
        # 本文内の画像チェック
        images = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
        if len(images) == 0:
            score -= 5
            issues.append("本文内に画像が含まれていません")
        else:
            for alt_text, _ in images:
                if not alt_text:
                    issues.append("alt属性が空の画像があります")
                    break
        
        return score, issues
    
    def analyze_internal_links(self, content: str) -> Tuple[int, List[str]]:
        """内部リンクの分析"""
        score = 20
        issues = []
        
        # 内部リンクの検出
        internal_links = re.findall(r'\[([^\]]+)\]\((/[^)]+)\)', content)
        
        if len(internal_links) == 0:
            score -= 10
            issues.append("内部リンクが含まれていません")
        elif len(internal_links) < 3:
            score -= 5
            issues.append(f"内部リンクが少なすぎます（{len(internal_links)}個）。3個以上が推奨です")
        
        return score, issues
    
    def generate_suggestions(self, issues: List[str]) -> List[str]:
        """改善提案を生成"""
        suggestions = []
        
        for issue in issues:
            if "タイトルが短すぎます" in issue:
                suggestions.append("タイトルに具体的な数字や期待される結果を追加してください")
            elif "パワーワード" in issue:
                suggestions.append("「〜の方法」「成功する〜」「完全ガイド」などの訴求力のある言葉を追加してください")
            elif "メタディスクリプション" in issue:
                suggestions.append("記事の要約と読者が得られるメリットを120-155文字で記載してください")
            elif "内部リンク" in issue:
                suggestions.append("関連する他の記事へのリンクを3-5個追加してください")
            elif "H2見出し" in issue:
                suggestions.append("コンテンツを論理的なセクションに分け、各セクションにH2見出しを追加してください")
            elif "画像" in issue:
                suggestions.append("視覚的な説明やインフォグラフィックを追加して、読みやすさを向上させてください")
        
        return suggestions
    
    def generate_report(self, analyses: List[Dict]) -> str:
        """SEO分析レポートを生成"""
        report = "# SEO分析レポート\n\n"
        report += f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # サマリー
        total_score = sum(a['score'] for a in analyses)
        avg_score = total_score / len(analyses) if analyses else 0
        
        report += f"## サマリー\n"
        report += f"- 分析記事数: {len(analyses)}\n"
        report += f"- 平均SEOスコア: {avg_score:.1f}/100\n\n"
        
        # 各記事の詳細
        report += "## 記事別分析結果\n\n"
        
        for analysis in sorted(analyses, key=lambda x: x['score']):
            report += f"### {analysis['title']}\n"
            report += f"- ファイル: {analysis['file']}\n"
            report += f"- SEOスコア: {analysis['score']}/100\n"
            
            if analysis['issues']:
                report += f"- 問題点:\n"
                for issue in analysis['issues']:
                    report += f"  - {issue}\n"
            
            if analysis['suggestions']:
                report += f"- 改善提案:\n"
                for suggestion in analysis['suggestions']:
                    report += f"  - {suggestion}\n"
            
            report += "\n"
        
        return report

def main():
    """メイン処理"""
    analyzer = SEOAnalyzer()
    analyses = []
    
    # すべての記事を分析
    for root, dirs, files in os.walk('_posts'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                analysis = analyzer.analyze_post(filepath)
                analyses.append(analysis)
    
    # ドラフトも分析
    for root, dirs, files in os.walk('_drafts'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                analysis = analyzer.analyze_post(filepath)
                analyses.append(analysis)
    
    # レポート生成
    report = analyzer.generate_report(analyses)
    
    # レポートを保存
    with open('seo_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("SEO分析が完了しました。")
    print(f"レポートを seo_report.md に保存しました。")
    
    # 低スコアの記事を警告
    low_score_posts = [a for a in analyses if a['score'] < 70]
    if low_score_posts:
        print(f"\n警告: {len(low_score_posts)}個の記事のSEOスコアが70未満です:")
        for post in low_score_posts[:5]:
            print(f"  - {post['title']}: {post['score']}/100")

if __name__ == "__main__":
    main()