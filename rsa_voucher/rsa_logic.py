"""Perhitungan RSA manual untuk demonstrasi kode voucher."""


def is_prime(n):
    """Periksa pembagi sampai akar n tanpa pustaka matematika."""
    # Bilangan di bawah 2 bukan prima; 2 adalah satu-satunya prima genap.
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Cukup periksa pembagi ganjil sampai akar n. Pembagi yang lebih besar
    # akan berpasangan dengan pembagi yang sudah diperiksa.
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def gcd(a, b):
    """Algoritma Euclidean: ulangi pembagian bersisa."""
    # Sisa pembagian terus dipakai sampai habis. Nilai terakhir adalah FPB.
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """Kembalikan (FPB, x, y) dengan a*x + b*y = FPB."""
    # Selain sisa pembagian, simpan koefisien x dan y untuk mencari invers.
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        quotient = old_r // r
        # Semua nilai diperbarui bersama agar masih memakai nilai putaran sebelumnya.
        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    if old_r < 0:
        return -old_r, -old_x, -old_y
    return old_r, old_x, old_y


def mod_inverse(e, phi):
    if phi <= 1:
        raise ValueError("Modulus invers harus lebih besar dari 1.")
    # Invers e hanya ada jika e dan phi relatif prima, yaitu FPB-nya 1.
    divisor, x, _ = extended_gcd(e, phi)
    if divisor != 1:
        raise ValueError("Invers modular tidak tersedia karena FPB bukan 1.")
    # Modulo membuat invers berada dalam rentang 0 sampai phi - 1.
    return x % phi


def mod_pow(base, exponent, modulus):
    """Square-and-Multiply: kuadratkan basis, bagi eksponen menjadi dua."""
    if exponent < 0 or modulus <= 0:
        raise ValueError("Eksponen harus nonnegatif dan modulus harus positif.")
    result = 1 % modulus
    base %= modulus
    while exponent > 0:
        # Eksponen ganjil berarti basis saat ini ikut dikalikan ke hasil.
        if exponent % 2 == 1:
            result = (result * base) % modulus
        # Kuadratkan basis dan bagi eksponen dua untuk putaran berikutnya.
        # Modulo di setiap langkah menjaga angka perhitungan tetap kecil.
        base = (base * base) % modulus
        exponent //= 2
    return result


def generate_keys(p, q):
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p dan q harus berupa bilangan prima.")
    if p == q:
        raise ValueError("p dan q tidak boleh sama.")
    # n dipakai pada kedua kunci, sedangkan phi dipakai untuk menentukan e dan d.
    n = p * q
    phi = (p - 1) * (q - 1)
    # Coba e = 17 dahulu. Jika tidak cocok, cari bilangan ganjil mulai dari 3.
    e = 17
    if not (1 < e < phi and gcd(e, phi) == 1):
        e = 3
        while e < phi and gcd(e, phi) != 1:
            e += 2
    if e >= phi:
        raise ValueError("Tidak ada eksponen e yang valid. Pilih prima lebih besar.")
    # d dipilih agar (d * e) mod phi = 1, sehingga teks bisa dipulihkan.
    d = mod_inverse(e, phi)
    return {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d,
            "public_key": (e, n), "private_key": (d, n)}


def text_to_ascii(text):
    # ord juga mendukung Unicode; nilai di luar ASCII tetap harus < n.
    return [ord(character) for character in text]


def encrypt(text, public_key):
    if not text or not text.strip():
        raise ValueError("Kode voucher tidak boleh kosong.")
    e, n = public_key
    values = text_to_ascii(text)
    # Nilai karakter harus lebih kecil dari n agar tidak hilang saat dimodulokan.
    if any(value >= n for value in values):
        raise ValueError("Nilai karakter lebih besar atau sama dengan modulus n. "
                         "Gunakan bilangan prima p dan q yang lebih besar.")
    # Enkripsi per karakter: C = M^e mod n. Nilai asli ikut dikembalikan untuk tabel.
    return values, [mod_pow(value, e, n) for value in values]


def decrypt(ciphertext, private_key):
    d, n = private_key
    if not ciphertext:
        raise ValueError("Ciphertext tidak boleh kosong.")
    # Tolak angka di luar rentang RSA dan tipe lain, termasuk boolean.
    if any(type(value) is not int or not 0 <= value < n for value in ciphertext):
        raise ValueError("Setiap ciphertext harus bilangan bulat dengan 0 <= C < n.")
    # Dekripsi per angka: M = C^d mod n.
    values = [mod_pow(value, d, n) for value in ciphertext]
    # Tidak semua angka merupakan karakter Unicode yang valid.
    # Rentang surrogate (D800-DFFF) juga tidak diterima sebagai karakter tunggal.
    if any(value > 0x10FFFF or 0xD800 <= value <= 0xDFFF for value in values):
        raise ValueError("Hasil dekripsi bukan karakter Unicode yang valid. Periksa kunci dan ciphertext.")
    return values, "".join(chr(value) for value in values)
