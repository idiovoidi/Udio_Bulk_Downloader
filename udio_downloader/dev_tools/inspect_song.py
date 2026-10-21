"""
Inspect a single song to find download URL pattern.

Usage:
Run: python -m udio_downloader.dev_tools.inspect_song
"""

import asyncio
import json
from udio_downloader.dev_tools.scraper.core import BrowserConnection
from udio_downloader.dev_tools.scraper.utils import get_logger, PathManager


async def main():
    """Inspect a song to find download URL"""
    # Setup
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_inspector', log_dir=str(paths.get_log_dir()))
    
    browser = BrowserConnection()
    
    try:
        # Launch Chrome
        logger.info("Starting song inspector")
        context = await browser.connect()
        
        # Get or create page
        pages = context.pages
        if pages:
            page = pages[0]
        else:
            page = await context.new_page()
        
        # Navigate to library
        logger.info("Navigating to Udio library...")
        try:
            await page.goto('https://www.udio.com/library', timeout=30000)
        except:
            pass
        
        await asyncio.sleep(2)
        
        print("\n" + "="*60)
        print("SONG DOWNLOAD URL INSPECTOR")
        print("="*60)
        print("\n📝 Instructions:")
        print("1. Navigate to a song page in the browser")
        print("2. Press Enter here when ready")
        print()
        input("Press Enter when on a song page...")
        
        # Get current URL
        current_url = page.url
        print(f"\n✓ Current URL: {current_url}")
        
        # Extract song ID from URL
        song_id = None
        if '/songs/' in current_url:
            song_id = current_url.split('/songs/')[-1].split('?')[0].split('/')[0]
            print(f"✓ Song ID: {song_id}")
        
        # Wait for page to fully load
        print("\n⏳ Waiting for page to fully load...")
        await asyncio.sleep(3)
        
        # Look for download button with multiple strategies
        print("\n🔍 Looking for download button...")
        
        # First, let's see what buttons are on the page and their titles
        button_info = await page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.map(btn => ({
                    title: btn.getAttribute('title'),
                    ariaLabel: btn.getAttribute('aria-label'),
                    text: btn.textContent?.trim().substring(0, 50),
                    hasSvg: !!btn.querySelector('svg')
                })).filter(b => b.title || b.ariaLabel || b.hasSvg);
            }
        """)
        
        print(f"  Found {len(button_info)} buttons with titles/labels:")
        for info in button_info[:10]:
            print(f"    - Title: {info['title']}, Label: {info['ariaLabel']}, Text: {info['text']}, HasSVG: {info['hasSvg']}")
        
        # Try multiple selectors
        download_button = await page.query_selector('button[title="Download media"]')
        
        if not download_button:
            print("  Trying alternative selectors...")
            # Use JavaScript to find the button
            download_button = await page.evaluate_handle("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    return buttons.find(btn => {
                        const title = btn.getAttribute('title');
                        if (title && title.toLowerCase().includes('download')) return true;
                        
                        const svg = btn.querySelector('svg');
                        if (!svg) return false;
                        
                        const paths = svg.querySelectorAll('path');
                        return Array.from(paths).some(path => 
                            path.getAttribute('d')?.includes('m12 16')
                        );
                    });
                }
            """)
            
            # Check if we got a valid element
            if download_button:
                try:
                    await download_button.evaluate('el => el.tagName')
                except:
                    download_button = None
        
        if download_button:
            print("✓ Found download button!")
            
            # Set up network request listener BEFORE clicking
            print("\n🔍 Setting up network listener...")
            download_requests = []
            
            async def handle_request(request):
                url = request.url
                if any(ext in url for ext in ['.mp3', '.wav', '.m4a', 'download', 'audio', 'media']):
                    download_requests.append({
                        'url': url,
                        'method': request.method,
                        'headers': dict(request.headers)
                    })
                    print(f"  📥 Captured: {url[:100]}...")
            
            page.on('request', handle_request)
            
            # Click the download button to open popup
            print("\n🖱️  Clicking download button to open popup...")
            await download_button.click()
            await asyncio.sleep(1)
            
            # Look for MP3 option in the popup
            print("🔍 Looking for MP3 option...")
            mp3_option = await page.query_selector('text=MP3')
            
            if mp3_option:
                print("✓ Found MP3 option, clicking...")
                await mp3_option.click()
                await asyncio.sleep(0.5)
            else:
                print("⚠️  MP3 option not found, trying alternative selector...")
                mp3_option = await page.query_selector('div:has-text("MP3")')
                if mp3_option:
                    await mp3_option.click()
                    await asyncio.sleep(0.5)
            
            # Look for the actual Download button in the popup
            print("🔍 Looking for Download button in popup...")
            popup_download_btn = await page.query_selector('button:has-text("Download")')
            
            if popup_download_btn:
                print("✓ Found Download button, clicking...")
                await popup_download_btn.click()
                
                # Wait for download to start
                print("⏳ Waiting for download to start...")
                await asyncio.sleep(5)
            else:
                print("❌ Download button not found in popup")
            
            # Remove listener
            page.remove_listener('request', handle_request)
            
            if download_requests:
                print(f"\n✓ Captured {len(download_requests)} download requests:")
                for req in download_requests:
                    print(f"\n  URL: {req['url']}")
                    print(f"  Method: {req['method']}")
                    print(f"  Headers: {list(req['headers'].keys())}")
            else:
                print("\n⚠️  No download requests captured")
                print("   The download might be handled differently (direct download)")
        else:
            print("❌ No download button found")
        
        # Look for audio element
        print("\n🔍 Looking for audio player...")
        audio_element = await page.query_selector('audio')
        
        if audio_element:
            print("✓ Found audio element!")
            src = await audio_element.get_attribute('src')
            if src:
                print(f"✓ Audio src: {src}")
            else:
                # Check for source elements
                sources = await audio_element.query_selector_all('source')
                if sources:
                    print(f"✓ Found {len(sources)} source elements:")
                    for i, source in enumerate(sources, 1):
                        src = await source.get_attribute('src')
                        src_type = await source.get_attribute('type')
                        print(f"  {i}. {src_type}: {src[:100]}...")
        else:
            print("❌ No audio element found")
        
        # Check for API calls in network
        print("\n🔍 Checking for API endpoints...")
        
        # Get all links on page
        links = await page.query_selector_all('a[href]')
        api_links = []
        for link in links:
            href = await link.get_attribute('href')
            if href and ('/api/' in href or '/download' in href or '.mp3' in href or '.wav' in href):
                api_links.append(href)
        
        if api_links:
            print(f"✓ Found {len(api_links)} potential API/download links:")
            for link in api_links[:10]:
                print(f"  - {link}")
        
        # Extract all tags from song page (deduplicated)
        print("\n🔍 Extracting tags from song page...")
        tags = await page.evaluate("""
            () => {
                const tagElements = document.querySelectorAll('.text-brand-gray-light, a[href*="/tags/"]');
                const tagSet = new Set();
                tagElements.forEach(el => {
                    const text = el.textContent.trim();
                    if (text && text !== 'More' && text !== 'Credits') {
                        tagSet.add(text);
                    }
                });
                return Array.from(tagSet);
            }
        """)
        
        if tags:
            print(f"✓ Found {len(tags)} unique tags: {', '.join(tags[:10])}")
            if len(tags) > 10:
                print(f"  ... and {len(tags) - 10} more")
        
        # Extract lyrics
        print("\n🔍 Extracting lyrics...")
        lyrics = await page.evaluate("""
            () => {
                const lyricsElement = document.querySelector('pre.whitespace-pre-wrap');
                return lyricsElement ? lyricsElement.textContent.trim() : null;
            }
        """)
        
        if lyrics:
            print(f"✓ Found lyrics ({len(lyrics)} characters)")
            print(f"  Preview: {lyrics[:100]}...")
        else:
            print("❌ No lyrics found")
        
        # Try to extract from page data
        print("\n🔍 Checking page data...")
        page_data = await page.evaluate("""
            () => {
                // Look for Next.js data
                const nextData = window.__NEXT_DATA__;
                
                // Look for any global data
                const keys = Object.keys(window).filter(k => 
                    k.includes('data') || k.includes('song') || k.includes('audio')
                );
                
                return {
                    hasNextData: !!nextData,
                    nextDataKeys: nextData ? Object.keys(nextData) : [],
                    globalKeys: keys.slice(0, 20)
                };
            }
        """)
        
        print(f"Has Next.js data: {page_data['hasNextData']}")
        if page_data['hasNextData']:
            print(f"Next.js data keys: {page_data['nextDataKeys']}")
        print(f"Global keys: {page_data['globalKeys']}")
        
        # Try to find download URL in page props
        print("\n🔍 Searching for download URL in page data...")
        download_url = await page.evaluate("""
            () => {
                const nextData = window.__NEXT_DATA__;
                if (!nextData) return null;
                
                // Search recursively for download-like URLs
                function findUrls(obj, depth = 0) {
                    if (depth > 10) return [];
                    if (!obj || typeof obj !== 'object') return [];
                    
                    const urls = [];
                    for (const [key, value] of Object.entries(obj)) {
                        if (typeof value === 'string') {
                            if (value.includes('.mp3') || value.includes('.wav') || 
                                value.includes('download') || value.includes('audio')) {
                                urls.push({ key, value });
                            }
                        } else if (typeof value === 'object') {
                            urls.push(...findUrls(value, depth + 1));
                        }
                    }
                    return urls;
                }
                
                return findUrls(nextData);
            }
        """)
        
        if download_url and len(download_url) > 0:
            print(f"✓ Found {len(download_url)} potential URLs:")
            for item in download_url[:10]:
                print(f"  {item['key']}: {item['value'][:100]}...")
        else:
            print("❌ No download URLs found in page data")
        
        # Save inspection results
        results = {
            'url': current_url,
            'song_id': song_id,
            'has_download_button': download_button is not None,
            'has_audio_element': audio_element is not None,
            'download_requests': download_requests if download_button else [],
            'tags': tags,
            'lyrics': lyrics,
            'api_links': api_links[:10],
            'page_data': page_data,
            'potential_urls': download_url[:10] if download_url else []
        }
        
        # Save lyrics to separate file if found
        if lyrics:
            lyrics_path = paths.get_export_path(f'lyrics_{song_id}.txt', timestamped=False)
            with open(lyrics_path, 'w', encoding='utf-8') as f:
                f.write(lyrics)
            print(f"\n✓ Saved lyrics to: {lyrics_path}")
        
        export_path = paths.get_export_path('song_inspection.json', timestamped=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Saved inspection results to: {export_path}")
        
        print("\n" + "="*60)
        print("INSPECTION COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Check the saved JSON for download URLs")
        print("2. Try clicking the download button manually")
        print("3. Check browser DevTools Network tab for download requests")
        
    except Exception as e:
        logger.error(f"Inspection failed: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nPress Enter to close browser...")
        input()
        await browser.close()
        logger.info("Browser closed")


if __name__ == '__main__':
    asyncio.run(main())
