# Sistem Voucher Aman RSA

Proyek ini dibuat untuk mata kuliah Kriptografi. Kami menggunakan kode voucher sebagai contoh penerapan RSA, mulai dari pembuatan kunci, enkripsi, sampai dekripsi. Perhitungan RSA ditulis sendiri dalam Python agar setiap tahapnya bisa dipelajari melalui aplikasi.

Aplikasi menggunakan Tkinter dan mengambil studi kasus toko fiktif bernama **NusaMart**. Pelanggan bisa menerima voucher terenkripsi, membuka kodenya, lalu memakai voucher tersebut pada simulasi pesanan.

## Anggota kelompok

| No. | Nama | NRP |
| --- | --- | --- |
| 1 | Tiara Fatimah Azzahra | 50272421090 |
| 2 | Naila Cahyarani Idelia | 5027241063 |
| 3 | Diva Aulia Rosa | 5027241003 |

## Gambaran proyek

Dalam simulasi ini, NusaMart menyediakan voucher `DISKON50` untuk potongan harga 50%. Kode voucher dienkripsi dengan kunci publik pelanggan, kemudian dibuka menggunakan kunci privat yang sesuai.

Setelah kode berhasil dibuka, aplikasi memeriksa apakah kode tersebut ada dalam daftar voucher toko. Jadi, keberhasilan dekripsi dan validitas voucher diperiksa secara terpisah. Misalnya, `DISKON99` tetap bisa dienkripsi dan dikembalikan ke teks semula, tetapi tidak bisa digunakan karena tidak terdaftar.

Selain halaman belanja, tersedia halaman pembelajaran yang menampilkan perhitungan kunci, nilai karakter, hasil enkripsi, hasil dekripsi, dan log proses.

## Struktur file

```text
rsa_voucher/
    main.py           # Tampilan aplikasi dan alur simulasi
    rsa_logic.py      # Fungsi perhitungan RSA
    voucher_rules.py  # Identitas toko dan daftar voucher
    preview.png       # Gambar tampilan aplikasi
    README.md         # Dokumentasi proyek
```

## Cara menjalankan

Siapkan Python 3 dengan Tkinter/Tcl/Tk. Aplikasi ini tidak membutuhkan paket tambahan dari pip.

Dari folder `voucher-system-verify`, jalankan:

```powershell
cd rsa_voucher
python main.py
```

Jika terminal sudah berada di folder `rsa_voucher`, cukup jalankan `python main.py`. Aplikasi juga bisa dibuka dari folder induk dengan:

```powershell
python -m rsa_voucher.main
```

Jika muncul pesan `Can't find a usable init.tcl`, periksa instalasi Python dan pastikan komponen Tcl/Tk terpasang. Jika pernah mengatur `TCL_LIBRARY` atau `TK_LIBRARY`, periksa juga apakah lokasinya sudah benar.

## Cara menggunakan aplikasi

### Simulasi belanja

Halaman awal menampilkan pesanan Kemeja Katun Nusa seharga Rp200.000. Untuk mencoba voucher:

1. Klik **Ambil voucher saya** untuk menerima kode dalam bentuk terenkripsi.
2. Klik **Buka voucher** untuk mendekripsi kode. Kode yang terbuka akan masuk ke kolom voucher.
3. Klik **Gunakan voucher**. Jika kode sesuai, total belanja berubah menjadi Rp100.000.
4. Klik **Selesaikan pesanan simulasi** untuk menyelesaikan pesanan.

Pesanan juga bisa diselesaikan tanpa voucher. Untuk mengulang percobaan, klik **Mulai pesanan baru** dan konfirmasi penghapusan pesanan sebelumnya.

Coba ganti kode menjadi `DISKON99` sebelum menerapkan voucher. Aplikasi akan menolak kode tersebut dan harga tetap Rp200.000. Setelah voucher berhasil digunakan, kolom kode dikunci agar diskon tidak diterapkan berulang kali.

### Melihat proses RSA

Klik **Lihat proses RSA** untuk membuka halaman pembelajaran. Percobaan di halaman ini tidak mengubah pesanan pada halaman belanja.

Cara cepatnya, isi kode voucher lalu klik **Jalankan Demo Otomatis**. Aplikasi akan membuat kunci dari nilai contoh, mengenkripsi kode, mendekripsinya, dan memeriksa hasilnya.

Untuk mencoba satu per satu:

