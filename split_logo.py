from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def split_logo():
    input_path = '../igreja-em-foco-app/public/logo.png'
    output_symbol = '../igreja-em-foco-app/public/logo-symbol.png'
    output_text = '../igreja-em-foco-app/public/logo-text.png'
    
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        
        # Split at 1800px (approx 60%)
        split_point = 1800
        
        symbol_img = img.crop((0, 0, width, split_point))
        text_img = img.crop((0, split_point, width, height))
        
        # Trim whitespace
        symbol_trimmed = trim(symbol_img)
        text_trimmed = trim(text_img)
        
        symbol_trimmed.save(output_symbol)
        text_trimmed.save(output_text)
        
        print(f"✅ Success! Generated:")
        print(f"   - {output_symbol} ({symbol_trimmed.size})")
        print(f"   - {output_text} ({text_trimmed.size})")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    split_logo()
