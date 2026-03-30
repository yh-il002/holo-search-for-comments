# YouTube Subtitle Search (Complete Free & Local RAG)

YouTubeの字幕データを取得し、ローカルの埋め込みモデルを使ってベクトル検索を行う、**完全無料・APIキー不要**なRAGシステムです。

## 特徴
- **完全無料**: OpenAI等の有料APIを一切使いません。
- **日本語対応**: 多言語に強い `multilingual-e5-small` モデルを採用。
- **タイムスタンプ連携**: 検索結果から該当シーンへの直接リンク（URL）を生成。
- **シンプルな構成**: `main.py` 一つで登録から検索まで完結。

## セットアップ

### 1. 依存関係のインストール
`pip` を使用して必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

※ 初回の実行時に、HuggingFaceから埋め込みモデル（約400MB）が自動的にダウンロードされます。

## 使い方

### 動画の登録 (Ingest)
YouTube URLを指定して、字幕データをローカルのベクトルDBに保存します。

```bash
./.venv/bin/python main.py ingest YouTube URL
```

### 字幕からの検索 (Search)
自然言語で動画内のシーンを検索します。

```bash
./.venv/bin/python main.py search "キーワード"
```

## 技術スタック
- **Transcript API**: `youtube-transcript-api`
- **Embeddings**: `intfloat/multilingual-e5-small` (HuggingFace)
- **Vector DB**: `ChromaDB`
- **Framework**: `LangChain`
