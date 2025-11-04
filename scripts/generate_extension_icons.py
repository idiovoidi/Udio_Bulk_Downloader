#!/usr/bin/env python3
"""
Generate simple icons for the Chrome extension.
"""

from pathlib import Path

def create_simple_icon_svg(size):
    """Create a simple SVG icon."""
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{size}" height="{size}" fill="#1976d2" rx="{size//8}"/>
  
  <!-- Music note -->
  <g transform="translate({size//4}, {size//4})">
    <circle cx="{size//8}" cy="{size//2.5}" r="{size//8}" fill="white"/>
    <rect x="{size//8}" y="{size//8}" width="{size//16}" height="{size//2.5}" fill="white"/>
    <path d="M {size//8} {size//8} Q {size//3} {size//12} {size//3} {size//6}" 
          stroke="white" stroke-width="{size//16}" fill="none"/>
  </g>
  
  <!-- Folder indicator -->
  <rect x="{size//1.8}" y="{size//1.6}" width="{size//4}" height="{size//5}" 
        fill="white" opacity="0.8" rx="{size//32}"/>
</svg>'''
    return svg

def generate_icons():
    """Generate icon files."""
    icons_dir = Path('chrome_extension/icons')
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    sizes = [16, 48, 128]
    
    for size in sizes:
        svg_content = create_simple_icon_svg(size)
        svg_file = icons_dir / f'icon{size}.svg'
        
        with open(svg_file, 'w') as f:
            f.write(svg_content)
        
        print(f'✅ Created {svg_file}')
    
    # Create a simple PNG fallback using PIL if available
    try:
        from PIL import Image, ImageDraw
        
        for size in sizes:
            # Create image
            img = Image.new('RGB', (size, size), color='#1976d2')
            draw = ImageDraw.Draw(img)
            
            # Draw simple music note shape
            # Circle
            circle_x = size // 3
            circle_y = size * 2 // 3
            circle_r = size // 6
            draw.ellipse([circle_x - circle_r, circle_y - circle_r, 
                         circle_x + circle_r, circle_y + circle_r], 
                        fill='white')
            
            # Stem
            stem_x = circle_x + circle_r - 2
            stem_y1 = circle_y - circle_r
            stem_y2 = size // 4
            draw.rectangle([stem_x, stem_y2, stem_x + size//20, stem_y1], 
                          fill='white')
            
            # Save
            png_file = icons_dir / f'icon{size}.png'
            img.save(png_file)
            print(f'✅ Created {png_file}')
            
    except ImportError:
        print('⚠️  PIL not available, using SVG icons only')
        print('   SVG icons will work fine in Chrome')
        
        # Create placeholder PNG files
        for size in sizes:
            png_file = icons_dir / f'icon{size}.png'
            # Copy SVG as fallback
            svg_file = icons_dir / f'icon{size}.svg'
            if svg_file.exists():
                import shutil
                # Just create empty file as placeholder
                png_file.touch()
                print(f'⚠️  Created placeholder {png_file}')

if __name__ == '__main__':
    print('🎨 Generating Chrome Extension Icons...')
    generate_icons()
    print('\n✅ Icon generation complete!')
    print('📁 Icons saved to: chrome_extension/icons/')
    print('\n💡 Note: Chrome supports SVG icons, so the extension will work fine.')
    print('   If you want PNG icons, install Pillow: pip install Pillow')