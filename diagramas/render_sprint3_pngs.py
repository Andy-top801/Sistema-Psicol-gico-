import requests
import os
import re

sprint3_md_path = os.path.abspath(r"documentacion\sprint3.md")
img_dir = os.path.abspath(r"documentacion\imagenes")
os.makedirs(img_dir, exist_ok=True)

with open(sprint3_md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern to find images followed by PlantUML code blocks
pattern = re.compile(
    r'!\[(.*?)\]\(\./imagenes/(.*?)\)\s*\n+```plantuml\s*\n(@startuml[\s\S]*?@enduml)\s*\n```',
    re.MULTILINE
)

matches = pattern.findall(content)
print(f"Found {len(matches)} diagrams to render:")

for caption, filename, puml in matches:
    out_path = os.path.join(img_dir, filename)
    print(f"\nRendering '{filename}' ({caption})...", flush=True)
    try:
        payload = {
            "diagram_source": puml,
            "diagram_type": "plantuml",
            "output_format": "png"
        }
        r = requests.post("https://kroki.io/plantuml/png", json=payload, timeout=30)
        if r.status_code == 200:
            with open(out_path, "wb") as f_out:
                f_out.write(r.content)
            print(f"  -> Successfully generated {filename} ({len(r.content)} bytes)")
        else:
            print(f"  -> Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  -> Exception: {e}")

print("\n=== RENDERING PROCESS COMPLETE ===")
