# 実装計画書 (Implementation Plan) - YouTube 字幕 RAG 版

YouTubeの字幕データを直接取得し、ベクトルデータベースに保存して検索可能にする、シンプルで効率的なRAGシステムを構築します。

## 1. 開発環境のセットアップ
- **環境管理**: `mise` または `pyenv` による Python 3.10+ の使用。
- **依存ライブラリ**:
    - `youtube-transcript-api`: 字幕データの取得用。
    - `langchain-text-splitters`: テキストのチャンク分割用。
    - `langchain-openai`: ベクトル化（Embeddings）用。
    - `chromadb`: ローカル・ベクトルデータベース。
- **設定**: OpenAI APIキーを `.env` に設定。

## 2. インジェクション・パイプラインの実装 (`ingest`)
- **字幕取得**: `youtube-transcript-api` を使用し、指定したYouTube URL（動画ID）から字幕テキストを取得。
- **チャンク分割**: `RecursiveCharacterTextSplitter` を使い、タイムスタンプ情報を保持したままテキストを適切なサイズに分割。
- **ベクトル化・保存**: OpenAIの `text-embedding-3-small` モデルを使用してベクトル化し、`ChromaDB` に保存。
    - メタデータとして `video_id`, `start_time`, `url` (タイムスタンプ付き) を保持。

## 3. 検索機能の実装 (`search`)
- **クエリ処理**: ユーザーの自然言語クエリをベクトル化。
- **セマンティック検索**: `ChromaDB` から類似度の高いチャンクを検索。
- **結果表示**: 関連するテキスト、動画タイトル（可能であれば）、および「該当箇所への直接リンク（タイムスタンプ付きURL）」を表示。

## 4. 実行インターフェース (`main.py`)
- `main.py` に `ingest` と `search` を統合し、CLI引数で操作できるようにする。
- 例: `python main.py ingest "https://www.youtube.com/watch?v=..."`
- 例: `python main.py search "特定のトピックについての質問"`
