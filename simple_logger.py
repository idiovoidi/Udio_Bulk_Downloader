"""
Simple Action Logger - Windows Compatible

Handles Ctrl+C properly on Windows and always saves logs.
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Global to store actions
collected_actions = []
session_start = datetime.now()


async def run_logger():
    """Run the action logger."""
    global collected_actions
    
    print("=" * 60)
    print("SIMPLE ACTION LOGGER")
    print("=" * 60)
    print()
    
    user_data_dir = str(Path.home() / '.udio_downloader' / 'browser_profile')
    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    
    playwright = await async_playwright().start()
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    page = await context.new_page()
    
    # Inject tracking script
    await page.add_init_script("""
        window.actionLog = [];
        
        document.addEventListener('click', (e) => {
            window.actionLog.push({
                type: 'click',
                timestamp: Date.now(),
                element: {
                    tagName: e.target.tagName,
                    className: e.target.className,
                    textContent: e.target.textContent?.substring(0, 100),
                    outerHTML: e.target.outerHTML?.substring(0, 500)
                },
                position: { x: e.clientX, y: e.clientY },
                url: window.location.href
            });
        }, true);
        
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                window.actionLog.push({
                    type: 'scroll',
                    timestamp: Date.now(),
                    position: { x: window.scrollX, y: window.scrollY },
                    url: window.location.href
                });
            }, 200);
        });
    """)
    
    # Navigate
    print("Navigating to Udio...")
    try:
        await page.goto('https://www.udio.com/library', timeout=30000)
    except:
        pass
    
    await asyncio.sleep(2)
    
    if 'login' in page.url.lower():
        print("Please log in...")
        input("Press Enter when on library page...")
    
    print()
    print("🎬 Recording started!")
    print()
    print("Do your thing in Udio, then press Ctrl+C here")
    print()
    
    try:
        while True:
            await asyncio.sleep(2)
            
            # Collect actions
            actions = await page.evaluate('() => { const log = window.actionLog || []; window.actionLog = []; return log; }')
            if actions:
                collected_actions.extend(actions)
                print(f"Actions: {len(collected_actions)}", end='\r')
    
    except asyncio.CancelledError:
        pass
    
    # Collect final actions
    try:
        actions = await page.evaluate('() => window.actionLog || []')
        if actions:
            collected_actions.extend(actions)
    except:
        pass
    
    await context.close()
    await playwright.stop()


def save_and_print_log():
    """Save log and print to terminal."""
    global collected_actions, session_start
    
    print()
    print()
    print("=" * 60)
    print("SAVING LOG")
    print("=" * 60)
    print()
    
    log_data = {
        'session': {
            'start': session_start.isoformat(),
            'end': datetime.now().isoformat(),
            'total_actions': len(collected_actions)
        },
        'actions': collected_actions
    }
    
    # Save to file
    try:
        with open('action_log.json', 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
        print("✅ Saved to: action_log.json")
    except Exception as e:
        print(f"❌ Could not save file: {e}")
    
    # Print to terminal
    print()
    print("=" * 60)
    print("FULL LOG (copy this)")
    print("=" * 60)
    print()
    print(json.dumps(log_data, indent=2))
    print()
    print("=" * 60)
    print()
    print(f"Total actions captured: {len(collected_actions)}")
    
    # Count types
    clicks = sum(1 for a in collected_actions if a.get('type') == 'click')
    scrolls = sum(1 for a in collected_actions if a.get('type') == 'scroll')
    print(f"  Clicks: {clicks}")
    print(f"  Scrolls: {scrolls}")
    print()


def signal_handler(sig, frame):
    """Handle Ctrl+C."""
    print()
    print()
    print("⏹️  Stopping...")
    save_and_print_log()
    sys.exit(0)


async def main():
    """Main entry point."""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await run_logger()
    except KeyboardInterrupt:
        pass
    finally:
        save_and_print_log()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        save_and_print_log()
