// Diagnostic utilities for debugging
import { DOMUtils } from '../modules/dom-utils.js';

export class Diagnostics {
  constructor(logger) {
    this.logger = logger;
  }

  async dumpTreeStructure() {
    console.log('\n========== TREE STRUCTURE DIAGNOSTIC ==========\n');
    
    const treeContainer = document.querySelector('[role="tree"][aria-label="Folder structure"]');
    
    if (!treeContainer) {
      console.error('❌ Folder tree panel not found!');
      return;
    }
    
    console.log('✓ Found folder tree panel');
    console.log(`Total direct children: ${treeContainer.children.length}\n`);
    
    const expandableFolder = this._findExpandableFolder(treeContainer);
    if (!expandableFolder) {
      console.log('No expandable folders found');
      return;
    }
    
    await this._testFolderExpansion(expandableFolder, treeContainer);
    this._dumpAllItems(treeContainer);
    this._dumpItemHTML(treeContainer);
    
    console.log('\n========== END DIAGNOSTIC ==========\n');
  }

  _findExpandableFolder(treeContainer) {
    return Array.from(treeContainer.children).find(item => {
      return item.querySelector('button[aria-label="Expand"]') !== null;
    });
  }

  async _testFolderExpansion(folder, treeContainer) {
    const folderName = folder.querySelector('button[title]')?.getAttribute('title');
    console.log(`Found expandable folder: "${folderName}"`);
    console.log(`Current aria-expanded: ${folder.getAttribute('aria-expanded')}`);
    
    const itemsBefore = treeContainer.children.length;
    console.log(`Items before expansion: ${itemsBefore}`);
    
    const expandButton = folder.querySelector('button[aria-label="Expand"]');
    console.log('\nClicking expand button...');
    expandButton.click();
    
    await DOMUtils.sleep(1500);
    
    const itemsAfter = treeContainer.children.length;
    console.log(`Items after expansion: ${itemsAfter}`);
    console.log(`Items added: ${itemsAfter - itemsBefore}`);
    console.log(`New aria-expanded: ${folder.getAttribute('aria-expanded')}`);
    
    this._checkNestedChildren(folder);
  }

  _checkNestedChildren(folder) {
    console.log('\n--- Checking for nested children ---');
    const nestedChildren = folder.querySelectorAll('[role="button"]');
    console.log(`Found ${nestedChildren.length} nested button elements (including parent)`);
    
    if (nestedChildren.length > 1) {
      console.log('✓ Children are NESTED inside the parent item!');
      console.log('First few nested children:');
      Array.from(nestedChildren).slice(1, 4).forEach((child, i) => {
        const name = child.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
        console.log(`  ${i + 1}. ${name}`);
      });
    }
  }

  _dumpAllItems(treeContainer) {
    console.log('\n--- All items in tree (with padding) ---');
    const allItems = Array.from(treeContainer.children);
    
    allItems.forEach((item, index) => {
      const name = item.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
      const group = item.querySelector('.group');
      const padding = group ? parseInt(window.getComputedStyle(group).paddingLeft) : 0;
      const hasExpand = item.querySelector('button[aria-label="Expand"]') !== null;
      const isExpanded = item.getAttribute('aria-expanded') === 'true';
      
      console.log(`${index}: "${name}" | padding=${padding}px | expand=${hasExpand} | expanded=${isExpanded}`);
    });
  }

  _dumpItemHTML(treeContainer) {
    console.log('\n--- First 3 items HTML ---');
    const allItems = Array.from(treeContainer.children);
    
    allItems.slice(0, 3).forEach((item, index) => {
      const name = item.querySelector('button[title]')?.getAttribute('title') || 'unnamed';
      console.log(`\nItem ${index} (${name}):`);
      console.log(item.outerHTML.substring(0, 400) + '...');
    });
  }
}
