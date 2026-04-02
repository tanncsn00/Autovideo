"""TikTok Auto Publisher — Playwright-based direct upload.

User logs in once via browser → cookies saved → auto upload after that.
Handles TikTok's joyride overlay and anti-bot measures.
"""

import os
import json
import time as _time
from pathlib import Path
from app.plugins.base import PublisherPlugin, PluginMeta
from app.config.config import get_api_key
from loguru import logger


def _cookies_dir() -> Path:
    """Directory for TikTok cookies"""
    try:
        from app.config.config_v2 import get_config_dir
        d = get_config_dir() / "tiktok"
        d.mkdir(parents=True, exist_ok=True)
        return d
    except Exception:
        d = Path("tiktok_cookies")
        d.mkdir(parents=True, exist_ok=True)
        return d


def _cookies_path() -> Path:
    return _cookies_dir() / "tiktok_cookies.json"


def _remove_joyride(page):
    """Remove TikTok's joyride tutorial overlay that blocks clicks"""
    try:
        page.evaluate("""() => {
            const portal = document.getElementById('react-joyride-portal');
            if (portal) portal.remove();
            document.querySelectorAll('[class*="joyride"]').forEach(el => el.remove());
            document.querySelectorAll('[data-test-id="overlay"]').forEach(el => el.remove());
        }""")
    except Exception:
        pass  # Page may be navigating


