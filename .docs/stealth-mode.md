# Stealth Mode

## Implementation

Both scrapers (`scrape_udio_library.py` and `scrape_udio_simple.py`) hide automation indicators:

### Chrome Arguments
```python
args=[
    '--disable-blink-features=AutomationControlled',
    '--disable-infobars',
    '--disable-automation',
    '--disable-browser-side-navigation',
    '--disable-gpu'
],
ignore_default_args=['--enable-automation']
```

### JavaScript Injection
```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
```

## Verification

Test stealth mode is working:
```bash
python scrape_udio_simple.py
```

In browser console (F12): `navigator.webdriver` should return `undefined` (not `true`)

## Detection Signs

Stop immediately if you see:
- Login loops
- CAPTCHA
- "Suspicious activity" messages
- Account locked
- Rate limit errors

## Risk Mitigation

Current protection:
- Persistent browser profile with real session
- Rate limiting (1-3 req/sec)
- Hidden automation flags
- Real user agent

If issues persist:
1. Use your actual Chrome profile path instead of automation profile
2. Add random delays: `await asyncio.sleep(random.uniform(1, 3))`
3. Consider `pip install playwright-stealth`
