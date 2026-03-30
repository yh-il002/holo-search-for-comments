import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from main import ingest_video, search_video

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

mcp = FastMCP("youtube-subtitle-search")


@mcp.tool()
def ingest(url: str) -> str:
    """
    YouTubeの動画URLを受け取り、字幕をベクトルDBに登録します。
    登録後はsearchツールで検索できるようになります。

    Args:
        url: YouTubeの動画URL (例: https://www.youtube.com/watch?v=XXXXXXXXXXX)
    """
    try:
        ingest_video(url, db_dir=DB_DIR)
        return f"動画のインジェストが完了しました: {url}"
    except Exception as e:
        return f"エラー: {e}"


@mcp.tool()
def search(query: str, limit: int = 5) -> str:
    """
    自然言語クエリで登録済みYouTube動画の字幕を検索し、関連シーンとURLを返します。

    Args:
        query: 検索クエリ (例: 「量子コンピュータの仕組み」)
        limit: 返却する結果の最大件数 (デフォルト: 5)
    """
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
        from main import DEFAULT_EMBED_MODEL

        embeddings = HuggingFaceEmbeddings(model_name=DEFAULT_EMBED_MODEL)
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=embeddings,
            collection_name="youtube_transcripts"
        )

        results = vector_store.similarity_search_with_relevance_scores(query, k=limit)

        if not results:
            return "結果が見つかりませんでした。先にingestツールで動画を登録してください。"

        lines = [f"検索クエリ: {query}\n"]
        for i, (doc, score) in enumerate(results, 1):
            url = doc.metadata.get("url", "")
            start_time = int(doc.metadata.get("start_time", 0))
            content = doc.page_content
            lines.append(f"【{i}】関連度: {score:.4f} / {start_time}秒付近")
            lines.append(f"内容: {content}")
            lines.append(f"URL: {url}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"エラー: {e}"


if __name__ == "__main__":
    mcp.run()
