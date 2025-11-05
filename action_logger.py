"""
Udio Action Logger

Records user interactions with the Udio interface to help identify
correct selectors and interaction patterns for automation.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ActionLogger:
    """Logs user actions for analysis."""
    
    def __init__(self, user_data_dir: str = None):
        self.user_data_dir = user_data_dir or str(Path.home() / '.udio_downloader' / 'browser_profile')
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.actions: List[Dict] = []
        self.session_start = datetime.now()
        
    async def initialize(self):
        """Initialize Playwright and browser."""
        logger.info("Initializing Action Logger...")
        
        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--disable-automation'
            ],
            viewport={'width': 1920, 'height': 1080},
            ignore_default_args=['--enable-automation']
        )
        
        self.page = await self.context.new_page()
        
        # Hide webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Inject action tracking script
        await self.page.add_init_script("""
            window.actionLog = [];
            
            // Track clicks
            document.addEventListener('click', (e) => {
                const target = e.target;
                const action = {
                    type: 'click',
                    timestamp: Date.now(),
                    element: {
                        tagName: target.tagName,
                        id: target.id,
                        className: target.className,
                        textContent: target.textContent?.substring(0, 100),
                        href: target.href,
                        outerHTML: target.outerHTML?.substring(0, 500)
                    },
                    position: {
                        x: e.clientX,
                        y: e.clientY
                    },
                    url: window.location.href
                };
                
                window.actionLog.push(action);
                console.log('CLICK:', action);
            }, true);
            
            // Track scrolls
            let scrollTimeout;
            window.addEventListener('scroll', (e) => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    const action = {
                        type: 'scroll',
                        timestamp: Date.now(),
                        position: {
                            x: window.scrollX,
                            y: window.scrollY
                        },
                        url: window.location.href
                    };
                    
                    window.actionLog.push(action);
                    console.log('SCROLL:', action);
                }, 200);
            });
            
            // Track keyboard input
            document.addEventListener('keydown', (e) => {
                const action = {
                    type: 'keydown',
                    timestamp: Date.now(),
                    key: e.key,
                    code: e.code,
                    target: {
                        tagName: e.target.tagName,
                        id: e.target.id,
                        className: e.target.className
                    },
                    url: window.location.href
                };
                
                window.actionLog.push(action);
                console.log('KEYDOWN:', action);
            });
            
            // Track navigation
            let lastUrl = window.location.href;
            setInterval(() => {
                if (window.location.href !== lastUrl) {
                    const action = {
                        type: 'navigation',
                        timestamp: Date.now(),
                        from: lastUrl,
                        to: window.location.href
                    };
                    
                    window.actionLog.push(action);
                    console.log('NAVIGATION:', action);
                    lastUrl = window.location.href;
                }
            }, 500);
        """)
        
        logger.info("Action Logger initialized")
        
    async def navigate_to_library(self):
        """Navigate to Udio library."""
        logger.info("Navigating to Udio library...")
        
        try:
            await self.page.goto('https://www.udio.com/library', timeout=30000)
        except:
            pass
        
        await asyncio.sleep(3)
        
        if 'login' in self.page.url.lower() or 'google.com' in self.page.url.lower():
            print()
            print("=" * 60)
            print("LOGIN REQUIRED")
            print("=" * 60)
            print("Please log in to Udio.")
            input("Press Enter when you're on the library page...")
            
            try:
                await self.page.wait_for_url('**/library**', timeout=60000)
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.info(f"Current URL: {self.page.url}")
    
    async def collect_actions(self):
        """Collect actions from the page."""
        actions = await self.page.evaluate('''() => {
            const log = window.actionLog || [];
            window.actionLog = [];  // Clear after collecting
            return log;
        }''')
        
        if actions:
            self.actions.extend(actions)
            logger.info(f"Collected {len(actions)} actions")
        
        return actions
    
    async def get_page_state(self) -> Dict:
        """Get current page state for context."""
        
        state = await self.page.evaluate('''() => {
            return {
                url: window.location.href,
                title: document.title,
                scrollPosition: {
                    x: window.scrollX,
                    y: window.scrollY
                },
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                visibleElements: {
                    folders: document.querySelectorAll('svg.lucide-folder').length,
                    songs: document.querySelectorAll('a[href*="/songs/"]').length,
                    buttons: document.querySelectorAll('button').length,
                    links: document.querySelectorAll('a').length
                }
            };
        }''')
        
        return state
    
    async def analyze_element(self, selector: str) -> Dict:
        """Analyze a specific element."""
        
        try:
            element_info = await self.page.evaluate(f'''(selector) => {{
                const el = document.querySelector(selector);
                if (!el) return null;
                
                return {{
                    tagName: el.tagName,
                    id: el.id,
                    className: el.className,
                    textContent: el.textContent?.substring(0, 200),
                    attributes: Array.from(el.attributes).map(attr => ({{
                        name: attr.name,
                        value: attr.value
                    }})),
                    computedStyle: {{
                        display: window.getComputedStyle(el).display,
                        visibility: window.getComputedStyle(el).visibility,
                        position: window.getComputedStyle(el).position
                    }},
                    boundingBox: el.getBoundingClientRect(),
                    outerHTML: el.outerHTML?.substring(0, 1000)
                }};
            }}''', selector)
            
            return element_info
        except Exception as e:
            logger.error(f"Error analyzing element: {e}")
            return None
    
    async def monitor_session(self):
        """Monitor user session until interrupted."""
        
        print()
        print("=" * 60)
        print("ACTION LOGGING SESSION")
        print("=" * 60)
        print()
        print("🎬 Recording started!")
        print()
        print("Interact with Udio normally:")
        print("- Click folders")
        print("- Scroll through songs")
        print("- Click on songs")
        print("- Navigate around")
        print()
        print("⏹️  Press Ctrl+C when done to save logs")
        print()
        
        try:
            while True:
                # Collect actions every 2 seconds
                await asyncio.sleep(2)
                await self.collect_actions()
                
                # Show progress
                print(f"Actions logged: {len(self.actions)}", end='\r')
        except KeyboardInterrupt:
            print()
            print()
            logger.info("⏹️  Recording stopped by user")
            # Collect any remaining actions
            await self.collect_actions()
        
        print()
        logger.info(f"✅ Session complete. Total actions: {len(self.actions)}")
    
    def save_log(self, filename: str = "action_log.json"):
        """Save action log to file."""
        
        # Add session metadata
        log_data = {
            'session': {
                'start': self.session_start.isoformat(),
                'end': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.session_start).total_seconds(),
                'total_actions': len(self.actions)
            },
            'actions': self.actions
        }
        
        # Get absolute path
        filepath = Path(filename).absolute()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved action log to {filepath}")
        print(f"📄 Log file: {filepath}")
        
        return log_data
    
    def analyze_log(self) -> Dict:
        """Analyze the action log to identify patterns."""
        
        analysis = {
            'summary': {
                'total_actions': len(self.actions),
                'clicks': 0,
                'scrolls': 0,
                'keydowns': 0,
                'navigations': 0
            },
            'clicked_elements': {},
            'navigation_paths': [],
            'common_selectors': []
        }
        
        # Count action types
        for action in self.actions:
            action_type = action.get('type')
            if action_type == 'click':
                analysis['summary']['clicks'] += 1
                
                # Track clicked elements
                element = action.get('element', {})
                text = element.get('textContent', '')[:50]
                if text:
                    analysis['clicked_elements'][text] = analysis['clicked_elements'].get(text, 0) + 1
                    
            elif action_type == 'scroll':
                analysis['summary']['scrolls'] += 1
            elif action_type == 'keydown':
                analysis['summary']['keydowns'] += 1
            elif action_type == 'navigation':
                analysis['summary']['navigations'] += 1
                analysis['navigation_paths'].append({
                    'from': action.get('from'),
                    'to': action.get('to')
                })
        
        # Find most clicked elements
        analysis['most_clicked'] = sorted(
            analysis['clicked_elements'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return analysis
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    print("=" * 60)
    print("UDIO ACTION LOGGER")
    print("=" * 60)
    print()
    print("This tool logs all your interactions with Udio to help")
    print("identify the correct selectors and patterns for automation.")
    print()
    
    logger_tool = ActionLogger()
    
    try:
        await logger_tool.initialize()
        await logger_tool.navigate_to_library()
        
        # Get initial page state
        state = await logger_tool.get_page_state()
        print()
        print("Current page state:")
        print(f"  URL: {state['url']}")
        print(f"  Folders visible: {state['visibleElements']['folders']}")
        print(f"  Songs visible: {state['visibleElements']['songs']}")
        print()
        
        # Start monitoring
        print("Ready to start logging!")
        input("Press Enter to begin recording...")
        
        try:
            await logger_tool.monitor_session()
        except KeyboardInterrupt:
            pass
        
        # Collect any final actions
        await logger_tool.collect_actions()
        
        # Save log
        print()
        print("💾 Saving action log...")
        log_data = logger_tool.save_log()
        
        # Analyze
        analysis = logger_tool.analyze_log()
        
        print()
        print("=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        print()
        print(f"Total actions: {analysis['summary']['total_actions']}")
        print(f"  Clicks: {analysis['summary']['clicks']}")
        print(f"  Scrolls: {analysis['summary']['scrolls']}")
        print(f"  Keydowns: {analysis['summary']['keydowns']}")
        print(f"  Navigations: {analysis['summary']['navigations']}")
        print()
        
        if analysis['most_clicked']:
            print("Most clicked elements:")
            for text, count in analysis['most_clicked'][:5]:
                print(f"  {count}x: {text}")
        
        print()
        print("=" * 60)
        print("LOG FILE READY")
        print("=" * 60)
        print()
        print("📄 File: action_log.json")
        print()
        print("To view the log:")
        print("  cat action_log.json")
        print()
        print("Or open it in your editor to share with me!")
        print()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await logger_tool.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
