# Vielelezo vya huduma — chanzo cha SVG

Faili hizi ndizo chanzo halisi cha picha zilizopo
`apps/static/images/services/*.jpg` na `*.webp`.

Ni SVG (vector), kwa hiyo unaweza kuzihariri kwa maandishi au kwenye
Figma/Inkscape kisha kuzitoa upya kwa ukubwa wowote bila kupoteza ubora.

Rangi zote zinatoka kwenye CSS variables za `index.html`:
`--navy-950 #04101F` · `--navy-800 #0A2245` · `--gold #F5A623` ·
`--blue #2E7BF6` · `--green #1FA97A` · WhatsApp `#25D366`.

## Kuzitoa upya baada ya kuhariri

```bash
pip install cairosvg pillow
python - <<'PY'
import cairosvg
from PIL import Image
n = 'web-development'          # badilisha jina
cairosvg.svg2png(url=f'design/service-illustrations/{n}.svg',
                 write_to='/tmp/hi.png', output_width=3200, output_height=2000)
im = Image.open('/tmp/hi.png').convert('RGB').resize((1600,1000), Image.LANCZOS)
im.save(f'apps/static/images/services/{n}.jpg', 'JPEG', quality=86,
        optimize=True, progressive=True)
im.save(f'apps/static/images/services/{n}.webp', 'WEBP', quality=80, method=6)
PY
```

Inatolewa 3200×2000 kisha kupunguzwa hadi 1600×1000 — hiyo supersampling
ndiyo inatoa kingo laini.

Uwiano ni **16:10**, unaolingana na `.svc__media{aspect-ratio:16/10}`.
Kadi ina gradient nyeusi chini (`transparent 42%` hadi `rgba(4,16,31,.62)`),
kwa hiyo weka maudhui muhimu sehemu ya juu na ya kati.
