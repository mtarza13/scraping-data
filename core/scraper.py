# File: core/scraper.py
import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, BrowserContext
from pydantic import BaseModel
import numpy as np
from utils.helpers import (
    rotate_proxy,
    generate_user_agent,
    detect_anti_bot,
    bypass_cloudflare,
    extract_with_ai
)

class ScrapeConfig(BaseModel):
    user_agents: List[str]
    proxy_services: Dict[str, str]
    retry_policy: Dict[str, int]
    extraction_rules: Dict[str, str]
    concurrency: int = 5
    throttle_delay: Tuple[float, float] = (0.5, 2.0)

class ScrapeResult(BaseModel):
    url: str
    data: Dict[str, List[str]]
    html: Optional[str] = None
    timestamp: float
    status: str

class AdvancedScraper:
    def __init__(
        self,
        config: ScrapeConfig,
        headless: bool = True,
        proxy_file: Optional[str] = None
    ):
        self.config = config
        self.headless = headless
        self.proxy_file = proxy_file
        self.proxies = self._load_proxies() if proxy_file else []
        self.visited = set()
        self.checkpoint = {}
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.playwright = None
        self.browser = None
        self.context = None

    def _load_proxies(self) -> List[str]:
        with open(self.proxy_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    async def _init_client(self) -> httpx.AsyncClient:
        headers = {
            'User-Agent': generate_user_agent(self.config.user_agents)
        }
        proxy = rotate_proxy(self.proxies) if self.proxies else None
        limits = httpx.Limits(
            max_connections=self.config.concurrency,
            max_keepalive_connections=5
        )
        return httpx.AsyncClient(
            headers=headers,
            transport=httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None,
            limits=limits,
            timeout=30.0
        )

    async def _init_browser(self) -> Tuple[BrowserContext, str]:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        user_agent = generate_user_agent(self.config.user_agents)
        self.context = await self.browser.new_context(user_agent=user_agent)
        return self.context, user_agent

    async def _fetch(self, url: str, retry: int = 0) -> Optional[ScrapeResult]:
        try:
            if not self.client:
                self.client = await self._init_client()
            delay = np.random.uniform(*self.config.throttle_delay)
            await asyncio.sleep(delay)
            resp = await self.client.get(url)
            if detect_anti_bot(resp.text):
                if not self.playwright:
                    await self._init_browser()
                data = await bypass_cloudflare(self.context, url)
                return ScrapeResult(
                    url=url,
                    data=data,
                    html=None,
                    timestamp=asyncio.get_event_loop().time(),
                    status="bypassed"
                )
            soup = BeautifulSoup(resp.text, 'html.parser')
            data = extract_with_ai(soup, self.config.extraction_rules)
            return ScrapeResult(
                url=url,
                data=data,
                html=resp.text,
                timestamp=asyncio.get_event_loop().time(),
                status="success"
            )
        except Exception as e:
            if retry < self.config.retry_policy['max_retries']:
                backoff = min(
                    self.config.retry_policy['base_delay'] * (2 ** retry),
                    self.config.retry_policy['max_delay']
                )
                await asyncio.sleep(backoff)
                return await self._fetch(url, retry + 1)
            self.logger.error(f"Failed after {retry} retries: {str(e)}")
            return ScrapeResult(
                url=url,
                data={},
                html=None,
                timestamp=asyncio.get_event_loop().time(),
                status=f"failed: {str(e)}"
            )

    async def run(self, start_url: str, checkpoint_file: str) -> List[ScrapeResult]:
        if Path(checkpoint_file).exists():
            with open(checkpoint_file, 'r') as f:
                self.checkpoint = json.load(f)
                self.visited = set(self.checkpoint.get('visited', []))
        try:
            results = []
            queue = [start_url]
            while queue:
                url = queue.pop(0)
                if url in self.visited:
                    continue
                self.visited.add(url)
                result = await self._fetch(url)
                if not isinstance(result, ScrapeResult):
                    result = ScrapeResult(
                        url=url,
                        data={},
                        html=None,
                        timestamp=asyncio.get_event_loop().time(),
                        status="failed: result not ScrapeResult"
                    )
                results.append(result)
                if result.status.startswith("success"):
                    links = result.data.get('links', [])
                    queue.extend(links[:self.config.concurrency])
                self.checkpoint['visited'] = list(self.visited)
                with open(checkpoint_file, 'w') as f:
                    json.dump(self.checkpoint, f)
            return results
        finally:
            await self._cleanup()

    async def _cleanup(self):
        if self.client:
            await self.client.aclose()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

