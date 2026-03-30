# 仕様策定書 (Specifications) - YouTube 字幕 RAG 版

YouTubeの字幕データをソースとした、タイムスタンプ付きRAGシステムの詳細なデータ構造、処理ロジック、およびインターフェース仕様を定義します。

## 1. データフロー詳細

### 1.1 字幕取得
1. ユーザーがYouTube URLを入力。
2. 動画IDをURLから抽出（例: `hOY9qw8cVlc`）。
3. `youtube-transcript-api` を呼び出し、タイムスタンプ付きの字幕リストを取得。
    - **出力例**: `[{ "start": 10.5, "duration": 4.7, "text": "こんにちは、今日はRAGについて話します。" }, ...]`

### 1.2 チャンク分割 (Chunking Strategy)
- **手法**: **Character-based Chunking with Metadata Propagation**。
- **詳細**:
    - 各字幕セグメントを結合し、約500-800文字程度のチャンクを作成。
    - チャンクのオーバーラップ（100-200文字）を設け、文脈の欠落を防止。
    - 各チャンクの**最初のセグメントの開始秒数（`start_time`）**をメタデータとして保持。

### 1.3 ベクトル化と保存
- チャンク化されたテキストを OpenAI `text-embedding-3-small` でベクトル化。
- `ChromaDB` に以下の情報を保存。

| フィールド名 | 型 | 説明 |
| :--- | :--- | :--- |
| `id` | string | 一意なID (video_id + chunk_index) |
| `text` | string | チャンク内のテキスト本文 |
| `video_id` | string | YouTubeの動画ID |
| `start_time` | float | チャンクの開始秒数 |
| `url` | string | `https://youtu.be/[video_id]?t=[int(start_time)]` |

## 2. ユーザーインターフェース (CLI) 仕様

### 2.1 `ingest` コマンド
新しいYouTube動画をシステムに登録します。
- **引数**: YouTube URL
- **処理**: 字幕取得 -> 分割 -> ベクトル化 -> Chroma保存。

### 2.2 `search` コマンド
自然言語クエリに基づき、関連する動画のシーンを検索します。
- **引数**: 検索クエリ文字列、最大結果数 (`limit`, デフォルト=5)
- **戻り値**:
    - 関連するテキスト、動画タイトル、再生位置URLのリスト。

## 3. 実装の簡略化ポイント
- サーバー（MCP等）を介さず、ローカルで完結する CLI スクリプトとして実装。
- 音声ファイルや一時ファイルのダウンロードを伴わないため、ストレージ使用量と実行時間を大幅に削減。
