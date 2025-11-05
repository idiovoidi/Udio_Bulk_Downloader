/**
 * Udio Page Inspector
 * 
 * Run this in the browser console (F12) on udio.com/library
 * to analyze the page structure and find song elements.
 */

console.log('='.repeat(60));
console.log('UDIO PAGE INSPECTOR');
console.log('='.repeat(60));
console.log();

// 1. Find all links
console.log('1. ANALYZING LINKS');
console.log('-'.repeat(60));
const allLinks = document.querySelectorAll('a');
console.log(`Total links: ${allLinks.length}`);

const songLinks = Array.from(allLinks).filter(a => a.href.includes('/songs/'));
console.log(`Links containing '/songs/': ${songLinks.length}`);

if (songLinks.length > 0) {
    console.log('\nSample song URLs:');
    songLinks.slice(0, 5).forEach(link => {
        console.log(`  ${link.href}`);
        console.log(`  Text: ${link.textContent.trim().substring(0, 50)}`);
        console.log(`  Classes: ${link.className}`);
        console.log();
    });
}
console.log();

// 2. Find elements with song-related classes
console.log('2. SONG-RELATED CLASSES');
console.log('-'.repeat(60));
const allElements = document.querySelectorAll('*');
const songClasses = new Set();

allElements.forEach(el => {
    if (el.className && typeof el.className === 'string') {
        el.className.split(' ').forEach(cls => {
            if (cls && (
                cls.toLowerCase().includes('song') ||
                cls.toLowerCase().includes('track') ||
                cls.toLowerCase().includes('audio')
            )) {
                songClasses.add(cls);
            }
        });
    }
});

console.log(`Found ${songClasses.size} song-related classes:`);
Array.from(songClasses).sort().forEach(cls => {
    const count = document.querySelectorAll(`.${cls}`).length;
    console.log(`  .${cls} (${count} elements)`);
});
console.log();

// 3. Find data-testid attributes
console.log('3. DATA-TESTID ATTRIBUTES');
console.log('-'.repeat(60));
const testIds = new Set();

allElements.forEach(el => {
    const testId = el.getAttribute('data-testid');
    if (testId) testIds.add(testId);
});

console.log(`Found ${testIds.size} unique data-testid values:`);
Array.from(testIds).sort().forEach(tid => {
    const count = document.querySelectorAll(`[data-testid="${tid}"]`).length;
    console.log(`  [data-testid="${tid}"] (${count} elements)`);
});
console.log();

// 4. Find your song titles
console.log('4. FINDING SONG TITLES');
console.log('-'.repeat(60));
console.log('Searching page text for potential song titles...');

// Get all text nodes
const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
);

const textNodes = [];
let node;
while (node = walker.nextNode()) {
    const text = node.textContent.trim();
    if (text.length > 5 && text.length < 100) {
        textNodes.push({
            text: text,
            parent: node.parentElement.tagName,
            classes: node.parentElement.className
        });
    }
}

console.log(`Found ${textNodes.length} potential text nodes`);
console.log('\nSample text (might include song titles):');
textNodes.slice(0, 10).forEach(n => {
    console.log(`  "${n.text.substring(0, 50)}"`);
    console.log(`    Parent: <${n.parent}> class="${n.classes}"`);
});
console.log();

// 5. Analyze page structure
console.log('5. PAGE STRUCTURE');
console.log('-'.repeat(60));

const structure = {
    totalElements: allElements.length,
    divs: document.querySelectorAll('div').length,
    spans: document.querySelectorAll('span').length,
    links: allLinks.length,
    buttons: document.querySelectorAll('button').length,
    images: document.querySelectorAll('img').length,
    iframes: document.querySelectorAll('iframe').length
};

console.log('Element counts:');
Object.entries(structure).forEach(([key, value]) => {
    console.log(`  ${key}: ${value}`);
});
console.log();

// 6. Check for Shadow DOM
console.log('6. SHADOW DOM CHECK');
console.log('-'.repeat(60));
const shadowHosts = Array.from(allElements).filter(el => el.shadowRoot);
console.log(`Elements with Shadow DOM: ${shadowHosts.length}`);
if (shadowHosts.length > 0) {
    console.log('Shadow DOM detected! Content might be hidden.');
    shadowHosts.forEach((host, i) => {
        console.log(`  Shadow host ${i + 1}: <${host.tagName}> class="${host.className}"`);
    });
}
console.log();

// 7. Find parent containers
console.log('7. POTENTIAL SONG CONTAINERS');
console.log('-'.repeat(60));

// Look for elements that might contain multiple songs
const containers = Array.from(allElements).filter(el => {
    const children = el.children.length;
    return children > 5 && children < 100;
});

console.log(`Found ${containers.length} potential container elements`);
containers.slice(0, 5).forEach((container, i) => {
    console.log(`  Container ${i + 1}:`);
    console.log(`    Tag: <${container.tagName}>`);
    console.log(`    Classes: ${container.className}`);
    console.log(`    Children: ${container.children.length}`);
    console.log(`    Test ID: ${container.getAttribute('data-testid') || 'none'}`);
});
console.log();

// 8. Generate selector suggestions
console.log('8. SELECTOR SUGGESTIONS');
console.log('-'.repeat(60));

const suggestions = [];

if (songLinks.length > 0) {
    const firstLink = songLinks[0];
    suggestions.push(`a[href*="/songs/"]`);
    
    if (firstLink.className) {
        const classes = firstLink.className.split(' ').filter(c => c);
        if (classes.length > 0) {
            suggestions.push(`a.${classes[0]}`);
        }
    }
    
    const parent = firstLink.closest('[class*="song"], [class*="track"], [class*="card"]');
    if (parent && parent.className) {
        const classes = parent.className.split(' ').filter(c => c);
        if (classes.length > 0) {
            suggestions.push(`.${classes[0]}`);
        }
    }
}

if (suggestions.length > 0) {
    console.log('Try these selectors in your scraper:');
    suggestions.forEach(sel => {
        const count = document.querySelectorAll(sel).length;
        console.log(`  "${sel}" - ${count} matches`);
    });
} else {
    console.log('No obvious selectors found.');
    console.log('Try inspecting a song element manually (right-click → Inspect)');
}
console.log();

// 9. Summary
console.log('='.repeat(60));
console.log('SUMMARY');
console.log('='.repeat(60));
console.log(`Total elements: ${allElements.length}`);
console.log(`Song links found: ${songLinks.length}`);
console.log(`Song-related classes: ${songClasses.size}`);
console.log(`Data-testid attributes: ${testIds.size}`);
console.log(`Shadow DOM elements: ${shadowHosts.length}`);
console.log();

if (songLinks.length > 0) {
    console.log('✅ Songs detected! Use the selector suggestions above.');
} else {
    console.log('❌ No songs found automatically.');
    console.log('Next steps:');
    console.log('1. Manually inspect a song element (right-click → Inspect)');
    console.log('2. Copy the selector (right-click element → Copy → Copy selector)');
    console.log('3. Test it: document.querySelectorAll("YOUR_SELECTOR")');
    console.log('4. Share the selector so we can update the scraper');
}
console.log();
console.log('='.repeat(60));
