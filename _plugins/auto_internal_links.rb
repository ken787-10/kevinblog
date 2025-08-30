# 自動内部リンク生成プラグイン
# 記事内のキーワードを自動的に関連記事へのリンクに変換

require 'yaml'

module Jekyll
  class AutoInternalLinks < Generator
    safe true
    priority :low

    def generate(site)
      # キーワードマッピングファイルを読み込み
      keywords_file = File.join(site.source, '_data', 'keywords.yml')
      @keywords = {}
      
      if File.exist?(keywords_file)
        @keywords = YAML.load_file(keywords_file) || {}
      end

      # すべての記事からキーワードを自動抽出
      extract_keywords_from_posts(site)

      # 各記事の内容を処理して内部リンクを追加
      site.posts.docs.each do |post|
        process_post_content(post, site)
      end
    end

    private

    def extract_keywords_from_posts(site)
      site.posts.docs.each do |post|
        # タイトルからキーワードを抽出
        title_keywords = extract_important_words(post.data['title'])
        
        # カテゴリとタグからキーワードを抽出
        categories = post.data['categories'] || []
        tags = post.data['tags'] || []
        
        # 記事URLとキーワードをマッピング
        post_url = post.url
        keywords_for_post = (title_keywords + categories + tags).uniq
        
        keywords_for_post.each do |keyword|
          @keywords[keyword] ||= []
          @keywords[keyword] << {
            'url' => post_url,
            'title' => post.data['title']
          } unless @keywords[keyword].any? { |k| k['url'] == post_url }
        end
      end
    end

    def extract_important_words(title)
      return [] unless title
      
      # 重要な単語を抽出（日本語対応）
      important_words = []
      
      # カタカナの専門用語を抽出
      important_words += title.scan(/[ァ-ヶー]+/)
      
      # 英数字の専門用語を抽出（2文字以上）
      important_words += title.scan(/[A-Za-z0-9]{2,}/)
      
      # 特定のキーワードパターン
      patterns = [
        /AI|人工知能/,
        /スタートアップ|起業/,
        /マーケティング|集客/,
        /資金調達|投資/,
        /SEO|検索エンジン/,
        /YouTube|動画/,
        /リーダーシップ|経営/
      ]
      
      patterns.each do |pattern|
        matches = title.scan(pattern)
        important_words += matches unless matches.empty?
      end
      
      important_words.map(&:to_s).uniq
    end

    def process_post_content(post, site)
      content = post.content
      current_url = post.url
      links_added = 0
      max_links_per_post = 5

      # キーワードを長さ順（長い順）にソート
      sorted_keywords = @keywords.keys.sort_by(&:length).reverse

      sorted_keywords.each do |keyword|
        next if links_added >= max_links_per_post
        
        # 同じ記事へのリンクは除外
        related_posts = @keywords[keyword].reject { |p| p['url'] == current_url }
        next if related_posts.empty?

        # 最も関連性の高い記事を選択
        target_post = related_posts.first

        # キーワードを内部リンクに置換（最初の1回のみ）
        if content.include?(keyword) && !content.include?("](#{target_post['url']})")
          # マークダウンリンクを作成
          link = "[#{keyword}](#{target_post['url']} \"#{target_post['title']}\")"
          
          # 正規表現で最初の出現箇所のみ置換
          content = content.sub(/(?<!\[)#{Regexp.escape(keyword)}(?!\])/, link)
          links_added += 1
        end
      end

      post.content = content
    end
  end
end