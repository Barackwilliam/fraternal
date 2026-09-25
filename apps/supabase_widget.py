"""
Widget ya kupakia image kwenda Supabase, kwa Django admin na forms.

Inachukua nafasi ya `uploadcare_widget.UploadcareImageWidget`.

TOFAUTI MOJA MUHIMU YA MUUNDO

Uploadcare ilihifadhi **UUID** na URL ilijengwa wakati wa kuonyesha
(`cdn_base(uuid)`). Hapa tunahifadhi **URL kamili**.

Sababu: Supabase URL ina bucket na project ref ndani yake. Ukibadilisha
bucket au project, URL zilizojengwa kutoka UUID zingevunjika zote kwa
mara moja. URL kamili inabaki ikifanya kazi.

Gharama yake: field zinahitaji nafasi zaidi (URLField badala ya
CharField(64)). Ni bei ndogo.
"""
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class SupabaseImageWidget(forms.TextInput):
    """
    Kitufe cha kupakia + hakikisho la macho.

    Matumizi:

        class MyForm(forms.ModelForm):
            class Meta:
                widgets = {'image': SupabaseImageWidget(folder='services')}
    """

    def __init__(self, attrs=None, folder='media', help_text='', max_px=None, min_px=None):
        self.folder = folder
        self.extra_help = help_text
        # max_px: picha inapunguzwa kwenye browser KABLA ya kupakia (upande mrefu
        # usizidi max_px, WebP ~82%). Picha ya simu ya 4MB inakuwa ~150-250KB →
        # ukurasa unafunguka haraka. None = pakia kama ilivyo (tabia ya zamani).
        self.max_px = int(max_px or 0)
        # min_px: onyo (si kizuizi) picha ikiwa nyembamba kuliko hii — mf. 1200 kwa
        # Google Discover.
        self.min_px = int(min_px or 0)
        super().__init__(attrs)

    class Media:
        # Hakuna library ya nje. Uploadcare ilihitaji 200KB ya JS
        # kutoka CDN yao; hii ni fetch() ya kawaida.
        pass

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        field_id = attrs.get('id') or f'id_{name}'
        value = value or ''

        preview = ''
        if value:
            if str(value).lower().endswith('.pdf'):
                preview = format_html(
                    '<a href="{}" target="_blank" rel="noopener" '
                    'style="display:inline-block;padding:8px 14px;background:#eef2ff;'
                    'border:1px solid #c7d2fe;border-radius:6px;color:#3730a3;'
                    'text-decoration:none;font-size:13px">Fungua PDF</a>', value)
            else:
                preview = format_html(
                    '<img src="{}" alt="" style="max-width:220px;max-height:150px;'
                    'border-radius:8px;border:1px solid #ddd;display:block;'
                    'object-fit:cover">', value)

        text_input = super().render(name, value, {
            **attrs, 'id': field_id,
            'style': 'width:100%;max-width:520px;font-family:monospace;font-size:12px',
            'placeholder': 'URL itajaa yenyewe baada ya kupakia',
        }, renderer)

        return mark_safe(f'''
<div class="sb-up" data-folder="{self.folder}" data-max="{self.max_px}" data-min="{self.min_px}" style="display:grid;gap:10px;max-width:520px">
  <div id="{field_id}_preview">{preview}</div>

  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
    <label for="{field_id}_file"
           style="display:inline-flex;align-items:center;gap:7px;padding:8px 16px;
                  background:#4f46e5;color:#fff;border-radius:7px;cursor:pointer;
                  font-size:13px;font-weight:600">
      Pakia picha
    </label>
    <input type="file" id="{field_id}_file" accept="image/*,application/pdf"
           style="display:none">
    <span id="{field_id}_msg" style="font-size:12px;color:#666"></span>
  </div>

  {text_input}
  <div style="font-size:11px;color:#888;line-height:1.5">
    JPG, PNG, WEBP, GIF au PDF &middot; hadi 10MB{(" &middot; " + self.extra_help) if self.extra_help else ""}
  </div>
</div>

<script>
(function () {{
  var input   = document.getElementById('{field_id}');
  var file    = document.getElementById('{field_id}_file');
  var msg     = document.getElementById('{field_id}_msg');
  var preview = document.getElementById('{field_id}_preview');
  var folder  = file.closest('.sb-up').dataset.folder;
  if (!input || !file) return;

  function csrf() {{
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    if (m) return m[1];
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }}

  var maxPx = parseInt(file.closest('.sb-up').dataset.max || '0', 10);
  var minPx = parseInt(file.closest('.sb-up').dataset.min || '0', 10);
  var origW = 0;

  function measure(f) {{
    return new Promise(function (resolve) {{
      if (!minPx || !/^image\//i.test(f.type)) return resolve(0);
      var u = URL.createObjectURL(f), im = new Image();
      im.onload = function () {{ URL.revokeObjectURL(u); resolve(im.naturalWidth); }};
      im.onerror = function () {{ URL.revokeObjectURL(u); resolve(0); }};
      im.src = u;
    }});
  }}

  // Punguza picha kwenye browser (canvas → WebP/JPEG). GIF/PDF/SVG haziguswi.
  function shrink(f) {{
    return new Promise(function (resolve) {{
      if (!maxPx || !/^image\/(jpeg|png|webp)$/i.test(f.type)) return resolve(f);
      var url = URL.createObjectURL(f), im = new Image();
      im.onload = function () {{
        var w = im.naturalWidth, h = im.naturalHeight, k = Math.min(1, maxPx / Math.max(w, h));
        if (k === 1 && f.size < 400 * 1024) {{ URL.revokeObjectURL(url); return resolve(f); }}
        var c = document.createElement('canvas');
        c.width = Math.round(w * k); c.height = Math.round(h * k);
        var ctx = c.getContext('2d');
        ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);   // PNG yenye uwazi
        ctx.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) {{
          if (!b || b.size >= f.size) return resolve(f);
          var ext = b.type === 'image/webp' ? 'webp' : 'jpg';
          resolve(new File([b], (f.name || 'image').replace(/\.[^.]+$/, '') + '.' + ext, {{ type: b.type }}));
        }}, 'image/webp', 0.82);
      }};
      im.onerror = function () {{ URL.revokeObjectURL(url); resolve(f); }};
      im.src = url;
    }});
  }}

  file.addEventListener('change', function () {{
    var original = file.files[0];
    if (!original) return;
    msg.textContent = maxPx ? 'Inaandaa picha…' : 'Inapakia…';
    msg.style.color = '#666';

    measure(original).then(function (w) {{ origW = w; return shrink(original); }}).then(function (f) {{
    if (f !== original) msg.textContent = 'Inapakia… (' + Math.round(original.size / 1024) + 'KB → ' + Math.round(f.size / 1024) + 'KB)';
    else msg.textContent = 'Inapakia…';

    var fd = new FormData();
    fd.append('file', f);
    fd.append('folder', folder);

    return fetch('/manage/upload/', {{
      method: 'POST',
      headers: {{ 'X-CSRFToken': csrf() }},
      body: fd,
    }})
      .then(function (r) {{ return r.json(); }})
      .then(function (d) {{
        if (!d.success) {{
          msg.textContent = d.error || 'Imeshindwa.';
          msg.style.color = '#dc2626';
          return;
        }}
        input.value = d.url;
        msg.textContent = 'Imepakiwa';
        msg.style.color = '#059669';
        if (minPx && origW && origW < minPx) {{
          msg.textContent = 'Imepakiwa — ⚠️ upana ni ' + origW + 'px; Google Discover inahitaji angalau ' + minPx + 'px. Tumia picha kubwa zaidi.';
          msg.style.color = '#b45309';
        }}
        if (d.url.toLowerCase().endsWith('.pdf')) {{
          preview.innerHTML = '<a href="' + d.url + '" target="_blank" rel="noopener">Fungua PDF</a>';
        }} else {{
          preview.innerHTML = '<img src="' + d.url + '" alt="" style="max-width:220px;'
            + 'max-height:150px;border-radius:8px;border:1px solid #ddd;display:block;'
            + 'object-fit:cover">';
        }}
      }})
      .catch(function () {{
        msg.textContent = 'Muunganisho umekatika.';
        msg.style.color = '#dc2626';
      }})
      .finally(function () {{ file.value = ''; }});
    }});
  }});
}})();
</script>
''')
