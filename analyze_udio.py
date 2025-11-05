"""
Analyze Udio's tech stack and page structure.

Usage:
1. Start Chrome with: chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/path/to/profile"
2. Navigate to Udio library page
3. Run: python analyze_udio.py
"""

import json
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from scraper.core import BrowserConnection
from scraper.utils import get_logger, PathManager, OutputFormatter


class UdioAnalyzer:
    """Analyze Udio's tech stack and structure"""
    
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.analysis = {
            'url': '',
            'title': '',
            'tech_stack': {},
            'dom_structure': {},
            'network': {},
            'javascript': {},
            'api_endpoints': [],
            'security': {},
            'performance': {}
        }
    
    def analyze_all(self):
        """Run all analysis methods"""
        self.logger.info("Starting comprehensive Udio analysis")
        
        self.analyze_basic_info()
        self.analyze_tech_stack()
        self.analyze_dom_structure()
        self.analyze_javascript()
        self.analyze_network()
        self.analyze_security()
        self.analyze_performance()
        
        self.logger.success("Analysis complete")
        return self.analysis
    
    def analyze_basic_info(self):
        """Get basic page information"""
        self.logger.info("Analyzing basic page info...")
        
        self.analysis['url'] = self.driver.current_url
        self.analysis['title'] = self.driver.title
        self.analysis['user_agent'] = self.driver.execute_script("return navigator.userAgent;")
        
        self.logger.success(f"Page: {self.analysis['title']}")
    
    def analyze_tech_stack(self):
        """Detect frameworks and libraries"""
        self.logger.info("Detecting tech stack...")
        
        tech_stack = {}
        
        # Check for React
        react_check = self.driver.execute_script("""
            return {
                hasReact: typeof React !== 'undefined',
                hasReactDOM: typeof ReactDOM !== 'undefined',
                hasReactRoot: !!document.querySelector('[data-reactroot], [data-reactid]'),
                reactVersion: typeof React !== 'undefined' ? React.version : null,
                hasReactDevTools: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__
            };
        """)
        tech_stack['react'] = react_check
        
        # Check for Next.js
        nextjs_check = self.driver.execute_script("""
            return {
                hasNext: typeof __NEXT_DATA__ !== 'undefined',
                hasNextRoot: !!document.getElementById('__next'),
                nextData: typeof __NEXT_DATA__ !== 'undefined' ? {
                    buildId: __NEXT_DATA__.buildId,
                    page: __NEXT_DATA__.page,
                    props: Object.keys(__NEXT_DATA__.props || {})
                } : null
            };
        """)
        tech_stack['nextjs'] = nextjs_check
        
        # Check for other frameworks
        frameworks = self.driver.execute_script("""
            return {
                vue: typeof Vue !== 'undefined',
                angular: typeof angular !== 'undefined' || typeof ng !== 'undefined',
                jquery: typeof jQuery !== 'undefined',
                lodash: typeof _ !== 'undefined',
                axios: typeof axios !== 'undefined',
                redux: typeof Redux !== 'undefined'
            };
        """)
        tech_stack['frameworks'] = frameworks
        
        # Check for UI libraries
        ui_libs = self.driver.execute_script("""
            return {
                tailwind: !!document.querySelector('[class*="tw-"], [class*="flex"], [class*="grid"]'),
                bootstrap: !!document.querySelector('[class*="btn-"], [class*="col-"]'),
                materialUI: !!document.querySelector('[class*="MuiButton"], [class*="Mui"]'),
                chakraUI: !!document.querySelector('[class*="chakra"]'),
                shadcn: !!document.querySelector('[class*="radix"]')
            };
        """)
        tech_stack['ui_libraries'] = ui_libs
        
        # Check for state management
        state_mgmt = self.driver.execute_script("""
            return {
                redux: typeof Redux !== 'undefined' || !!window.__REDUX_DEVTOOLS_EXTENSION__,
                mobx: typeof mobx !== 'undefined',
                zustand: typeof zustand !== 'undefined',
                recoil: typeof Recoil !== 'undefined'
            };
        """)
        tech_stack['state_management'] = state_mgmt
        
        self.analysis['tech_stack'] = tech_stack
        self.logger.success(f"Detected: React={react_check['hasReact']}, Next.js={nextjs_check['hasNext']}")
    
    def analyze_dom_structure(self):
        """Analyze DOM structure and key elements"""
        self.logger.info("Analyzing DOM structure...")
        
        dom = {}
        
        # Get meta tags
        meta_tags = self.driver.execute_script("""
            const metas = Array.from(document.querySelectorAll('meta'));
            return metas.map(m => ({
                name: m.name || m.getAttribute('property'),
                content: m.content
            })).filter(m => m.name);
        """)
        dom['meta_tags'] = meta_tags
        
        # Get main containers
        containers = self.driver.execute_script("""
            return {
                body_classes: document.body.className,
                main_id: document.querySelector('main')?.id || null,
                root_elements: Array.from(document.body.children).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    classes: el.className
                }))
            };
        """)
        dom['containers'] = containers
        
        # Find key UI elements
        key_elements = self.driver.execute_script("""
            return {
                navigation: !!document.querySelector('nav, [role="navigation"]'),
                sidebar: !!document.querySelector('aside, [role="complementary"]'),
                main_content: !!document.querySelector('main, [role="main"]'),
                folder_tree: !!document.querySelector('[role="tree"]'),
                song_list: !!document.querySelector('[role="list"], table'),
                player: !!document.querySelector('audio, video, [class*="player"]')
            };
        """)
        dom['key_elements'] = key_elements
        
        # Get folder tree structure
        folder_tree = self.driver.execute_script("""
            const tree = document.querySelector('[role="tree"]');
            if (!tree) return null;
            
            return {
                exists: true,
                aria_label: tree.getAttribute('aria-label'),
                classes: tree.className,
                item_count: tree.querySelectorAll('[role="button"]').length,
                sample_item: (() => {
                    const item = tree.querySelector('[role="button"]');
                    if (!item) return null;
                    return {
                        classes: item.className,
                        attributes: Array.from(item.attributes).map(a => ({
                            name: a.name,
                            value: a.value
                        }))
                    };
                })()
            };
        """)
        dom['folder_tree'] = folder_tree
        
        # Get song list structure
        song_list = self.driver.execute_script("""
            const table = document.querySelector('table');
            if (!table) return null;
            
            const rows = table.querySelectorAll('tr');
            const sampleRow = rows[1]; // Skip header
            
            return {
                exists: true,
                row_count: rows.length,
                classes: table.className,
                sample_row: sampleRow ? {
                    classes: sampleRow.className,
                    cell_count: sampleRow.querySelectorAll('td').length,
                    has_link: !!sampleRow.querySelector('a[href*="/songs/"]'),
                    has_image: !!sampleRow.querySelector('img'),
                    structure: Array.from(sampleRow.children).map(cell => ({
                        tag: cell.tagName,
                        classes: cell.className,
                        content_type: cell.querySelector('img') ? 'image' :
                                     cell.querySelector('a') ? 'link' :
                                     cell.querySelector('button') ? 'button' : 'text'
                    }))
                } : null
            };
        """)
        dom['song_list'] = song_list
        
        self.analysis['dom_structure'] = dom
        self.logger.success(f"Found folder tree: {folder_tree is not None}")
    
    def analyze_javascript(self):
        """Analyze JavaScript environment"""
        self.logger.info("Analyzing JavaScript environment...")
        
        js_info = {}
        
        # Get global objects
        globals = self.driver.execute_script("""
            const interesting = [
                'React', 'ReactDOM', '__NEXT_DATA__', 'Redux',
                'fetch', 'axios', 'WebSocket', 'EventSource'
            ];
            
            const found = {};
            interesting.forEach(name => {
                found[name] = typeof window[name] !== 'undefined';
            });
            
            return found;
        """)
        js_info['globals'] = globals
        
        # Check for service workers
        service_worker = self.driver.execute_script("""
            return {
                supported: 'serviceWorker' in navigator,
                registered: navigator.serviceWorker?.controller !== null,
                controller: navigator.serviceWorker?.controller?.scriptURL || null
            };
        """)
        js_info['service_worker'] = service_worker
        
        # Check for web workers
        web_worker = self.driver.execute_script("""
            return {
                supported: typeof Worker !== 'undefined'
            };
        """)
        js_info['web_worker'] = web_worker
        
        # Check for WebSocket
        websocket = self.driver.execute_script("""
            return {
                supported: typeof WebSocket !== 'undefined',
                active_connections: 0  // Can't easily detect without hooking
            };
        """)
        js_info['websocket'] = websocket
        
        # Get loaded scripts
        scripts = self.driver.execute_script("""
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            return scripts.map(s => ({
                src: s.src,
                async: s.async,
                defer: s.defer,
                type: s.type || 'text/javascript'
            })).slice(0, 20);  // First 20 scripts
        """)
        js_info['scripts'] = scripts
        
        self.analysis['javascript'] = js_info
        self.logger.success(f"Service Worker: {service_worker['registered']}")
    
    def analyze_network(self):
        """Analyze network requests and API endpoints"""
        self.logger.info("Analyzing network patterns...")
        
        # Get performance entries (recent network requests)
        network = self.driver.execute_script("""
            const entries = performance.getEntriesByType('resource');
            
            const byType = {};
            entries.forEach(entry => {
                const type = entry.initiatorType;
                if (!byType[type]) byType[type] = [];
                byType[type].push({
                    name: entry.name,
                    duration: entry.duration,
                    size: entry.transferSize
                });
            });
            
            // Get API-like requests
            const apiRequests = entries
                .filter(e => e.name.includes('/api/') || e.name.includes('graphql'))
                .map(e => ({
                    url: e.name,
                    duration: e.duration,
                    size: e.transferSize
                }));
            
            return {
                total_requests: entries.length,
                by_type: Object.keys(byType).reduce((acc, key) => {
                    acc[key] = byType[key].length;
                    return acc;
                }, {}),
                api_requests: apiRequests.slice(0, 10)
            };
        """)
        
        self.analysis['network'] = network
        
        # Try to detect API endpoints from links
        api_endpoints = self.driver.execute_script("""
            const links = Array.from(document.querySelectorAll('a[href]'));
            const endpoints = new Set();
            
            links.forEach(link => {
                const href = link.href;
                if (href.includes('/api/') || href.includes('/songs/')) {
                    try {
                        const url = new URL(href);
                        endpoints.add(url.pathname);
                    } catch (e) {}
                }
            });
            
            return Array.from(endpoints).slice(0, 20);
        """)
        self.analysis['api_endpoints'] = api_endpoints
        
        self.logger.success(f"Total requests: {network['total_requests']}")
    
    def analyze_security(self):
        """Analyze security features"""
        self.logger.info("Analyzing security features...")
        
        security = {}
        
        # Check CSP
        csp = self.driver.execute_script("""
            const meta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
            return meta ? meta.content : null;
        """)
        security['csp'] = csp
        
        # Check cookies
        cookies = self.driver.get_cookies()
        security['cookies'] = {
            'count': len(cookies),
            'names': [c['name'] for c in cookies],
            'has_secure': any(c.get('secure') for c in cookies),
            'has_httponly': any(c.get('httpOnly') for c in cookies)
        }
        
        # Check localStorage
        local_storage = self.driver.execute_script("""
            const keys = Object.keys(localStorage);
            return {
                count: keys.length,
                keys: keys.slice(0, 10),
                sample_sizes: keys.slice(0, 5).map(k => ({
                    key: k,
                    size: localStorage.getItem(k)?.length || 0
                }))
            };
        """)
        security['local_storage'] = local_storage
        
        # Check sessionStorage
        session_storage = self.driver.execute_script("""
            const keys = Object.keys(sessionStorage);
            return {
                count: keys.length,
                keys: keys.slice(0, 10)
            };
        """)
        security['session_storage'] = session_storage
        
        self.analysis['security'] = security
        self.logger.success(f"Cookies: {security['cookies']['count']}, LocalStorage keys: {local_storage['count']}")
    
    def analyze_performance(self):
        """Analyze performance metrics"""
        self.logger.info("Analyzing performance...")
        
        perf = self.driver.execute_script("""
            const timing = performance.timing;
            const navigation = performance.navigation;
            
            return {
                load_time: timing.loadEventEnd - timing.navigationStart,
                dom_ready: timing.domContentLoadedEventEnd - timing.navigationStart,
                first_paint: performance.getEntriesByType('paint')
                    .find(e => e.name === 'first-paint')?.startTime || null,
                first_contentful_paint: performance.getEntriesByType('paint')
                    .find(e => e.name === 'first-contentful-paint')?.startTime || null,
                navigation_type: navigation.type,
                redirect_count: navigation.redirectCount
            };
        """)
        
        self.analysis['performance'] = perf
        self.logger.success(f"Load time: {perf['load_time']}ms")
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("UDIO TECH STACK ANALYSIS")
        print("="*60)
        
        print(f"\n📄 Page: {self.analysis['title']}")
        print(f"🔗 URL: {self.analysis['url']}")
        
        print("\n🛠️  TECH STACK:")
        ts = self.analysis['tech_stack']
        print(f"  React: {ts['react']['hasReact']} (v{ts['react']['reactVersion']})")
        print(f"  Next.js: {ts['nextjs']['hasNext']}")
        if ts['nextjs']['hasNext'] and ts['nextjs']['nextData']:
            print(f"    Build ID: {ts['nextjs']['nextData']['buildId']}")
            print(f"    Page: {ts['nextjs']['nextData']['page']}")
        
        print("\n  UI Libraries:")
        for lib, detected in ts['ui_libraries'].items():
            if detected:
                print(f"    ✓ {lib}")
        
        print("\n  Other Frameworks:")
        for fw, detected in ts['frameworks'].items():
            if detected:
                print(f"    ✓ {fw}")
        
        print("\n🏗️  DOM STRUCTURE:")
        dom = self.analysis['dom_structure']
        print(f"  Key Elements:")
        for elem, exists in dom['key_elements'].items():
            print(f"    {elem}: {'✓' if exists else '✗'}")
        
        if dom['folder_tree']:
            print(f"\n  Folder Tree:")
            print(f"    Items: {dom['folder_tree']['item_count']}")
            print(f"    Label: {dom['folder_tree']['aria_label']}")
        
        if dom['song_list']:
            print(f"\n  Song List:")
            print(f"    Rows: {dom['song_list']['row_count']}")
            print(f"    Has images: {dom['song_list']['sample_row']['has_image']}")
            print(f"    Has links: {dom['song_list']['sample_row']['has_link']}")
        
        print("\n🌐 NETWORK:")
        net = self.analysis['network']
        print(f"  Total requests: {net['total_requests']}")
        print(f"  By type:")
        for req_type, count in net['by_type'].items():
            print(f"    {req_type}: {count}")
        
        if self.analysis['api_endpoints']:
            print(f"\n  API Endpoints found:")
            for endpoint in self.analysis['api_endpoints'][:5]:
                print(f"    {endpoint}")
        
        print("\n🔒 SECURITY:")
        sec = self.analysis['security']
        print(f"  Cookies: {sec['cookies']['count']}")
        print(f"  LocalStorage keys: {sec['local_storage']['count']}")
        print(f"  SessionStorage keys: {sec['session_storage']['count']}")
        
        print("\n⚡ PERFORMANCE:")
        perf = self.analysis['performance']
        print(f"  Load time: {perf['load_time']}ms")
        print(f"  DOM ready: {perf['dom_ready']}ms")
        if perf['first_contentful_paint']:
            print(f"  First contentful paint: {perf['first_contentful_paint']}ms")
        
        print("\n" + "="*60)


def main():
    """Run Udio analysis"""
    # Setup
    paths = PathManager(base_dir='output', platform='udio')
    logger = get_logger('udio_analyzer', log_dir=str(paths.get_log_dir()))
    
    browser = BrowserConnection(debug_port=9222)
    
    try:
        # Connect
        logger.info("Connecting to Chrome...")
        driver = browser.connect()
        
        # Analyze
        analyzer = UdioAnalyzer(driver, logger)
        analysis = analyzer.analyze_all()
        
        # Print summary
        analyzer.print_summary()
        
        # Save detailed analysis
        export_path = paths.get_export_path('tech_analysis.json', timestamped=True)
        OutputFormatter.save_json(analysis, export_path)
        
        logger.success("Analysis complete!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()


if __name__ == '__main__':
    main()
