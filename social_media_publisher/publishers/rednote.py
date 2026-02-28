import logging
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BasePublisher
from ..models import PostContent

logger = logging.getLogger(__name__)

class RednotePublisher(BasePublisher):
    """Upload posts to Rednote using Selenium WebDriver."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.driver = None
        self._started = False

    def _init_driver(self, auth_config: Dict[str, Any]) -> bool:
        if self._started:
            return True
        
        logger.info("Starting WebDriver")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            profile_path = auth_config.get("profile_path")
            
            chrome_options = Options()
            if profile_path:
                chrome_options.add_argument(f"--user-data-dir={profile_path}")
                chrome_options.add_argument("--profile-directory=Default")
                logger.info(f"Using Chrome profile: {profile_path}")
            else:
                if self.config.get("selenium", {}).get("headless", True):
                    chrome_options.add_argument("--headless")

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if profile_path:
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''Object.defineProperty(navigator, 'webdriver', { get: () => undefined });'''
            })
            self._started = True
            logger.info("WebDriver initialized")
            return True
        except Exception as e:
            logger.error(f"WebDriver init failed: {e}")
            return False

    def login(self, auth_config: Dict[str, Any]) -> bool:
        if not self._init_driver(auth_config):
            return False

        profile_path = auth_config.get("profile_path")
        if profile_path:
            logger.info("Using Chrome profile - skipping cookie login")
            # We assume the profile is already logged in
            return True

        cookie_file = auth_config.get("cookie_file")
        if not cookie_file:
            logger.error("No cookie file or profile path provided for auth")
            return False
            
        cookie_path = Path(cookie_file)
        if not cookie_path.exists():
            logger.error(f"Cookie file not found: {cookie_file}")
            return False

        try:
            cookies = self._load_cookies(cookie_path)
            
            logger.info("Navigating directly to creator dashboard...")
            self.driver.get("https://creator.xiaohongshu.com")
            time.sleep(5)
            
            logger.info(f"Injecting {len(cookies)} cookies...")
            current_domain = "creator.xiaohongshu.com"
            count = 0
            for cookie in cookies:
                try:
                    if "name" not in cookie or "value" not in cookie:
                        continue
                    
                    cdomain = cookie.get("domain", "")
                    if cdomain.startswith("."):
                        pass
                    elif cdomain != current_domain and cdomain != "xiaohongshu.com":
                        continue
                        
                    self.driver.add_cookie(cookie)
                    count += 1
                except: pass
            
            logger.info(f"Successfully injected {count} relevant cookies")
            
            self.driver.refresh()
            logger.info("Page refreshed, verifying login...")
            time.sleep(12)
            
            if self._is_logged_in():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login verification failed")
                return False
        except Exception as e:
            logger.error(f"Login process failed: {e}")
            return False

    def _load_cookies(self, cookie_path: Path) -> List[Dict[str, Any]]:
        cookies = []
        try:
            with open(cookie_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                data = json.loads(content)
                raw_cookies = data if isinstance(data, list) else data.get("cookies", [])
                for c in raw_cookies:
                    sanitized = {}
                    if "name" in c: sanitized["name"] = c["name"]
                    if "value" in c: sanitized["value"] = c["value"]
                    if "domain" in c: sanitized["domain"] = c["domain"]
                    if "path" in c: sanitized["path"] = c["path"]
                    if "secure" in c: sanitized["secure"] = bool(c["secure"])
                    if "httpOnly" in c: sanitized["httpOnly"] = bool(c["httpOnly"])
                    if "expirationDate" in c:
                        try: sanitized["expiry"] = int(c["expirationDate"])
                        except: pass
                    elif "expiry" in c:
                        try: sanitized["expiry"] = int(c["expiry"])
                        except: pass
                    if "sameSite" in c:
                        ss = c["sameSite"]
                        if isinstance(ss, str) and ss.lower() in ("lax", "strict", "none"):
                            sanitized["sameSite"] = ss.lower().capitalize()
                    cookies.append(sanitized)
        except: pass
        return cookies

    def _is_logged_in(self) -> bool:
        try:
            indicators = [
                ".creator-header", "[class*='creator']",
                ".user-avatar", ".avatar", "[class*='avatar']"
            ]
            for sel in indicators:
                try:
                    if self.driver.find_elements("css selector", sel):
                        return True
                except: continue
            return False
        except: return False

    def publish(self, content: PostContent) -> bool:
        logger.info(f"Publishing to Rednote: {content.title}")
        if not self._started:
            logger.error("Publisher not started. Call login() first.")
            return False

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            wait = WebDriverWait(self.driver, 30)

            self.driver.get("https://creator.xiaohongshu.com/publish/publish?target=image")
            time.sleep(8)
            
            # 1. Image Upload
            if not content.image_paths:
                logger.error("No images available for upload")
                return False

            logger.info(f"Uploading {len(content.image_paths)} image(s)...")
            try:
                file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
                abs_paths = "\n".join([os.path.abspath(p) for p in content.image_paths])
                file_input.send_keys(abs_paths)
            except Exception as e:
                logger.error(f"Failed to upload images: {e}")
                self._capture_debug_page("image_upload_failed")
                return False

            time.sleep(15)

            # 2. Title
            try:
                title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".c-input_inner input.d-text, input[placeholder*='标题']")))
                self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", title_input, content.title)
            except Exception as e:
                logger.error(f"Failed to fill title: {e}")
                self._capture_debug_page("title_fill_failed")
                return False

            # 3. Body and Hashtags
            try:
                body_editor = self.driver.find_element(By.CSS_SELECTOR, "div.ProseMirror, [contenteditable='true']")
                
                paragraphs = [p for p in content.body.split("\n") if p.strip()]
                html_content = "".join([f"<p>{line}</p>" for line in paragraphs])
                html_content += "<p><br></p>"
                
                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", body_editor, html_content)
                time.sleep(1)
                
                if content.hashtags:
                    self.driver.execute_script("""
                        const el = arguments[0];
                        const range = document.createRange();
                        const sel = window.getSelection();
                        range.selectNodeContents(el);
                        range.collapse(false);
                        sel.removeAllRanges();
                        sel.addRange(range);
                        el.focus();
                    """, body_editor)
                    time.sleep(0.5)
                    
                    for tag in content.hashtags:
                        clean_tag = tag.strip().lstrip("#")
                        if not clean_tag: continue
                        body_editor.send_keys(f"#{clean_tag}")
                        time.sleep(1.5)
                        body_editor.send_keys(" ")
                        time.sleep(0.5)
                
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", body_editor)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", body_editor)
                
            except Exception as e:
                logger.error(f"Failed to fill body/hashtags: {e}")
                self._capture_debug_page("body_fill_failed")
                return False

            time.sleep(5)
            
            # 4. Submit
            submit_btn = self._find_submit_button()
            if not submit_btn:
                logger.error("Failed to locate submit button")
                return False

            try:
                time.sleep(10)
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
                time.sleep(2)
                
                try:
                    submit_btn.click()
                except:
                    self.driver.execute_script("arguments[0].click();", submit_btn)
                
                # Verification
                try:
                    wait = WebDriverWait(self.driver, 30)
                    wait.until(lambda d: "publish" not in d.current_url.lower())
                    result = True
                except:
                    page_text = self.driver.page_source
                    success_indicators = ["发布成功", "笔记发布成功"]
                    if any(indicator in page_text for indicator in success_indicators):
                        result = True
                    else:
                        result = "publish" not in self.driver.current_url.lower()
                
                return result
            except Exception as e:
                logger.error(f"Failed during submission: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            return False

    def _find_submit_button(self):
        from selenium.webdriver.common.by import By
        selectors = [
            (By.CSS_SELECTOR, "button.bg-red"),
            (By.XPATH, "//button[contains(.,'发布')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, ".publish-btn")
        ]
        for by, sel in selectors:
            try:
                btns = self.driver.find_elements(by, sel)
                for b in btns:
                    if b.is_displayed() and b.is_enabled():
                        return b
            except: continue
        return None

    def _capture_debug_page(self, name: str):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"{name}_{timestamp}.png")
        except: pass

    def cleanup(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
            except: pass
            self.driver = None
            self._started = False
