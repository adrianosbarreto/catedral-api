from PIL import Image, ImageOps

def generate_icons():
    source_path = '../igreja-em-foco-app/public/logo-symbol.png'
    public_dir = '../igreja-em-foco-app/public/'
    
    try:
        # Load the symbol (it's white with transparency)
        img = Image.open(source_path).convert("RGBA")
        
        # We want the icon to be black for better visibility on most browser tabs
        # or we can keep it as is if it's meant to be white.
        # Given the user's preference for black logo in UI, let's make a version that is visible.
        # But let's first auto-trim and then add padding to make it a square.
        
        def make_icon(size, color=None):
            icon_img = img.copy()
            if color == 'black':
                # Simple way to make it black: replace non-transparent pixels
                data = icon_img.getdata()
                new_data = []
                for item in data:
                    if item[3] > 0:
                        new_data.append((0, 0, 0, item[3]))
                    else:
                        new_data.append(item)
                icon_img.putdata(new_data)
            
            # Add padding to make it square and centered
            w, h = icon_img.size
            max_dim = max(w, h)
            new_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
            new_img.paste(icon_img, ((max_dim - w) // 2, (max_dim - h) // 2))
            
            # Resize
            return new_img.resize((size, size), Image.Resampling.LANCZOS)

        # Generate different versions
        # Favicon (usually black/colored)
        # PWA icons (can be white on theme color, but let's make them black on transparent for now)
        
        fav_icon = make_icon(64, 'black')
        fav_icon.save(public_dir + 'favicon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
        
        pwa_192 = make_icon(192, 'black')
        pwa_192.save(public_dir + 'pwa-192x192.png')
        
        pwa_512 = make_icon(512, 'black')
        pwa_512.save(public_dir + 'pwa-512x512.png')
        
        apple_icon = make_icon(180, 'black')
        apple_icon.save(public_dir + 'apple-touch-icon.png')
        
        print(f"✅ All icons generated in {public_dir}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    generate_icons()