1. Buka tab **Pembangkitan Kunci RSA**.
2. Klik **Gunakan Nilai Contoh** untuk mengisi `p = 61` dan `q = 53`, lalu klik **Buat Kunci RSA**.
3. Buka tab **Enkripsi Voucher**, isi kode seperti `DISKON50`, lalu klik **Enkripsi Voucher**.
4. Perhatikan tabel konversi karakter dan ciphertext yang dihasilkan.
5. Klik **Kirim ke Tab Dekripsi**, lalu **Dekripsi Voucher** untuk melihat kode yang berhasil dikembalikan dan status vouchernya.

Tombol **Salin Ciphertext** bisa digunakan untuk menyalin hasil enkripsi. Input dekripsi menerima daftar angka dengan kurung siku, angka yang dipisahkan koma, atau angka yang dipisahkan spasi. Contoh input lengkap tersedia di bagian berikutnya.

Log bisa dibuka melalui **Lihat Log**. Untuk menghapus data percobaan, gunakan **Reset Aplikasi**. Pembuatan kunci baru juga menghapus hasil sebelumnya supaya hasil enkripsi lama tidak digunakan dengan kunci yang berbeda.

## Perhitungan RSA

RSA menggunakan dua kunci: kunci publik `(e, n)` untuk enkripsi dan kunci privat `(d, n)` untuk dekripsi. Kunci dibuat dari dua bilangan prima berbeda, yaitu `p` dan `q`.

Tahapan yang digunakan dalam program:

1. Hitung `n = p * q`.
2. Hitung `phi(n) = (p - 1) * (q - 1)`.
3. Pilih `e` dengan syarat `1 < e < phi(n)` dan `gcd(e, phi(n)) = 1`. Program mencoba nilai 17 terlebih dahulu, kemudian mencari bilangan ganjil lain jika nilai tersebut tidak memenuhi syarat.
4. Cari `d`, yaitu invers modular dari `e`, sehingga `(d * e) mod phi(n) = 1`.
5. Ubah setiap karakter voucher menjadi angka menggunakan `ord()`.
6. Enkripsi setiap angka dengan rumus `C = M^e mod n`.
7. Dekripsi dengan rumus `M = C^d mod n`, lalu ubah angkanya kembali menjadi karakter menggunakan `chr()`.

Pemeriksaan bilangan prima dilakukan dengan pembagian percobaan. FPB dihitung menggunakan algoritma Euclidean, sedangkan invers modular menggunakan Extended Euclidean. Perpangkatan modular menggunakan Square-and-Multiply yang ditulis sendiri, tanpa pustaka kriptografi atau fungsi bawaan `pow()`.

Nilai setiap karakter harus lebih kecil dari `n`. Karakter Unicode juga dapat digunakan selama memenuhi syarat tersebut. Untuk input dekripsi, setiap angka ciphertext harus berada dalam rentang `0 <= C < n`.

## Contoh hasil

Dengan `p = 61` dan `q = 53`, hasil perhitungannya adalah:

```text
n           = 3233
phi(n)      = 3120
e           = 17
d           = 2753
Kunci publik = (17, 3233)
Kunci privat = (2753, 3233)

Kode voucher:
DISKON50

Nilai ASCII:
68 73 83 75 79 78 53 48

Ciphertext:
[1759, 1486, 2680, 597, 1307, 3165, 1802, 624]

Hasil dekripsi:
DISKON50
```

Sebagai contoh, huruf `D` memiliki nilai 68. Setelah dienkripsi, `68^17 mod 3233` menghasilkan 1759. Saat didekripsi, `1759^2753 mod 3233` menghasilkan 68 kembali, sehingga karakter yang diperoleh adalah `D`.

## Pemeriksaan voucher

Daftar voucher berada di `voucher_rules.py`. Saat ini, kode yang terdaftar adalah `DISKON50`. Pencocokan kode memperhatikan huruf besar, huruf kecil, dan spasi. Karena itu, `diskon50` atau `DISKON50 ` dengan spasi di akhir akan ditolak.

Untuk membandingkan hasilnya, jalankan demo dengan `DISKON50` dan `DISKON99`. Keduanya dapat kembali ke teks awal setelah dekripsi, tetapi hanya `DISKON50` yang berstatus valid.

## Batasan proyek

Proyek ini digunakan untuk pembelajaran. Enkripsi dilakukan per karakter tanpa padding, dan simulasi belanja memakai nilai prima contoh yang tetap. Pemeriksaan voucher hanya mencocokkan kode dengan daftar toko; belum ada pemeriksaan pemilik, masa berlaku, penggunaan ulang, atau tanda tangan digital.

Pesanan disimpan di memori selama aplikasi berjalan. Aplikasi belum terhubung ke server atau database, dan penyelesaian pesanan tidak melibatkan pembayaran nyata.
