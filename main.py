import os
import argparse
import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

# 環境変数の読み込み (.env) - 現状は不要だが拡張性のために残す
load_dotenv()

# 無料で利用可能な軽量かつ高性能な多言語モデル
# intfloat/multilingual-e5-small: 日本語に強く、CPUでも高速
DEFAULT_EMBED_MODEL = "intfloat/multilingual-e5-small"

def extract_video_id(url: str) -> str:
    """YouTube URLから動画IDを抽出する"""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"無効なYouTube URLです: {url}")

def get_transcript(video_id: str) -> List[Dict]:
    """YouTubeの字幕を取得する"""
    try:
        # YouTubeTranscriptApiのインスタンスを作成
        api = YouTubeTranscriptApi()
        # 利用可能な字幕リストを取得
        transcript_list = api.list(video_id)
        # 日本語(ja)と英語(en)の順に字幕を探す
        transcript = transcript_list.find_transcript(['ja', 'en'])
        # 各スニペットを従来の辞書形式に変換して取得
        return [
            {'text': s.text, 'start': s.start, 'duration': s.duration} 
            for s in transcript.fetch()
        ]
    except Exception as e:
        print(f"字幕の取得に失敗しました: {e}")
        return []

def ingest_video(url: str, db_dir: str = "chroma_db"):
    """動画の字幕をベクトルDBに保存する"""
    video_id = extract_video_id(url)
    print(f"動画ID {video_id} の処理を開始します...")

    transcript = get_transcript(video_id)
    if not transcript:
        print("字幕が見つかりませんでした。")
        return

    # 字幕をテキストとタイムスタンプ付きのドキュメントに変換
    documents = []
    for entry in transcript:
        text = entry['text']
        start_time = entry['start']
        # メタデータに動画IDと開始時間を保持
        doc = Document(
            page_content=text,
            metadata={
                "video_id": video_id,
                "start_time": start_time,
                "url": f"https://youtu.be/{video_id}?t={int(start_time)}"
            }
        )
        documents.append(doc)

    print(f"埋め込みモデル ({DEFAULT_EMBED_MODEL}) をロード中...")
    # ローカルの埋め込みモデルを初期化 (初回のみダウンロードが発生)
    embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBED_MODEL)
    
    # ChromaDBに保存
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=db_dir,
        collection_name="youtube_transcripts"
    )
    
    print(f"動画ID {video_id} のインジェストが完了しました。")

def search_video(query: str, db_dir: str = "chroma_db", limit: int = 5):
    """自然言語クエリで関連シーンを検索する"""
    print(f"埋め込みモデル ({DEFAULT_EMBED_MODEL}) をロード中...")
    embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBED_MODEL)
    
    # ChromaDBの読み込み
    vector_store = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings,
        collection_name="youtube_transcripts"
    )
    
    # 類似度検索を実行 (scoreが低いほど類似)
    results = vector_store.similarity_search_with_relevance_scores(query, k=limit)
    
    print(f"\n検索クエリ: {query}")
    print("-" * 50)
    
    if not results:
        print("結果が見つかりませんでした。")
        return

    for doc, score in results:
        url = doc.metadata.get("url")
        start_time = doc.metadata.get("start_time")
        content = doc.page_content
        print(f"【関連度スコア: {score:.4f}】 {int(start_time)}秒付近")
        print(f"内容: {content}")
        print(f"URL: {url}")
        print("-" * 50)

def clear_db(db_dir: str = "chroma_db"):
    """ChromaDBのデータをクリアする"""
    import shutil
    if os.path.exists(db_dir):
        print(f"データベースディレクトリ {db_dir} を削除しています...")
        shutil.rmtree(db_dir)
        print("データベースをクリアしました。")
    else:
        print(f"データベースディレクトリ {db_dir} は存在しません。")

def main():
    parser = argparse.ArgumentParser(description="YouTube字幕 RAG システム (完全無料・ローカル版)")
    subparsers = parser.add_subparsers(dest="command", help="実行コマンド")

    # ingestコマンド
    ingest_parser = subparsers.add_parser("ingest", help="YouTube動画を登録")
    ingest_parser.add_argument("url", help="YouTubeの動画URL")

    # searchコマンド
    search_parser = subparsers.add_parser("search", help="字幕から関連シーンを検索")
    search_parser.add_argument("query", help="検索クエリ")
    search_parser.add_argument("--limit", type=int, default=5, help="返却する結果の数")

    # clear-dbコマンド
    subparsers.add_parser("clear-db", help="ChromaDBのデータをクリア")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest_video(args.url)
    elif args.command == "search":
        search_video(args.query, limit=args.limit)
    elif args.command == "clear-db":
        clear_db()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
