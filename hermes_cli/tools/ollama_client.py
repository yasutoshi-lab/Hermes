"""Ollama API client for Hermes"""

import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
import asyncio
import json
import re


class OllamaClient:
    """Ollama API クライアント"""

    def __init__(
        self,
        api_url: str,
        model: str,
        timeout: int = 120,
        retry: int = 3,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self.api_url = api_url
        self.model = model
        self.timeout = timeout
        self.retry = retry
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = httpx.AsyncClient(timeout=timeout)

    async def chat(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """チャット実行"""
        for attempt in range(self.retry):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", self.temperature),
                        "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    },
                }

                logger.debug(
                    f"Ollama request attempt {attempt + 1}/{self.retry}",
                    extra={"category": "OLLAMA"},
                )

                response = await self.client.post(self.api_url, json=payload)
                response.raise_for_status()

                result = response.json()
                content = result["message"]["content"]

                logger.info(
                    f"Ollama response received",
                    extra={
                        "category": "OLLAMA",
                        "model": self.model,
                        "prompt_length": len(prompt),
                        "response_length": len(content),
                    },
                )

                return content

            except Exception as e:
                logger.warning(
                    f"Ollama request failed: {e}",
                    extra={"category": "OLLAMA", "attempt": attempt + 1},
                )
                if attempt == self.retry - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

        raise RuntimeError("Ollama request failed after all retries")

    async def generate_queries(self, prompt: str, num_queries: int = 3) -> List[str]:
        """検索クエリ生成"""
        system_prompt = """あなたは調査エージェントです。
ユーザーのプロンプトを分析し、効果的な検索クエリを生成してください。
各クエリは1行で、異なる観点から情報を集められるようにしてください。"""

        user_prompt = f"""以下のプロンプトに対して、{num_queries}個の検索クエリを生成してください：

{prompt}

各クエリを1行ずつ出力してください。"""

        response = await self.chat(user_prompt, system_prompt)
        queries = [q.strip() for q in response.strip().split("\n") if q.strip()]

        # 番号付きリストの場合は番号を削除
        cleaned_queries = []
        for q in queries:
            # "1. query" や "1) query" のパターンを削除
            cleaned = re.sub(r"^\d+[\.)]\s*", "", q)
            if cleaned:
                cleaned_queries.append(cleaned)

        return cleaned_queries[:num_queries]

    async def summarize(self, contents: List[str], prompt: str) -> str:
        """コンテンツ要約"""
        system_prompt = """あなたは情報整理の専門家です。
複数のソースから得られた情報を統合し、簡潔に要約してください。
矛盾する情報がある場合は両論を併記してください。"""

        combined = "\n\n---\n\n".join(contents)
        user_prompt = f"""元の質問: {prompt}

以下の情報を要約してください：

{combined}"""

        return await self.chat(user_prompt, system_prompt)

    async def validate(self, report: str, original_prompt: str) -> Dict[str, Any]:
        """レポート検証"""
        system_prompt = """あなたは品質管理の専門家です。
レポートを分析し、以下の観点で評価してください：
1. 矛盾や論理的誤りはないか
2. 元の質問に十分に答えているか
3. 追加調査が必要な点はないか

評価結果をJSON形式で返してください：
{
  "has_issues": true/false,
  "issues": ["問題点1", "問題点2", ...],
  "additional_queries": ["追加クエリ1", ...]
}"""

        user_prompt = f"""元の質問: {original_prompt}

レポート:
{report}

上記レポートを評価してください。"""

        response = await self.chat(user_prompt, system_prompt)

        # JSON抽出（LLMが余分なテキストを含む可能性を考慮）
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                logger.warning(
                    "Failed to parse validation JSON",
                    extra={"category": "OLLAMA"},
                )
                return {
                    "has_issues": False,
                    "issues": [],
                    "additional_queries": [],
                }
        else:
            return {"has_issues": False, "issues": [], "additional_queries": []}

    async def close(self):
        """クライアントクローズ"""
        await self.client.aclose()
