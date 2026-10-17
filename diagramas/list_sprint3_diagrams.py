import re

with open('documentacion/sprint3.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all plantuml blocks
pattern = re.compile(r'(@startuml(.*?)@enduml)', re.DOTALL)
matches = pattern.findall(content)

print(f"Total PlantUML diagrams found in sprint3.md: {len(matches)}")
for idx, (block, inner) in enumerate(matches, 1):
    # find preceding header
    pos = content.find(block)
    preceding = content[:pos]
    headers = [line.strip() for line in preceding.splitlines() if line.strip().startswith('#')]
    last_header = headers[-1] if headers else "No header"
    
    # check title inside block
    title_match = re.search(r'title\s+(.*?)\n', inner)
    title = title_match.group(1).strip() if title_match else "No title"
    first_lines = [l.strip() for l in inner.strip().splitlines()[:3] if l.strip()]
    print(f"\n[{idx}] Header: {last_header}")
    print(f"    Title: {title}")
    print(f"    Snippet: {first_lines}")
