# apps/receipt_graphics.py
"""
QR codes and Code 128 barcodes as base64 data URIs, embeddable straight into
the receipt HTML/PDF.

Only uses qrcode + pillow, both already in requirements.txt. reportlab's
barcode renderer is deliberately avoided: it needs rlPyCairo, which is not
installed and would be another moving part on Render.
"""

import base64
from io import BytesIO

# ── Code 128 pattern table (107 entries, index = code value) ──────────
# Each string is the run-length of bar,space,bar,space,bar,space in modules.
# Every pattern sums to 11 modules; the stop pattern (106) sums to 13.
_C128 = [
    '212222', '222122', '222221', '121223', '121322', '131222', '122213', '122312', '132212', '221213',
    '221312', '231212', '112232', '122132', '122231', '113222', '123122', '123221', '223211', '221132',
    '221231', '213212', '223112', '312131', '311222', '321122', '321221', '312212', '322112', '322211',
    '212123', '212321', '232121', '111323', '131123', '131321', '112313', '132113', '132311', '211313',
    '231113', '231311', '112133', '112331', '132131', '113123', '113321', '133121', '313121', '211331',
    '231131', '213113', '213311', '213131', '311123', '311321', '331121', '312113', '312311', '332111',
    '314111', '221411', '431111', '111224', '111422', '121124', '121421', '141122', '141221', '112214',
    '112412', '122114', '122411', '142112', '142211', '241211', '221114', '413111', '241112', '134111',
    '111242', '121142', '121241', '114212', '124112', '124211', '411212', '421112', '421211', '212141',
    '214121', '412121', '111143', '111341', '131141', '114113', '114311', '411113', '411311', '113141',
    '114131', '311141', '411131', '211412', '211214', '211232', '2331112',
]

_START_B = 104
_STOP = 106


def code128b_modules(text):
    """
    Encode `text` as Code 128-B and return a list of (is_bar, width) runs.
    Raises ValueError if the text contains characters outside ASCII 32..126.
    """
    values = []
    for char in text:
        point = ord(char)
        if not 32 <= point <= 126:
            raise ValueError(f'Code 128-B cannot encode {char!r}')
        values.append(point - 32)

    checksum = _START_B
    for position, value in enumerate(values, start=1):
        checksum += position * value
    checksum %= 103

    codes = [_START_B] + values + [checksum, _STOP]

    runs = []
    for code in codes:
        pattern = _C128[code]
        for index, digit in enumerate(pattern):
            runs.append((index % 2 == 0, int(digit)))   # even index = bar
    # No extra bar here: the stop pattern (2331112) already ends with one.
    return runs


def barcode_data_uri(text, module_px=2, height_px=54, quiet_modules=10):
    """Code 128-B barcode PNG as a data URI. Returns '' if it cannot be drawn."""
    try:
        from PIL import Image, ImageDraw

        runs = code128b_modules(text)
        total_modules = sum(width for _, width in runs) + quiet_modules * 2
        image_width = total_modules * module_px

        img = Image.new('RGB', (image_width, height_px), 'white')
        draw = ImageDraw.Draw(img)

        x = quiet_modules * module_px
        for is_bar, width in runs:
            span = width * module_px
            if is_bar:
                draw.rectangle([x, 0, x + span - 1, height_px - 1], fill='black')
            x += span

        return _png_uri(img)
    except Exception:
        return ''


def qr_data_uri(data, box_px=4, border=2):
    """QR code PNG as a data URI. Returns '' if it cannot be drawn."""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M

        qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M,
                           box_size=box_px, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        return _png_uri(qr.make_image(fill_color='black', back_color='white'))
    except Exception:
        return ''


def _png_uri(img):
    buf = BytesIO()
    if hasattr(img, 'save'):
        img.save(buf, format='PNG')
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'
