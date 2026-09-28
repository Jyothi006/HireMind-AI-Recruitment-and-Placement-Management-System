import os
import urllib.request

IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

IMAGES = {
    'resume_screening.jpg': 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=800&q=80',
    'video_interview.jpg': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
    'candidate_matching.jpg': 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80',
    'campus_placement.jpg': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80',
    'coding_assessment.jpg': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',
    'offer_placement.jpg': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=800&q=80'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Downloading royalty-free Unsplash recruitment images...")
for filename, url in IMAGES.items():
    filepath = os.path.join(IMAGE_DIR, filename)
    print(f"Downloading {filename}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        print(f"SUCCESS: Saved {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

# Create SVG & PNG logo asset
svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 60" width="240" height="60">
  <rect width="240" height="60" rx="12" fill="#1e1b4b"/>
  <circle cx="30" cy="30" r="18" fill="#4f46e5"/>
  <path d="M30 18 L40 30 L30 42 L20 30 Z" fill="#06b6d4"/>
  <text x="60" y="38" font-family="'Inter', sans-serif" font-weight="800" font-size="24" fill="#ffffff" letter-spacing="-0.5">HireMind</text>
  <circle cx="215" cy="22" r="4" fill="#06b6d4"/>
</svg>"""

svg_path = os.path.join(IMAGE_DIR, 'logo.svg')
with open(svg_path, 'w', encoding='utf-8') as f:
    f.write(svg_logo)

png_logo_path = os.path.join(IMAGE_DIR, 'logo.png')
# Save SVG content into logo.png/logo.svg
with open(png_logo_path, 'w', encoding='utf-8') as f:
    f.write(svg_logo)

print("SUCCESS: Created brand logo files at static/images/logo.svg and static/images/logo.png!")
