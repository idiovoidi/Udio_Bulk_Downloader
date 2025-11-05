// DOM manipulation utilities
export class DOMUtils {
  static sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  static async waitForElement(selector, timeout = 5000) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      const element = document.querySelector(selector);
      if (element) return element;
      await this.sleep(100);
    }
    throw new Error(`Element ${selector} not found after ${timeout}ms`);
  }

  static getScrollContainer() {
    return document.querySelector('main') || 
           document.querySelector('[role="main"]') || 
           document.querySelector('.overflow-auto') ||
           document.documentElement;
  }

  static async scrollToBottom(container, maxAttempts = 50) {
    let previousHeight = 0;
    let noChangeCount = 0;
    let attempts = 0;

    while (attempts < maxAttempts) {
      const currentHeight = container.scrollHeight;
      
      if (currentHeight === previousHeight) {
        noChangeCount++;
        if (noChangeCount >= 3) break;
      } else {
        noChangeCount = 0;
      }

      previousHeight = currentHeight;
      container.scrollBy(0, 1000);
      await this.sleep(800);
      attempts++;
    }

    container.scrollTo(0, 0);
    return attempts < maxAttempts;
  }

  static extractAttribute(element, attr) {
    return element?.getAttribute(attr) || null;
  }

  static extractText(element, selector) {
    const el = selector ? element.querySelector(selector) : element;
    return el?.textContent?.trim() || null;
  }
}
