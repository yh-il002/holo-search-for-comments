# YouTube Subtitle Search (Complete Free & Local RAG)

YouTubeの字幕データを取得し、ローカルの埋め込みモデルを使ってベクトル検索を行う、**完全無料・APIキー不要**なRAGシステムです。

## 特徴
- **完全無料**: OpenAI等の有料APIを一切使いません。
- **日本語対応**: 多言語に強い `multilingual-e5-small` モデルを採用。
- **タイムスタンプ連携**: 検索結果から該当シーンへの直接リンク（URL）を生成。
- **シンプルな構成**: `main.py` 一つで登録から検索まで完結。

## 仕組み

### このリポジトリでできること
- 動画の登録 (Ingest): YouTubeのURLを指定するだけで、その動画の全字幕データを取得し、検索可能な状態に保存します。
- シーン検索 (Search): 「〇〇について話しているシーン」のように自然言語で検索すると、関連する発言が含まれる箇所を特定します。
- タイムスタンプ連携: 検索結果として、該当するシーンから再生が始まるYouTubeのリンク（URL）を直接取得できます。
- 完全ローカル・無料: 外部の有料API（OpenAI等）を使用せず、PC内のリソースだけで完結します。

### 機能を利用できる仕組み（プロセス一覧）
- 字幕取得: youtube-transcript-api を使い、動画からタイムスタンプ付きのテキストデータを抽出します。
- チャンク分割: 長い字幕を適切な長さ（500〜800文字程度）の塊（チャンク）に分け、それぞれの開始時間を記録します。
- ベクトル化 (Embedding): 日本語に強いモデル（multilingual-e5-small）を用いて、テキストの意味を数値化（ベクトル化）します。
- ベクトルDB保存: 分割したテキストと数値を ChromaDB というローカルデータベースに保存します。
- 類似度検索: ユーザーの検索キーワードも同様にベクトル化し、データベース内のデータと照らし合わせて「意味が近いシーン」を上位から表示します。

## セットアップ

### 1. 依存関係のインストール
`pip` を使用して必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

※ 初回の実行時に、HuggingFaceから埋め込みモデル（約400MB）が自動的にダウンロードされます。

## コマンドラインからの使い方

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

### データベースのクリア (Clear-DB)
登録済みのデータをすべて削除して初期化します。

```bash
./.venv/bin/python main.py clear-db
```

## ClaudeデスクトップからMCPサーバーとして使用する方法

Claude DesktopなどのMCPクライアントから以下のツールを使用できます。

- **ingest** │ YouTube動画を登録    │ 「https://youtu.be/XXXXXXXXXXX を登録して」
- **search** │ 字幕を自然言語で検索 │ 「量子コンピュータの仕組みについて話しているシーンを探して」
- **clear**  │ データベースをクリア  │ 「データベースを初期化して」

### MCPサーバーの登録
- ~/Library/Application Support/Claude/claude_desktop_config.json

```bash
"mcpServers": {
  "youtube-subtitle-search": {
    "command": "/Users/username/test/holo-search-for-comments/.venv/bin/python",
    "args": ["/Users/username/test/holo-search-for-comments/mcp_server.py"]
  }
},
```

## 技術スタック
- **Transcript API**: `youtube-transcript-api`
- **Embeddings**: `intfloat/multilingual-e5-small` (HuggingFace)
- **Vector DB**: `ChromaDB`
- **Framework**: `LangChain`