def _launch_browser(playwright, cookies=None):
    """Launch browser with anti-detection and optional cookies"""
    browser = playwright.chromium.launch(
        headless=False,
        channel="msedge",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        viewport={"width": 1280, "height": 900},
    )
    # Inject anti-detection script
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.chrome = {runtime: {}};
    """)
    if cookies:
        context.add_cookies(cookies)
    return browser, context


class TikTokAutoPlugin(PublisherPlugin):

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            name="tiktok-auto",
            display_name="TikTok (Auto Upload)",
            version="3.0.0",
            description="Upload videos to TikTok automatically. Login once, upload forever.",
            author="MoneyPrinterTurbo",
            plugin_type="publisher",
            config_schema={
                "account_name": {"type": "string", "description": "Your TikTok username"},
            },
            builtin=True,
        )

    def validate_config(self, config: dict) -> bool:
        return True

    def is_available(self) -> bool:
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            return False

    async def authenticate(self, credentials: dict) -> bool:
        return self.is_logged_in()

    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list[str] = None,
        thumbnail_path: str = None,
        schedule_time: str = None,
        **kwargs,
    ) -> dict:
        """Upload video to TikTok using Playwright directly"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        account_name = get_api_key("tiktok_account_name") or kwargs.get("account_name", "")
        if not account_name:
            raise ValueError("TikTok account name not set. Go to Settings → Publishing and set your TikTok username.")

        if not self.is_logged_in():
            raise ValueError("Not logged in to TikTok. Go to Settings → Publishing and click Login.")

        # Load cookies
        cookies_file = _cookies_path()
        with open(cookies_file, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        caption = description or title
        hashtags = tags or []
        if hashtags:
            caption += " " + " ".join(f"#{t}" for t in hashtags)

        import concurrent.futures

        def _do_upload():
            from playwright.sync_api import sync_playwright

            logger.info(f"Uploading to TikTok: {video_path}")
            logger.info(f"Account: {account_name}, Caption: {caption[:80]}...")

            with sync_playwright() as p:
                browser, context = _launch_browser(p, cookies)
                page = context.new_page()

                try:
                    # Go to TikTok upload page
                    logger.info("Navigating to TikTok upload page...")
                    page.goto("https://www.tiktok.com/upload", timeout=60000, wait_until="domcontentloaded")

                    # Wait for redirects to settle (TikTok often redirects /upload → /creator-center/upload)
                    _time.sleep(5)

                    # Wait for page to be stable after any redirects
                    for attempt in range(10):
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=5000)
                            break
                        except Exception:
                            _time.sleep(1)

                    _remove_joyride(page)

                    # Check if we're redirected to login (cookies expired)
                    try:
                        current_url = page.url
                        logger.info(f"On page: {current_url}")
                    except Exception:
                        _time.sleep(3)
                        current_url = page.url
                        logger.info(f"On page (retry): {current_url}")

                    if "/login" in current_url:
                        browser.close()
                        raise ValueError("TikTok session expired. Please login again in Settings → Publishing.")

                    _time.sleep(2)
                    _remove_joyride(page)

                    # Find file input and upload video
                    logger.info("Looking for file input...")
                    file_input = page.locator('input[type="file"]').first
                    file_input.set_input_files(video_path)
                    logger.info("Video file selected, waiting for video to process...")

                    # Wait for video to finish uploading to TikTok servers
                    # TikTok shows a progress bar/percentage while uploading
                    # Wait for video to finish uploading to TikTok servers
                    # Track percentage text: "XX%" → when it disappears, upload is done
                    logger.info("Waiting for video to upload to TikTok servers...")
                    saw_progress = False
                    for i in range(120):  # Wait up to 6 minutes
                        _time.sleep(3)
                        _remove_joyride(page)
                        try:
                            progress_pct = page.evaluate("""() => {
                                const body = document.body.innerText;
                                const match = body.match(/(\\d+)\\s*%/);
                                return match ? parseInt(match[1]) : null;
                            }""")

                            if progress_pct is not None:
                                saw_progress = True
                                if i % 3 == 0:
                                    logger.info(f"Upload progress: {progress_pct}%")
                            elif saw_progress:
                                # Had progress before, now gone → upload finished
                                logger.info("Upload complete! (progress indicator gone)")
                                break
                            elif i >= 5:
                                # Never saw progress, waited 15s+ → might already be done
                                logger.info("No progress indicator found — assuming upload complete")
                                break

                        except Exception:
                            _time.sleep(1)
                            continue

                    # Extra wait for TikTok to process
                    _time.sleep(3)

                    _time.sleep(2)
                    _remove_joyride(page)

                    # Set caption/description
                    logger.info("Setting caption...")
                    _remove_joyride(page)

                    caption_editor = None
                    for selector in [
                        '[data-text="true"]',
                        '[contenteditable="true"]',
                        '.public-DraftEditor-content',
                        '[role="textbox"]',
                        '.notranslate',
                    ]:
                        try:
                            el = page.locator(selector).first
                            if el.is_visible(timeout=3000):
                                caption_editor = el
                                logger.info(f"Found caption editor: {selector}")
                                break
                        except Exception:
                            continue

                    if caption_editor:
                        try:
                            caption_editor.click()
                            _time.sleep(0.5)
                            page.keyboard.press("Control+a")
                            _time.sleep(0.3)
                            page.keyboard.press("Backspace")
                            _time.sleep(0.3)
                            page.keyboard.type(caption[:2200], delay=10)
                            logger.info("Caption set successfully")
                        except Exception as e:
                            logger.warning(f"Could not set caption: {e}")
                    else:
                        logger.warning("Caption editor not found, uploading without custom caption")

                    _time.sleep(2)
                    _remove_joyride(page)

                    # Wait for TikTok content checks to complete
                    logger.info("Waiting for TikTok content checks to complete...")
                    for check_i in range(120):  # Wait up to 10 minutes
                        _time.sleep(5)
                        _remove_joyride(page)
                        try:
                            checks_status = page.evaluate("""() => {
                                const body = document.body.innerText || '';
                                const hasChecking = body.includes('Checking in progress') ||
                                                    body.includes('checking in progress');
                                const hasIssues = body.includes('No issues found');
                                return { checking: hasChecking, passed: hasIssues };
                            }""")

                            if checks_status.get("checking"):
                                if check_i % 6 == 0:  # Log every 30s
                                    logger.info(f"Content checks still running... ({check_i*5}s)")
                                continue
                            elif checks_status.get("passed"):
                                logger.info("All content checks passed!")
                                break
                            else:
                                # No checks visible or already done
                                if check_i >= 3:  # Wait at least 15s
                                    logger.info("Content checks section not found — proceeding")
                                    break
                        except Exception:
                            if check_i >= 3:
                                break
                            continue

                    _time.sleep(2)

                    # Click the actual Post button (pink/red button at the bottom)
                    # Must be precise — "Post" text appears in many places on page
                    logger.info("Looking for Post button...")
                    _remove_joyride(page)

                    post_clicked = page.evaluate("""() => {
                        // Find the EXACT Post/Đăng submit button
                        // It's the pink/red button, usually last in the form actions
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {
                            const text = btn.textContent.trim();
                            // Must be exactly "Post" or "Đăng" (not "Repost", "When to post", etc.)
                            if (text === 'Post' || text === 'Đăng') {
                                // Check it looks like a submit button (has color/style)
                                const style = window.getComputedStyle(btn);
                                const bg = style.backgroundColor;
                                // Log for debugging
                                console.log('Found button:', text, 'bg:', bg, 'class:', btn.className);
                                btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                                return {found: true, text: text, clicked: false};
                            }
                        }
                        return {found: false};
                    }""")

                    if post_clicked and post_clicked.get("found"):
                        logger.info(f"Found Post button: '{post_clicked.get('text')}'")
                        _time.sleep(1)
                        # Now click it properly
                        page.evaluate("""() => {
                            const buttons = document.querySelectorAll('button');
                            for (const btn of buttons) {
                                const text = btn.textContent.trim();
                                if (text === 'Post' || text === 'Đăng') {
                                    btn.click();
                                    return true;
                                }
                            }
                            return false;
                        }""")
                        post_clicked = True
                        logger.info("Post button clicked!")
                    else:
                        browser.close()
                        raise RuntimeError("Could not find the Post button on TikTok upload page")

                    # Wait for TikTok to redirect away from upload page
                    logger.info("Post clicked, waiting for TikTok to redirect...")
                    upload_success = False
                    for i in range(180):  # Wait up to 6 minutes
                        _time.sleep(2)

                        try:
                            # Wait for page to be stable
                            page.wait_for_load_state("domcontentloaded", timeout=3000)
                        except Exception:
                            pass

                        try:
                            current_url = page.url
                            logger.info(f"[{i}] Current URL: {current_url}")
                        except Exception as e:
                            logger.warning(f"[{i}] Could not get URL: {e}")
                            _time.sleep(2)
                            continue

                        # SUCCESS: no longer on upload page
                        if "/upload" not in current_url and "tiktok" in current_url:
                            upload_success = True
                            logger.info(f"Post successful! Redirected to: {current_url}")
                            break

                        if i % 15 == 0 and i > 0:
                            logger.info(f"Still on upload page, waiting for redirect... ({i*2}s)")

                    # Save updated cookies
                    try:
                        new_cookies = context.cookies()
                        with open(str(cookies_file), "w", encoding="utf-8") as f:
                            json.dump(new_cookies, f, indent=2, ensure_ascii=False)
                        logger.info("Cookies updated after upload")
                    except Exception:
                        pass

                    # Wait before closing browser to let TikTok finish processing
                    logger.info("Waiting 5s before closing browser...")
                    _time.sleep(5)
                    browser.close()

                    if upload_success:
                        return {"status": "published", "message": "Video uploaded to TikTok"}
                    else:
                        logger.warning("Upload may have succeeded but no confirmation detected")
                        return {"status": "unknown", "message": "Upload submitted but confirmation not detected"}

                except Exception as e:
                    browser.close()
                    raise e

        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(_do_upload)
                result = future.result(timeout=600)  # 10 min timeout

            logger.info(f"TikTok upload result: {result}")
            return {
                "platform": "tiktok",
                "status": result.get("status", "unknown"),
                "result": result.get("message", ""),
                "caption": caption[:100],
            }

        except Exception as e:
            logger.error(f"TikTok upload failed: {e}")
            raise RuntimeError(f"TikTok upload failed: {e}")

    def get_supported_features(self) -> list[str]:
        return ["upload", "tags"]

    def login(self) -> bool:
        """Open browser for TikTok login — saves cookies for later uploads"""
        from playwright.sync_api import sync_playwright

        cookies_file = str(_cookies_path())
        logger.info("Opening browser for TikTok login...")

        try:
            with sync_playwright() as p:
                browser, context = _launch_browser(p)
                page = context.new_page()
                page.goto("https://www.tiktok.com/login", timeout=60000, wait_until="domcontentloaded")
                logger.info("Please login to TikTok in the browser window...")

                logged_in = False
                for check_idx in range(150):  # 5 min timeout
                    _time.sleep(2)
                    try:
                        current_url = page.url
                    except Exception:
                        continue

                    # URL no longer on login page
                    if "/login" not in current_url and "tiktok.com" in current_url:
                        logged_in = True
                        logger.info(f"Login detected via URL: {current_url}")
                        break

                    # Check session cookies (multiple possible names)
                    current_cookies = context.cookies()
                    session_names = {"sessionid", "sid_tt", "uid_tt", "sid_guard", "passport_csrf_token"}
                    has_session = any(c.get("name") in session_names for c in current_cookies)
                    if has_session:
                        logged_in = True
                        logger.info("Login detected via session cookies!")
                        # Wait for page to settle after QR login
                        _time.sleep(5)
                        break

                    if check_idx % 15 == 0 and check_idx > 0:
                        logger.info(f"Waiting for login... ({check_idx*2}s)")

                if logged_in:
                    logger.info(f"Login detected! URL: {page.url}")
                    _time.sleep(3)
                else:
                    logger.warning("Login timeout — saving cookies anyway")

                cookies = context.cookies()
                if cookies:
                    with open(cookies_file, "w", encoding="utf-8") as f:
                        json.dump(cookies, f, indent=2, ensure_ascii=False)
                    logger.info(f"Cookies saved: {cookies_file} ({len(cookies)} cookies)")
                    browser.close()
                    return True

                browser.close()
                return False

        except Exception as e:
            logger.error(f"TikTok login failed: {e}")
            return False

    def is_logged_in(self) -> bool:
        cookies_file = _cookies_path()
        if not cookies_file.exists():
            return False
        if cookies_file.stat().st_size < 100:
            return False
        age_days = (_time.time() - cookies_file.stat().st_mtime) / 86400
        return age_days < 30
