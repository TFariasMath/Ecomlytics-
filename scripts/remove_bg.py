"""Script para remover el fondo blanco/claro de una imagen"""
from PIL import Image
import os

def remove_light_background(input_path, output_path, threshold=250):
    """
    Remueve el fondo claro/blanco de una imagen convirtiéndolo en transparente.
    
    Args:
        input_path: Ruta de la imagen de entrada
        output_path: Ruta de la imagen de salida (PNG)
        threshold: Umbral para considerar un pixel como "claro" (0-255)
    """
    # Abrir imagen y convertir a RGBA
    img = Image.open(input_path).convert('RGBA')
    data = img.getdata()
    
    new_data = []
    for item in data:
        # Si el pixel es muy claro (casi blanco), hacerlo transparente
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))  # Transparente
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    img.save(output_path, 'PNG')
    print(f"Imagen guardada en: {output_path}")
    return output_path

if __name__ == "__main__":
    input_image = r"C:/Users/USER/.gemini/antigravity/brain/992f2b87-0146-4703-b9bc-ab8f293cfde1/uploaded_image_1766201714151.png"
    output_image = r"c:\Users\USER\Documents\Maquina de produccion masiva\ExtraerDatosGoogleAnalitics\dashboard\assets\logo_frutos_tayen.png"
    
    # Crear directorio de assets si no existe
    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    
    # Remover fondo
    remove_light_background(input_image, output_image, threshold=240)
