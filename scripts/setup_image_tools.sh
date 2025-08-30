#!/bin/bash

# 画像最適化ツールのセットアップスクリプト

echo "画像最適化ツールのセットアップを開始します..."

# Python3のインストール確認
if ! command -v python3 &> /dev/null; then
    echo "Python3がインストールされていません。"
    echo "Homebrewでインストールするには："
    echo "  brew install python3"
    exit 1
fi

# pipのアップグレード
echo "pipをアップグレードしています..."
python3 -m pip install --upgrade pip

# 必要なパッケージのインストール
echo "必要なパッケージをインストールしています..."
python3 -m pip install -r scripts/requirements.txt

echo ""
echo "セットアップが完了しました！"
echo ""
echo "使い方："
echo "1. インタラクティブ記事作成ツール："
echo "   python3 scripts/create_post_interactive.py"
echo ""
echo "2. 画像最適化ツール（単体）："
echo "   python3 scripts/image_optimizer.py <画像ファイル>"
echo ""
echo "3. ディレクトリ内の全画像を最適化："
echo "   python3 scripts/image_optimizer.py <ディレクトリ>"