"""
Simple Udio Library Scraper - Debug Version

This is a simplified version that shows you what's on the page
and helps identify the correct selectors.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def debug_udio_page():
    """Debug what's on the Udio library page."""
    
    print("=" * 60)
    print("UDIO PAGE DEBUGGER")
    print("=" * 60)
    print()
    
    user_data_dir = str(Path.home() / '.udio_downloader' / 'browser_profile')
    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--disable-automation'
            ],
            ignore_default_args=['--enable-automation']
        )
        
        page = await context.new_page()
        
        # Hide webdriver flag
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Navigate to library
        print("Navigating to Udio library...")
        try:
            await page.goto('https://www.udio.com/library', timeout=30000)
        except Exception as e:
            print(f"Navigation interrupted (likely OAuth redirect): {e}")
            print("This is normal if you're logging in through Google.")
        
        # Check if logged in
        await asyncio.sleep(2)
        if 'login' in page.url.lower() or 'google.com' in page.url.lower():
            print()
            print("⚠️  Not logged in!")
            print("Please log in to Udio in the browser window.")
            print("(The login process may redirect through Google)")
            input("Press Enter after you see the library page...")
            
            # Wait for navigation to complete
            try:
                await page.wait_for_url('**/library**', timeout=60000)
            except:
                # If timeout, just continue - user might already be on library page
                pass
            
            await asyncio.sleep(2)
        
        print(f"Current URL: {page.url}")
        print()
        
        # Check page title
        title = await page.title()
        print(f"Page title: {title}")
        print()
        
        # Wait for user to see the page
        print("Browser is open. Take a look at the page.")
        print()
        print("IMPORTANT:")
        print("1. Make sure you can see your songs in the browser")
        print("2. If the page is blank, try scrolling or refreshing")
        print("3. If you see a loading spinner, wait for it to finish")
        print()
        input("Press Enter when you can see your songs in the browser...")
        
        # Give page time to finish any loading
        print("Waiting for page to stabilize...")
        await asyncio.sleep(3)
        
        # Analyze page structure
        print()
        print("=" * 60)
        print("PAGE ANALYSIS")
        print("=" * 60)
        print()
        
        # Get page HTML
        html = await page.content()
        print(f"Page HTML length: {len(html)} characters")
        
        # Save HTML to file for analysis
        html_file = "udio_page_dump.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML saved to: {html_file}")
        print()
        
        # Try to find songs
        print("Looking for song elements...")
        
        selectors_to_try = [
            'a[href*="/songs/"]',
            '[data-testid*="song"]',
            '[class*="song"]',
            '[class*="Song"]',
            '.song-item',
            '[data-testid="song-item"]',
            'a',  # All links
            'button',  # All buttons
            '[role="button"]',  # Button roles
        ]
        
        for selector in selectors_to_try:
            try:
                count = await page.locator(selector).count()
                print(f"  {selector}: {count} elements")
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        print()
        
        # Get all unique class names
        print("Analyzing page structure...")
        structure = await page.evaluate('''() => {
            const classes = new Set();
            const testIds = new Set();
            const tags = {};
            
            document.querySelectorAll('*').forEach(el => {
                // Collect classes
                if (el.className && typeof el.className === 'string') {
                    el.className.split(' ').forEach(c => {
                        if (c) classes.add(c);
                    });
                }
                
                // Collect test IDs
                const testId = el.getAttribute('data-testid');
                if (testId) testIds.add(testId);
                
                // Count tags
                const tag = el.tagName.toLowerCase();
                tags[tag] = (tags[tag] || 0) + 1;
            });
            
            return {
                classes: Array.from(classes).sort(),
                testIds: Array.from(testIds).sort(),
                tags: tags,
                totalElements: document.querySelectorAll('*').length
            };
        }''')
        
        print(f"Total elements: {structure['totalElements']}")
        print(f"Unique classes: {len(structure['classes'])}")
        print(f"Unique test IDs: {len(structure['testIds'])}")
        print()
        
        # Show interesting classes
        print("Classes containing 'song', 'track', 'item', 'card':")
        interesting = [c for c in structure['classes'] if any(
            word in c.lower() for word in ['song', 'track', 'item', 'card', 'list', 'grid']
        )]
        for cls in interesting[:20]:
            print(f"  .{cls}")
        
        print()
        
        # Show test IDs
        if structure['testIds']:
            print("Data-testid attributes found:")
            for tid in structure['testIds'][:20]:
                print(f"  [data-testid='{tid}']")
            print()
        
        # Show common tags
        print("Most common tags:")
        sorted_tags = sorted(structure['tags'].items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:10]:
            print(f"  <{tag}>: {count}")
        
        print()
        
        # Extract all links
        print("Extracting all links on page...")
        links = await page.evaluate('''() => {
            const links = [];
            document.querySelectorAll('a').forEach(a => {
                if (a.href) links.push(a.href);
            });
            return links;
        }''')
        
        song_links = [link for link in links if '/songs/' in link]
        print(f"Found {len(song_links)} links containing '/songs/'")
        
        if song_links:
            print()
            print("Sample song URLs:")
            for link in song_links[:5]:
                print(f"  {link}")
        
        print()
        
        # Try to extract song data
        print("Attempting to extract song data...")
        songs = await page.evaluate('''() => {
            const songs = [];
            const links = document.querySelectorAll('a[href*="/songs/"]');
            
            links.forEach((link, i) => {
                const url = link.href;
                const songId = url.split('/songs/')[1]?.split('?')[0]?.split('/')[0];
                
                if (songId) {
                    // Try to find title
                    let title = link.textContent.trim();
                    
                    // Try parent element
                    if (!title || title.length < 3) {
                        const parent = link.closest('[class*="song"], [class*="Song"], [data-testid*="song"]');
                        if (parent) {
                            title = parent.textContent.trim().split('\\n')[0];
                        }
                    }
                    
                    songs.push({
                        id: songId,
                        title: title || `Song ${i + 1}`,
                        url: url
                    });
                }
            });
            
            // Remove duplicates
            const unique = {};
            songs.forEach(s => {
                if (!unique[s.id]) unique[s.id] = s;
            });
            
            return Object.values(unique);
        }''')
        
        print(f"Extracted {len(songs)} unique songs")
        
        if songs:
            print()
            print("Sample songs:")
            for song in songs[:5]:
                print(f"  ID: {song['id']}")
                print(f"  Title: {song['title']}")
                print(f"  URL: {song['url']}")
                print()
        
        print()
        print("=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print()
        
        if songs:
            print(f"✅ Successfully found {len(songs)} songs!")
            print()
            print("The main scraper should work. Run:")
            print("  python scrape_udio_library.py")
        else:
            print("❌ Could not find songs automatically.")
            print()
            print("Troubleshooting:")
            print("1. Make sure you're on the library page")
            print("2. Make sure songs are visible (scroll if needed)")
            print("3. Check browser console (F12) for errors")
            print("4. Try refreshing the page")
        
        print()
        input("Press Enter to close browser...")
        
        await context.close()


if __name__ == "__main__":
    asyncio.run(debug_udio_page())
