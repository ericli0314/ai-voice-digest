import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1",
)

MODEL = "deepseek-chat"


def _chat(prompt: str, max_tokens: int = 400, json_mode: bool = False) -> str:
    kwargs = dict(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.4,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content.strip()


def filter_relevant(articles: list[dict]) -> list[dict]:
    """Use DeepSeek to pick the most on-topic articles (max 30)."""
    listing = "\n".join(
        f"{i+1}. {a['title']} | {a['summary'][:180]}"
        for i, a in enumerate(articles)
    )
    prompt = f"""你是專注於Voice AI、AI Agent、對話式AI、AI客服領域的分析師。

以下是今天撈取的 {len(articles)} 篇文章。請選出與下列主題最相關的文章：
- Voice AI / Voice Bot / 語音AI
- AI Agent / Agentic AI
- AI客服 / AI聯絡中心 / Contact Center AI
- 統一通訊 UCC / CCaaS
- 對話式AI / Conversational AI
- 語音辨識、語音合成（TTS/STT）商業應用
- LLM用於客服、自動化、機器人流程

回傳JSON，格式：{{"relevant": [1, 3, 7, ...]}}（編號從1開始，最多30篇）
只回傳JSON，不要說明。

文章列表：
{listing}"""

    try:
        raw = _chat(prompt, max_tokens=300, json_mode=True)
        indices = json.loads(raw).get("relevant", [])
        selected = [articles[i - 1] for i in indices if 0 < i <= len(articles)]
        print(f"[summarizer] Filtered to {len(selected)} relevant articles")
        return selected
    except Exception as e:
        print(f"[summarizer] Filter error: {e} — keeping all")
        return articles[:30]


def summarize_article(article: dict) -> str:
    prompt = f"""請用2-3句繁體中文摘要以下文章，說明對Voice AI / AI Agent / AI客服產業的影響或重要性。
標題：{article['title']}
內容：{article['summary'][:600]}
只回傳摘要，不加說明。"""
    try:
        return _chat(prompt, max_tokens=180)
    except Exception as e:
        print(f"[summarizer] Article summary error: {e}")
        return ""


def generate_digest(articles: list[dict]) -> str:
    if not articles:
        return "今日無符合主題的相關新聞。"

    lines = "\n".join(
        f"- {a['title']}：{a.get('ai_summary', a['summary'][:100])}"
        for a in articles[:20]
    )
    prompt = f"""你是Voice AI與AI Agent產業分析師。
根據今日以下新聞，用繁體中文撰寫一份300字以內的產業趨勢摘要。
結構：
1. 今日最重要的1-2個發展
2. 值得關注的技術或商業趨勢
3. 對AI客服/UCC/CCaaS產業的潛在影響

今日文章：
{lines}

直接撰寫摘要，不要加標題或編號。"""

    try:
        return _chat(prompt, max_tokens=600)
    except Exception as e:
        print(f"[summarizer] Digest error: {e}")
        return "今日摘要生成失敗，請直接查看文章列表。"


def process(articles: list[dict]) -> tuple[list[dict], str]:
    relevant = filter_relevant(articles)
    for a in relevant:
        a["ai_summary"] = summarize_article(a)
    digest = generate_digest(relevant)
    return relevant, digest
