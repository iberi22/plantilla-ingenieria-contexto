"""
Generador de Imágenes para Blog Posts usando Replicate API
Costo: ~$0.003 USD por imagen con Flux Schnell
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

def extract_frontmatter(md_file):
    """Extrae el frontmatter de un archivo markdown."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    return {
        'frontmatter': parts[1],
        'content': parts[2],
        'file': md_file
    }

def parse_title_and_repo(frontmatter):
    """Extrae el título y repo del frontmatter."""
    lines = frontmatter.strip().split('\n')
    data = {}

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"')
            data[key] = value

    return data.get('title', ''), data.get('repo', ''), data.get('language', 'Unknown')

def generate_image_replicate(prompt, output_path):
    """Genera una imagen usando Replicate API (Flux Schnell)."""

    api_token = os.environ.get('REPLICATE_API_TOKEN')
    if not api_token:
        print("❌ Error: REPLICATE_API_TOKEN no está configurado")
        print("   Obtén tu token en: https://replicate.com/account/api-tokens")
        print("   Luego ejecuta: $env:REPLICATE_API_TOKEN='tu-token-aqui'")
        return False

    print(f"🎨 Generando imagen con prompt: {prompt[:80]}...")

    # API de Replicate
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "f2ab8a5569e71f8e9e69c5e3b6ff75d2d0c39c2b6e6f9e4e3f0a2d9c8b7a6f5e",  # Flux Schnell
        "input": {
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "16:9",
            "output_format": "png",
            "output_quality": 90
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        prediction = response.json()

        # Esperar a que termine
        prediction_url = prediction['urls']['get']
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            response = requests.get(prediction_url, headers=headers)
            prediction = response.json()

            if prediction['status'] == 'succeeded':
                image_url = prediction['output'][0] if isinstance(prediction['output'], list) else prediction['output']

                # Descargar la imagen
                img_response = requests.get(image_url)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, 'wb') as f:
                    f.write(img_response.content)

                print(f"✅ Imagen guardada en: {output_path}")
                return True

            elif prediction['status'] == 'failed':
                print(f"❌ Error generando imagen: {prediction.get('error', 'Unknown error')}")
                return False

            attempt += 1
            import time
            time.sleep(2)

        print("❌ Timeout esperando generación de imagen")
        return False

    except Exception as e:
        print(f"❌ Error en API de Replicate: {e}")
        return False

def create_prompt_from_post(title, repo, language, content_preview=""):
    """Crea un prompt para generar la imagen del blog post."""

    # Extraer categoría/tema del título
    title_lower = title.lower()

    themes = {
        'automation': 'automation workflow, gears and circuits',
        'ai': 'artificial intelligence, neural network visualization',
        'web': 'modern web interface, responsive design',
        'database': 'database architecture, data flow',
        'cloud': 'cloud infrastructure, distributed systems',
        'security': 'cybersecurity, encryption, shield',
        'devops': 'CI/CD pipeline, deployment automation',
        'testing': 'software testing, quality assurance',
        'mobile': 'mobile app interface, smartphone',
        'api': 'API architecture, REST endpoints',
    }

    theme = 'modern software development'
    for key, value in themes.items():
        if key in title_lower or key in content_preview.lower():
            theme = value
            break

    prompt = f"""Professional 3D infographic for '{title}' project.
    Theme: {theme}.
    Visualizing real-world application and solution architecture.
    Style: High-end digital art, isometric view, sleek modern design,
    vibrant colors, professional lighting, sharp focus, {language} programming language aesthetic.
    High quality, 16:9 aspect ratio, no text."""

    return prompt

def process_blog_posts(blog_dir, output_dir, force=False):
    """Procesa todos los posts del blog y genera imágenes faltantes."""

    blog_path = Path(blog_dir)
    output_path = Path(output_dir)

    md_files = list(blog_path.rglob('*.md'))
    print(f"📁 Encontrados {len(md_files)} archivos markdown")

    generated = 0
    skipped = 0
    errors = 0

    for md_file in md_files:
        data = extract_frontmatter(md_file)
        if not data:
            continue

        title, repo, language = parse_title_and_repo(data['frontmatter'])
        if not title or not repo:
            print(f"⚠️  Saltando {md_file.name}: No tiene title o repo")
            skipped += 1
            continue

        # Determinar ruta de salida
        repo_name = repo.replace('/', '-')
        image_filename = f"{repo_name}-header.png"
        image_path = output_path / image_filename

        if image_path.exists() and not force:
            print(f"⏭️  Saltando {repo}: Ya existe imagen")
            skipped += 1
            continue

        # Generar prompt y crear imagen
        content_preview = data['content'][:500]
        prompt = create_prompt_from_post(title, repo, language, content_preview)

        print(f"\n📝 Procesando: {repo}")
        if generate_image_replicate(prompt, image_path):
            generated += 1
        else:
            errors += 1

    print(f"\n✨ Resumen:")
    print(f"   Generadas: {generated}")
    print(f"   Saltadas: {skipped}")
    print(f"   Errores: {errors}")

if __name__ == "__main__":
    blog_dir = Path(__file__).parent.parent / "website" / "src" / "content" / "blog"
    output_dir = Path(__file__).parent.parent / "website" / "public" / "images" / "blog"

    force = "--force" in sys.argv

    process_blog_posts(blog_dir, output_dir, force)
