import random
import re
from typing import List, Dict
from bs4 import BeautifulSoup


def generate_user_agent(user_agents: List[str]) -> str:
    return random.choice(user_agents)


def rotate_proxy(proxies: List[str]) -> str:
    return random.choice(proxies)


def detect_anti_bot(html: str) -> bool:
    # كشف Cloudflare أو صفحات بها حماية
    return "cf-browser-verification" in html.lower() or "Attention Required" in html


def bypass_cloudflare(context, url: str) -> Dict[str, List[str]]:
    # استخدام playwright لتجاوز حماية Cloudflare
    async def fetch():
        page = await context.new_page()
        await page.goto(url)
        content = await page.content()
        await page.close()
        return extract_with_ai(BeautifulSoup(content, "html.parser"))
    import asyncio
    return asyncio.get_event_loop().run_until_complete(fetch())


def extract_with_ai(soup: BeautifulSoup, rules: Dict[str, str] = None) -> Dict[str, List[str]]:
    """
    يستخدم regex و BeautifulSoup لاستخراج الإيميلات، الهواتف، والروابط
    """
    text = soup.get_text()
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\s().-]{7,}\d", text)
    links = [a.get("href") for a in soup.find_all("a", href=True)]

    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "links": list(set(links))
    }

