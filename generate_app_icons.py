from PIL import Image
import os

# Caminhos
source_path = r"c:\Users\Adriano\Documents\repo\catedral_familia\igreja-em-foco-app\public\icon-source.png"
public_dir = r"c:\Users\Adriano\Documents\repo\catedral_familia\igreja-em-foco-app\public"

def generate_icons():
    try:
        if not os.path.exists(source_path):
            print(f"Erro: Arquivo fonte não encontrado em {source_path}")
            return

        img = Image.open(source_path)
        
        # 1. Favicon.ico (tamanhos múltiplos)
        ico_path = os.path.join(public_dir, "favicon.ico")
        img.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        print(f"Gerado: {ico_path}")

        # 2. Favicon.png
        favicon_png_path = os.path.join(public_dir, "favicon.png")
        img.resize((192, 192), Image.Resampling.LANCZOS).save(favicon_png_path)
        print(f"Gerado: {favicon_png_path}")

        # 3. Apple Touch Icon (180x180)
        apple_path = os.path.join(public_dir, "apple-touch-icon.png")
        img.resize((180, 180), Image.Resampling.LANCZOS).save(apple_path)
        print(f"Gerado: {apple_path}")

        # 4. PWA 192x192
        pwa192_path = os.path.join(public_dir, "pwa-192x192.png")
        img.resize((192, 192), Image.Resampling.LANCZOS).save(pwa192_path)
        print(f"Gerado: {pwa192_path}")

        # 5. PWA 512x512
        pwa512_path = os.path.join(public_dir, "pwa-512x512.png")
        img.resize((512, 512), Image.Resampling.LANCZOS).save(pwa512_path)
        print(f"Gerado: {pwa512_path}")
        
    except Exception as e:
        print(f"Erro ao gerar ícones: {e}")

if __name__ == "__main__":
    generate_icons()
