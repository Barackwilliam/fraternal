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

    def __init__(self, attrs=None, folder='media', help_text=''):
        self.folder = folder
        self.extra_help = help_text
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
<div class="sb-up" data-folder="{self.folder}" style="display:grid;gap:10px;max-width:520px">
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

  file.addEventListener('change', function () {{
    var f = file.files[0];
    if (!f) return;
    msg.textContent = 'Inapakia…';
    msg.style.color = '#666';

    var fd = new FormData();
    fd.append('file', f);
    fd.append('folder', folder);

    fetch('/manage/upload/', {{
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
        msg.innerHTML = '✅ Imepakiwa — <b>bonyeza SAVE kuhifadhi</b>';
        msg.style.color = '#059669';
        // Ashiria mabadiliko hayajahifadhiwa (onyo la browser ukiondoka bila Save)
        try {{ input.dispatchEvent(new Event('change', {{bubbles:true}})); }} catch(e) {{}}
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
}})();
</script>
''')
