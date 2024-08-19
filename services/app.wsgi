import sys
import logging
from flask import Flask
# アプリケーションのディレクトリをPythonパスに追加
sys.path.insert(0, '/var/www/micro_app')
# Flaskアプリケーションのインポート
from services.products import app as application  # appはFlaskアプリケーションのインスタンスです
# ロギング設定（オプション）
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

