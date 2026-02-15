from PIL import Image
import os

# Caminhos
source_path = r"c:\Users\Adriano\Documents\repo\catedral_familia\igreja-em-foco-app\public\favicon.png"
dest_path = r"c:\Users\Adriano\Documents\repo\catedral_familia\igreja-em-foco-app\public\favicon.ico"

def convert_to_ico():
    try:
        if not os.path.exists(source_path):
            print(f"Erro: Arquivo fonte não encontrado em {source_path}")
            return

        img = Image.open(source_path)
        
        # Redimensionar para tamanhos padrão de ícone se necessário
        # O PIL gerencia isso automaticamente ao salvar como ICO se passarmos tamanhos
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        img.save(dest_path, sizes=icon_sizes)
        print(f"Sucesso! Ícone salvo em {dest_path}")
        
    except Exception as e:
        print(f"Erro ao converter: {e}")

if __name__ == "__main__":
    # Instalar Pillow se não existir (apenas para garantir no ambiente do script, 
    # mas assumindo que o ambiente python já tem ou podemos rodar pip install)
    # Como não posso rodar pip aqui dentro facilmente sem ser bloqueante, 
    # assumo que o usuário ou o ambiente deve ter PIL/Pillow. 
    # O ambiente flask provavelmente tem.
    convert_to_ico()
