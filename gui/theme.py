"""
Konfigurasi tema, warna, dan font untuk SmartStock GUI.
Terinspirasi dari desain modern dashboard inventaris bersih.
"""

# Palette Warna Utama
BG_MAIN = "#F4F6F9"          # Warna latar belakang halaman utama
BG_CARD = "#FFFFFF"          # Warna kartu dan panel konten
BG_SIDEBAR = "#FFFFFF"       # Latar belakang bilah navigasi
BORDER_COLOR = "#E2E8F0"     # Garis pemisah / border halus

# Warna Aksen
ACCENT_PRIMARY = "#4F46E5"   # Indigo modern
ACCENT_PRIMARY_HOVER = "#4338CA"
ACCENT_PRIMARY_LIGHT = "#EEF2FF"  # Latar belakang menu aktif

ACCENT_SUCCESS = "#10B981"   # Hijau (Aman / In Stock)
ACCENT_SUCCESS_LIGHT = "#ECFDF5"

ACCENT_WARNING = "#F59E0B"   # Kuning / Oranye (Low Stock / Reorder)
ACCENT_WARNING_LIGHT = "#FFFBEB"

ACCENT_DANGER = "#EF4444"    # Merah (Out of Stock / Kritis)
ACCENT_DANGER_LIGHT = "#FEF2F2"

ACCENT_INFO = "#3B82F6"      # Biru
ACCENT_INFO_LIGHT = "#EFF6FF"

# Warna Teks
TEXT_PRIMARY = "#0F172A"     # Teks utama pekat (Slate 900)
TEXT_SECONDARY = "#475569"   # Teks sekunder (Slate 600)
TEXT_MUTED = "#94A3B8"       # Teks pendukung / placeholder (Slate 400)
TEXT_LIGHT = "#FFFFFF"       # Teks di atas tombol gelap

# Font Konfigurasi
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11, "bold")
FONT_HEADING = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 10, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "normal")
FONT_STAT_VAL = (FONT_FAMILY, 20, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 9, "bold")
