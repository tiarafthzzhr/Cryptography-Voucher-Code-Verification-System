"""Pemeriksaan voucher terhadap daftar resmi toko untuk demonstrasi."""

# Ganti atau tambahkan kode di sini sesuai voucher resmi studi kasus.
STORE_NAME = "NusaMart"
STORE_DESCRIPTION = "Toko daring pakaian dan aksesori fiktif"
# Pencocokan harus persis: huruf besar/kecil dan spasi tidak diubah.
OFFICIAL_VOUCHERS = {"DISKON50": "Diskon 50%"}


def check_voucher(code):
    """Pemeriksaan daftar terpisah dari proses enkripsi/dekripsi RSA."""
    # Cek keanggotaan kode saja. Berhasil didekripsi tidak otomatis membuat kode valid.
    if code in OFFICIAL_VOUCHERS:
        return True, f"Voucher valid: Terdaftar dalam daftar resmi toko ({OFFICIAL_VOUCHERS[code]})."
    return False, "Voucher tidak valid: Kode tidak terdaftar dalam daftar resmi toko."
