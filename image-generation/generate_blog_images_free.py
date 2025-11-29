"""
Generador de Imágenes GRATUITO usando Hugging Face Inference API
No requiere Docker ni GPU local, usa los servidores de Hugging Face
"""

import os
import sys
import requests
from pathlib import Path
import time

def generate_image_huggingface(prompt, output_path):
    """Genera una imagen usando Hugging Face Inference API (GRATIS)."""

    api_token = os.environ.get('HUGGINGFACE_TOKEN')
    if not api_token:
        print("❌ Error: HUGGINGFACE_TOKEN no está configurado")
        print("   Obtén tu token en: https://huggingface.co/settings/tokens")
        print("   Luego ejecuta: $env:HUGGINGFACE_TOKEN='tu-token-aqui'")
        return False

    print(f"🎨 Generando imagen con prompt: {prompt[:80]}...")

    # Usar Stable Diffusion XL (gratis en Hugging Face)
    # API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {api_token}"}

    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

            if response.status_code == 503:
                print(f"⏳ Modelo cargando... (intento {attempt + 1}/{max_retries})")
                time.sleep(20)
                continue

            response.raise_for_status()

            # Guardar imagen
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Imagen guardada en: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error en API de Hugging Face: {e}")
            if attempt < max_retries - 1:
                print(f"   Reintentando en 10 segundos...")
                time.sleep(10)
            else:
                return False

    return False

def create_prompt_from_post(title, repo, language):
    """Crea un prompt optimizado para Stable Diffusion XL."""

    title_lower = title.lower()

    themes = {
        'automation': 'digital workflow automation with gears and circuits',
        'ai': 'artificial intelligence neural network visualization',
        'web': 'modern web application interface design',
        'database': 'database architecture with data flow diagram',
        'cloud': 'cloud computing infrastructure',
        'security': 'cybersecurity with digital shield',
        'devops': 'CI/CD pipeline visualization',
        'testing': 'software testing and quality assurance',
        'mobile': 'mobile app interface on smartphone',
        'api': 'REST API architecture diagram',
    }

    theme = 'software development'
    for key, value in themes.items():
        if key in title_lower:
            theme = value
            break

    # Prompt optimizado para SDXL - Estilo Infografía Profesional
    prompt = (
        f"Professional 3D infographic for '{title}', {theme}. "
        f"Visualizing real-world application and solution architecture. "
        f"High-end digital art, isometric view, sleek modern design, "
        f"vibrant colors, professional lighting, sharp focus, 16:9 aspect ratio, "
        f"no text, clean composition, tech blog header style."
    )

    return prompt

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
        prompt = create_prompt_from_post(title, repo, language)

        print(f"\n📝 Procesando: {repo}")
        if generate_image_huggingface(prompt, image_path):
            generated += 1
            # Pequeña pausa para no sobrecargar la API
            time.sleep(2)
        else:
            errors += 1

    print(f"\n✨ Resumen:")
    print(f"   Generadas: {generated}")
    print(f"   Saltadas: {skipped}")
    print(f"   Errores: {errors}")
    print(f"\n💡 Costo total: $0.00 (GRATIS con Hugging Face)")

if __name__ == "__main__":
    blog_dir = Path(__file__).parent.parent / "website" / "src" / "content" / "blog"
    output_dir = Path(__file__).parent.parent / "website" / "public" / "images" / "blog"

    force = "--force" in sys.argv

    print("🆓 Usando Hugging Face Inference API (GRATIS)")
    print("⏱️  Cada imagen puede tardar 20-60 segundos...\n")

    process_blog_posts(blog_dir, output_dir, force)
