#!/usr/bin/env python3
"""
画像最適化ユーティリティ
ローカル画像の自動リサイズ・圧縮機能
"""

import os
import shutil
from PIL import Image
from typing import Tuple, Optional
import hashlib
from datetime import datetime

class ImageOptimizer:
    def __init__(self, max_width: int = 1000, quality: int = 85):
        """
        画像最適化クラス
        
        Args:
            max_width: 最大幅（デフォルト1000px）
            quality: JPEG品質（デフォルト85%）
        """
        self.max_width = max_width
        self.quality = quality
        self.assets_dir = os.path.join('assets', 'img', 'posts')
        os.makedirs(self.assets_dir, exist_ok=True)
    
    def optimize_image(self, 
                      source_path: str, 
                      target_filename: Optional[str] = None,
                      is_thumbnail: bool = False) -> Tuple[str, dict]:
        """
        画像を最適化して保存
        
        Args:
            source_path: 元画像のパス
            target_filename: 保存時のファイル名（省略時は自動生成）
            is_thumbnail: サムネイル画像かどうか
        
        Returns:
            (保存先パス, 画像情報の辞書)
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"画像ファイルが見つかりません: {source_path}")
        
        # 画像を開く
        with Image.open(source_path) as img:
            original_format = img.format
            original_size = os.path.getsize(source_path)
            original_dimensions = img.size
            
            # EXIF情報を保持（向きの情報など）
            exif = img.info.get('exif', b'')
            
            # 画像の向きを自動修正
            img = self._fix_orientation(img)
            
            # リサイズ処理
            if is_thumbnail:
                # サムネイルは1200x630（OGP対応）
                img = self._resize_for_thumbnail(img, 1200, 630)
                max_size = (1200, 630)
            else:
                # 通常画像は最大幅でリサイズ
                if img.width > self.max_width:
                    ratio = self.max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
                max_size = (self.max_width, int(img.height))
            
            # ファイル名の生成
            if not target_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_hash = hashlib.md5(source_path.encode()).hexdigest()[:8]
                ext = 'jpg' if original_format in ['JPEG', 'JPG'] else 'png'
                target_filename = f"img_{timestamp}_{file_hash}.{ext}"
            
            # 保存パスの生成
            save_path = os.path.join(self.assets_dir, target_filename)
            
            # RGB変換（必要な場合）
            if img.mode in ('RGBA', 'P'):
                if original_format == 'PNG' and img.mode == 'RGBA':
                    # PNG with transparencyはそのまま保存
                    img.save(save_path, 'PNG', optimize=True)
                else:
                    # その他はJPEGに変換
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        rgb_img.paste(img, mask=img.split()[-1])
                    else:
                        rgb_img.paste(img)
                    rgb_img.save(save_path, 'JPEG', 
                               quality=self.quality, 
                               optimize=True,
                               exif=exif if exif else None)
            else:
                # JPEGとして保存
                img.save(save_path, 'JPEG', 
                        quality=self.quality, 
                        optimize=True,
                        exif=exif if exif else None)
            
            # 圧縮後のファイルサイズ
            optimized_size = os.path.getsize(save_path)
            
            # 画像情報を返す
            info = {
                'original_path': source_path,
                'optimized_path': f"/assets/img/posts/{target_filename}",
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': round((1 - optimized_size / original_size) * 100, 1),
                'original_dimensions': original_dimensions,
                'optimized_dimensions': img.size,
                'format': img.format
            }
            
            return save_path, info
    
    def _fix_orientation(self, img: Image.Image) -> Image.Image:
        """EXIF情報に基づいて画像の向きを修正"""
        try:
            # EXIF情報から向きを取得
            exif = img._getexif()
            if exif:
                orientation = exif.get(0x0112)  # Orientation tag
                if orientation:
                    rotations = {
                        3: 180,
                        6: 270,
                        8: 90
                    }
                    if orientation in rotations:
                        img = img.rotate(rotations[orientation], expand=True)
        except:
            pass
        return img
    
    def _resize_for_thumbnail(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """サムネイル用にリサイズ（アスペクト比を維持してクロップ）"""
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
    
    def batch_optimize(self, image_paths: list, prefix: str = "") -> list:
        """複数画像を一括最適化"""
        results = []
        for i, path in enumerate(image_paths):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{prefix}_{timestamp}_{i:02d}.jpg" if prefix else None
                save_path, info = self.optimize_image(path, filename)
                results.append({
                    'success': True,
                    'path': info['optimized_path'],
                    'info': info
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_path': path
                })
        return results

def optimize_directory(source_dir: str, max_width: int = 1000, quality: int = 85):
    """
    ディレクトリ内のすべての画像を最適化
    
    Args:
        source_dir: 画像が含まれるディレクトリ
        max_width: 最大幅
        quality: JPEG品質
    """
    optimizer = ImageOptimizer(max_width=max_width, quality=quality)
    
    # 対応する画像形式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # ディレクトリ内の画像を検索
    image_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if os.path.splitext(file.lower())[1] in image_extensions:
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print("画像ファイルが見つかりませんでした。")
        return
    
    print(f"見つかった画像: {len(image_files)}枚")
    
    # 各画像を最適化
    total_original_size = 0
    total_optimized_size = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n処理中 ({i}/{len(image_files)}): {os.path.basename(image_path)}")
        
        try:
            save_path, info = optimizer.optimize_image(image_path)
            total_original_size += info['original_size']
            total_optimized_size += info['optimized_size']
            
            print(f"  元のサイズ: {info['original_size']:,} bytes")
            print(f"  最適化後: {info['optimized_size']:,} bytes")
            print(f"  圧縮率: {info['compression_ratio']}%")
            print(f"  寸法: {info['original_dimensions']} → {info['optimized_dimensions']}")
            
        except Exception as e:
            print(f"  エラー: {e}")
    
    # 合計結果を表示
    if total_original_size > 0:
        total_compression = (1 - total_optimized_size / total_original_size) * 100
        print(f"\n合計圧縮結果:")
        print(f"  元の合計サイズ: {total_original_size:,} bytes")
        print(f"  最適化後の合計: {total_optimized_size:,} bytes")
        print(f"  総圧縮率: {total_compression:.1f}%")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python image_optimizer.py <画像ファイルまたはディレクトリ>")
        print("  python image_optimizer.py <画像ファイル> [最大幅] [品質]")
        print("\n例:")
        print("  python image_optimizer.py photo.jpg")
        print("  python image_optimizer.py photo.jpg 800 90")
        print("  python image_optimizer.py ./images/")
        sys.exit(1)
    
    path = sys.argv[1]
    max_width = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 85
    
    if os.path.isfile(path):
        # 単一ファイルの処理
        optimizer = ImageOptimizer(max_width=max_width, quality=quality)
        try:
            save_path, info = optimizer.optimize_image(path)
            print(f"画像を最適化しました: {save_path}")
            print(f"圧縮率: {info['compression_ratio']}%")
            print(f"サイズ: {info['original_dimensions']} → {info['optimized_dimensions']}")
        except Exception as e:
            print(f"エラー: {e}")
    
    elif os.path.isdir(path):
        # ディレクトリの処理
        optimize_directory(path, max_width=max_width, quality=quality)
    
    else:
        print(f"エラー: {path} が見つかりません。")