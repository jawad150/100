"""Download the Montserrat weights used by the end card into fonts/."""
import os
import re
import urllib.request

os.makedirs("fonts", exist_ok=True)
url = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600"
css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/4.0"})).read().decode()
for fam, w, u in re.findall(r"font-family: '([^']+)';.*?font-weight: (\d+);.*?src: url\(([^)]+)\)", css, re.S):
    urllib.request.urlretrieve(u, f"fonts/{fam.replace(' ', '')}-{w}.ttf")
    print(f"fonts/{fam.replace(' ', '')}-{w}.ttf")
