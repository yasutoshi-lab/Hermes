"""Browser client for Hermes"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from typing import Optional
from loguru import logger


class BrowserClient:
    """ヘッドレスブラウザクライアント"""

    def __init__(
        self, headless: bool = True, stealth_mode: bool = True, timeout: int = 30
    ):
        self.headless = headless
        self.stealth_mode = stealth_mode
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None

    def _init_driver(self):
        """ドライバー初期化"""
        if self.stealth_mode:
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = uc.Chrome(options=options)
        else:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)

        self.driver.set_page_load_timeout(self.timeout)

    async def extract_text(self, url: str) -> str:
        """URLからテキスト抽出"""
        if not self.driver:
            self._init_driver()

        try:
            logger.info(f"Extracting text from: {url}", extra={"category": "WEB"})

            self.driver.get(url)

            # ページ読み込み待機
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # HTMLソース取得
            html = self.driver.page_source

            # BeautifulSoupでパース
            soup = BeautifulSoup(html, "html.parser")

            # スクリプト・スタイル削除
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # テキスト抽出
            text = soup.get_text(separator="\n", strip=True)

            # 空行削除
            lines = [line for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)

            logger.info(
                f"Text extracted: {len(clean_text)} chars",
                extra={"category": "WEB", "url": url},
            )

            return clean_text

        except Exception as e:
            logger.error(
                f"Text extraction failed: {e}", extra={"category": "WEB", "url": url}
            )
            return ""

    def close(self):
        """ブラウザクローズ"""
        if self.driver:
            self.driver.quit()
            self.driver = None
