"""Antarmuka demonstrasi RSA manual, seluruh teks berbahasa Indonesia."""

import re
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

try:
    from .rsa_logic import generate_keys, encrypt, decrypt, text_to_ascii
    from .voucher_rules import OFFICIAL_VOUCHERS, STORE_NAME, STORE_DESCRIPTION, check_voucher
except ImportError:
    from rsa_logic import generate_keys, encrypt, decrypt, text_to_ascii
    from voucher_rules import OFFICIAL_VOUCHERS, STORE_NAME, STORE_DESCRIPTION, check_voucher


def parse_ciphertext(text):
    """Terima angka dipisahkan koma/spasi, dengan atau tanpa kurung siku."""
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    # Setelah kurung dibuang, hanya angka dengan pemisah koma atau spasi yang diterima.
    if not text or not re.fullmatch(r"[0-9]+(?:(?:\s*,\s*|\s+)[0-9]+)*", text):
        raise ValueError("Format ciphertext tidak valid. Masukkan angka dipisahkan koma atau spasi.")
    return [int(value) for value in re.split(r"[\s,]+", text)]


# Jendela pembelajaran berisi input kunci, tabel perhitungan, dan log RSA.
class VoucherApp:
    def __init__(self, root):
        self.root = root
        self.keys = None
        self.ciphertext = []
        self.original = None
        root.title(f"{STORE_NAME} | Sistem Voucher Aman RSA")
        root.geometry("1100x850")
        root.minsize(980, 800)
        root.configure(background="#f2eee5")
        style = ttk.Style(root)
        style.theme_use("clam")
        # Palet kertas dan tinta, seperti meja kasir toko.
        paper, ink, muted, line = "#f2eee5", "#27251f", "#746e62", "#d1c9ba"
        style.configure("TFrame", background=paper)
        style.configure("TLabel", font=("Segoe UI", 10), background=paper, foreground=ink)
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 7), background=paper,
                        foreground=ink, borderwidth=1, bordercolor=line, relief="solid")
        style.map("TButton", background=[("active", "#e5ddce")])
        for name in ("Primary.TButton", "Accent.TButton"):
            style.configure(name, background=ink, foreground="#fffdf7", bordercolor=ink)
            style.map(name, background=[("active", "#494538")])
        style.configure("Title.TLabel", font=("Georgia", 30, "bold"), background=paper, foreground=ink)
        style.configure("Header.TLabel", background=paper, foreground=muted, font=("Consolas", 9))
        style.configure("Header.TFrame", background=paper)
        style.configure("Step.TLabel", font=("Georgia", 17), foreground=ink)
        style.configure("TLabelframe", background=paper, bordercolor=line, relief="solid")
        style.configure("TLabelframe.Label", background=paper, foreground=muted, font=("Consolas", 9))
        style.configure("TEntry", padding=7, fieldbackground="#fffdf7", bordercolor=line)
        style.configure("TNotebook", background=paper, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(20, 10), background=paper, foreground=muted)
        style.map("TNotebook.Tab", background=[("selected", ink)], foreground=[("selected", "#fffdf7")])
        style.configure("Treeview", font=("Consolas", 10), rowheight=28, background="#fffdf7",
                        fieldbackground="#fffdf7", foreground=ink, borderwidth=0)
        style.configure("Treeview.Heading", font=("Consolas", 9, "bold"), background="#e5ddce", foreground=ink, padding=7)
        style.map("Treeview", background=[("selected", "#ddd3be")], foreground=[("selected", ink)])
        style.configure("Valid.TLabel", background="#fffdf7", foreground="#35563d", padding=8, font=("Consolas", 11, "bold"))
        style.configure("Invalid.TLabel", background="#fffdf7", foreground="#9b3a28", padding=8, font=("Consolas", 11, "bold"))
        style.configure("Neutral.TLabel", background="#fffdf7", foreground=muted, padding=8, font=("Consolas", 10))
        style.configure("Receipt.TFrame", background="#fffdf7")
        style.configure("Receipt.TLabel", background="#fffdf7", foreground=ink, font=("Consolas", 10))
        container = ttk.Frame(root, padding=16)
        container.pack(fill="both", expand=True)
        header = ttk.Frame(container, style="Header.TFrame", padding=(4, 6))
        header.pack(fill="x", pady=(0, 10))
        brand = ttk.Frame(header)
        brand.pack(side="left")
        ttk.Label(brand, text=STORE_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand, text="PAKAIAN / AKSESORI / VOUCHER", style="Header.TLabel").pack(anchor="w")
        details = ttk.Frame(header)
        details.pack(side="right")
        ttk.Label(details, text="MEJA VOUCHER", style="Header.TLabel").pack(anchor="e")
        ttk.Label(details, text="Pengiriman kode dengan RSA manual").pack(anchor="e", pady=3)
        ttk.Label(details, text="Toko fiktif ? Demonstrasi kriptografi", style="Header.TLabel").pack(anchor="e")
        ttk.Separator(container).pack(fill="x")
        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=(4, 10))
        self.progress = tk.StringVar(value="Mulai di langkah 1 · Gunakan nilai contoh untuk demo")
        ttk.Label(actions, textvariable=self.progress).pack(side="left")
        ttk.Button(actions, text="Identitas Kelompok", command=self.about).pack(side="right")
        ttk.Button(actions, text="Lihat Log", command=self.toggle_log).pack(side="right", padx=4)
        ttk.Button(actions, text="Reset Aplikasi", command=self.reset).pack(side="right", padx=8)
        self.voucher = tk.StringVar(value="DISKON50")
        demo = ttk.Frame(container, padding=(0, 0, 0, 10))
        demo.pack(fill="x")
        ttk.Label(demo, text="Kode voucher:").pack(side="left")
        ttk.Entry(demo, textvariable=self.voucher, width=18).pack(side="left", padx=8)
        ttk.Button(demo, text="Jalankan Demo Otomatis →", style="Accent.TButton", command=self.run_demo).pack(side="left")
        ttk.Label(demo, text="  Kunci → Enkripsi → Dekripsi → Validasi", foreground="#746e62").pack(side="left")
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        self.tabs = []
        for title in ("Kunci pelanggan", "Pengiriman toko", "Penerimaan & pemeriksaan"):
            tab = ttk.Frame(self.notebook, padding=12)
            self.notebook.add(tab, text=title)
            self.tabs.append(tab)
        self.p = tk.StringVar()
        self.q = tk.StringVar()
        self.public = tk.StringVar(value="Silakan buat kunci RSA terlebih dahulu.")
        self.private = tk.StringVar(value="Silakan buat kunci RSA terlebih dahulu.")
        self.calculation = tk.StringVar(value="Hasil perhitungan akan tampil setelah kunci dibuat.")
        self.encrypted_summary = tk.StringVar()
        self.decrypted_summary = tk.StringVar()
        self.voucher_status = tk.StringVar(value="Status voucher akan muncul setelah dekripsi.")
        self.build_keys()
        self.build_encrypt()
        self.build_decrypt()
        log_frame = ttk.LabelFrame(container, text="Log Proses", padding=6)
        self.log_frame = log_frame
        self.log_box = ScrolledText(log_frame, height=3, font=("Consolas", 9), state="disabled")
        self.log_box.pack(fill="x")
        # Bidang teks tetap dapat dipilih dan disalin saat hasil hanya-baca.
        for widget in (self.cipher_input, self.cipher_output, self.log_box):
            widget.configure(background="#fffdf7", foreground="#27251f", insertbackground="#27251f",
                             relief="flat", borderwidth=0, padx=10, pady=6, selectbackground="#ddd3be")

    # Penjelasan bisa dibuka dan ditutup supaya tabel tetap punya ruang.
    def explanation(self, tab, text):
        section = ttk.Frame(tab)
        section.pack(side="bottom", fill="x", pady=(8, 0))
        panel = ttk.LabelFrame(section, text="Penjelasan Proses", padding=8)
        def toggle():
            if panel.winfo_manager():
                panel.pack_forget()
            else:
                panel.pack(fill="x", pady=4)
        ttk.Button(section, text="Penjelasan perhitungan RSA", command=toggle).pack(anchor="w")
        ttk.Label(panel, text=text, wraplength=840, justify="left").pack(anchor="w")

    def heading(self, tab, text):
        ttk.Label(tab, text=text, style="Step.TLabel").pack(anchor="w", pady=(0, 10))

    # Siapkan kolom p dan q serta tempat menampilkan kunci dan perhitungannya.
    def build_keys(self):
        tab = self.tabs[0]
        self.heading(tab, "Kunci untuk pelanggan")
        inputs = ttk.LabelFrame(tab, text="Bilangan Prima", padding=10)
        inputs.pack(fill="x")
        for column, (label, variable) in enumerate((("Bilangan Prima p:", self.p), ("Bilangan Prima q:", self.q))):
            ttk.Label(inputs, text=label).grid(row=0, column=column * 2, padx=6)
            ttk.Entry(inputs, textvariable=variable, width=14).grid(row=0, column=column * 2 + 1, padx=6)
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Gunakan Nilai Contoh", command=self.example).pack(side="left")
        ttk.Button(buttons, text="Buat Kunci RSA", style="Primary.TButton", command=self.make_keys).pack(side="left", padx=8)
        ttk.Button(buttons, text="Lanjut ke Enkripsi →", command=lambda: self.notebook.select(self.tabs[1])).pack(side="right")
        calculation = ttk.LabelFrame(tab, text="Perhitungan RSA", padding=10)
        calculation.pack(fill="x")
        ttk.Label(calculation, textvariable=self.calculation, justify="left", font=("Consolas", 12)).pack(anchor="w")
        keys = ttk.Frame(tab)
        keys.pack(fill="x", pady=8)
        for label, variable in (("Public Key (e, n)", self.public), ("Private Key (d, n)", self.private)):
            box = ttk.LabelFrame(keys, text=label, padding=10)
            box.pack(side="left", fill="both", expand=True, padx=4)
            ttk.Label(box, textvariable=variable).pack(anchor="w")
        self.explanation(tab, "1. Pilih prima p dan q yang berbeda.  2. Hitung n = p × q.\n"
                         "3. Hitung phi(n) = (p - 1)(q - 1).  4. Pilih 1 < e < phi dengan gcd(e, phi) = 1.\n"
                         "5. Cari d menggunakan Extended Euclidean: (d × e) mod phi = 1.\n"
                         "6. Public Key = (e, n).  7. Private Key = (d, n).")

    # Tabel yang sama dipakai untuk enkripsi dan dekripsi, dengan kolom berbeda.
    def table(self, tab, columns):
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, pady=8)
        tree = ttk.Treeview(frame, columns=tuple(range(len(columns))), show="headings", height=6)
        for i, title in enumerate(columns):
            tree.heading(i, text=title)
            tree.column(i, width=260 if title == "Rumus" else 150, minwidth=100, anchor="center")
        vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    # Tab ini menampilkan perubahan kode voucher menjadi angka ciphertext.
    def build_encrypt(self):
        tab = self.tabs[1]
        self.heading(tab, "Siapkan kiriman voucher")
        ttk.Label(tab, text="Public Key aktif:").pack(anchor="w")
        ttk.Label(tab, textvariable=self.public).pack(anchor="w")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text="Kode Voucher:").pack(side="left")
        ttk.Entry(row, textvariable=self.voucher).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(row, text="Enkripsi Voucher", style="Primary.TButton", command=self.encrypt_voucher).pack(side="left")
        ttk.Label(tab, text="Coba DISKON50 (resmi) atau DISKON99 (tidak terdaftar) untuk membandingkan hasil.", foreground="#746e62").pack(anchor="w", pady=(0, 6))
        ttk.Label(tab, textvariable=self.encrypted_summary, wraplength=840).pack(anchor="w")
        self.explanation(tab, "C = M^e mod n untuk setiap karakter. M = nilai ASCII/Unicode plaintext, "
                         "e = eksponen publik, n = modulus, C = ciphertext. Setiap M harus lebih kecil dari n.")
        output = ttk.LabelFrame(tab, text="Ciphertext", padding=6)
        output.pack(side="bottom", fill="x", pady=4)
        self.cipher_output = ScrolledText(output, height=2, font=("Consolas", 10), state="disabled")
        self.cipher_output.pack(fill="x")
        buttons = ttk.Frame(output)
        buttons.pack(fill="x", pady=(6, 0))
        ttk.Button(buttons, text="Salin Ciphertext", command=self.copy_ciphertext).pack(side="left")
        ttk.Button(buttons, text="Kirim ke Tab Dekripsi →", style="Accent.TButton", command=self.send_ciphertext).pack(side="left", padx=8)
        self.encrypt_table = self.table(tab, ("Karakter", "ASCII (M)", "Rumus", "Ciphertext (C)"))

    # Tab ini menerima ciphertext dan menampilkan kode beserta status vouchernya.
    def build_decrypt(self):
        tab = self.tabs[2]
        self.heading(tab, "Buka kiriman, periksa kode")
        ttk.Label(tab, text="Private Key aktif:").pack(anchor="w")
        ttk.Label(tab, textvariable=self.private).pack(anchor="w")
        ttk.Label(tab, text="Voucher resmi toko: " + ", ".join(OFFICIAL_VOUCHERS)).pack(anchor="w")
        ttk.Label(tab, text="Ciphertext (angka dipisahkan koma atau spasi):").pack(anchor="w", pady=(8, 0))
        self.cipher_input = ScrolledText(tab, height=2, font=("Consolas", 10))
        self.cipher_input.pack(fill="x", pady=4)
        ttk.Button(tab, text="Dekripsi & Periksa Voucher", style="Accent.TButton", command=self.decrypt_voucher).pack(anchor="w")
        self.explanation(tab, "M = C^d mod n untuk setiap ciphertext. C = ciphertext, d = eksponen privat, "
                         "n = modulus, M = nilai plaintext yang dipulihkan. Gunakan chr(M) untuk memperoleh karakter. "
                         "Setelah dekripsi, periksa kode terhadap daftar resmi toko untuk menentukan validitas voucher.")
        receipt = ttk.Frame(tab, style="Receipt.TFrame", padding=(16, 10))
        receipt.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Label(receipt, text=f"{STORE_NAME.upper()} / BUKTI PEMERIKSAAN", style="Receipt.TLabel").pack(anchor="w")
        ttk.Separator(receipt).pack(fill="x", pady=5)
        self.status_label = ttk.Label(receipt, textvariable=self.voucher_status, style="Neutral.TLabel", wraplength=840)
        self.status_label.pack(fill="x")
        ttk.Label(receipt, textvariable=self.decrypted_summary, style="Receipt.TLabel", wraplength=840, justify="left").pack(anchor="w")
        self.decrypt_table = self.table(tab, ("Ciphertext (C)", "Rumus", "ASCII Hasil Dekripsi (M)", "Karakter"))

    # Kotak log dibuka sebentar untuk menambah tulisan, lalu dikunci kembali.
    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def toggle_log(self):
        if self.log_frame.winfo_manager():
            self.log_frame.pack_forget()
        else:
            self.log_frame.pack(fill="x", pady=(8, 0))

    # Widget yang terkunci perlu dibuka sebelum isinya diganti lewat program.
    def set_text(self, widget, text, readonly=False):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        if readonly:
            widget.configure(state="disabled")

    def clear_results(self):
        # Hapus hasil lama agar ciphertext dari kunci lama tidak dipakai kembali.
        self.ciphertext = []
        self.original = None
        self.encrypted_summary.set("")
        self.decrypted_summary.set("")
        self.voucher_status.set("Status voucher akan muncul setelah dekripsi.")
        self.status_label.configure(style="Neutral.TLabel")
        self.set_text(self.cipher_output, "", True)
        self.set_text(self.cipher_input, "")
        for tree in (self.encrypt_table, self.decrypt_table):
            for item in tree.get_children():
                tree.delete(item)

    # Hanya mengisi p dan q; kunci baru dibuat saat tombol pembuatan kunci ditekan.
    def example(self):
        self.p.set("61")
        self.q.set("53")

    def run_demo(self):
        """Otomatisasi klik; seluruh perhitungan tetap memakai fungsi RSA manual."""
        if not self.voucher.get().strip():
            self.error("Kode voucher tidak boleh kosong. Isi kode sebelum menjalankan demo.")
            return
        self.log(f"[INFO] Demo {STORE_NAME}: pelanggan membuat kunci; toko mengirim voucher terenkripsi")
        # Prima contoh dipilih otomatis agar hasil demo mudah dijelaskan.
        self.example()
        # Hentikan demo jika suatu tahap gagal. Pesan sukses tiap tahap disembunyikan
        # supaya pengguna cukup melihat hasil akhir.
        if not self.make_keys(notify=False):
            return
        if not self.encrypt_voucher(notify=False):
            return
        self.send_ciphertext()
        self.decrypt_voucher()

    def error(self, error):
        self.log("[KESALAHAN] " + str(error))
        messagebox.showerror("Kesalahan", str(error), parent=self.root)

    # Enkripsi dan dekripsi harus memakai pasangan kunci yang sudah dibuat.
    def require_keys(self):
        if self.keys is None:
            raise ValueError("Silakan buat kunci RSA terlebih dahulu.")

    def make_keys(self, notify=True):
        try:
            if not self.p.get().strip() or not self.q.get().strip():
                raise ValueError("Nilai p dan q tidak boleh kosong.")
            try:
                p, q = int(self.p.get()), int(self.q.get())
            except ValueError:
                raise ValueError("p dan q harus berupa bilangan bulat.") from None
            keys = generate_keys(p, q)
            # Validasi ukuran modulus terhadap voucher yang sedang diisi.
            if any(value >= keys["n"] for value in text_to_ascii(self.voucher.get())):
                raise ValueError("Modulus n terlalu kecil untuk voucher saat ini. Gunakan prima p dan q lebih besar.")
            self.clear_results()
            self.keys = keys
            self.public.set(str(keys["public_key"]))
            self.private.set(str(keys["private_key"]))
            self.calculation.set(f"p = {p}     q = {q}\n"
                                 f"n = p × q = {keys['n']}\n"
                                 f"phi(n) = (p - 1)(q - 1) = {keys['phi']}\n"
                                 f"e = {keys['e']}     d = {keys['d']}\n"
                                 f"gcd(e, phi) = 1; (d × e) mod phi = {(keys['d'] * keys['e']) % keys['phi']}")
            self.log(f"[INFO] p = {p} dan q = {q} adalah bilangan prima")
            for name in ("n", "phi", "e"):
                self.log(f"[INFO] {name} = {keys[name]}")
            self.log(f"[INFO] Invers modular melalui Extended Euclidean: d = {keys['d']}")
            self.log("[BERHASIL] Kunci RSA berhasil dibuat")
            self.progress.set("Kunci siap · Lanjut ke langkah 2 untuk mengenkripsi voucher")
            if notify:
                messagebox.showinfo("Berhasil", "Kunci RSA berhasil dibuat.", parent=self.root)
            return True
        except ValueError as error:
            self.error(error)
            return False

    def encrypt_voucher(self, notify=True):
        try:
            self.require_keys()
            text = self.voucher.get()
            values, ciphertext = encrypt(text, self.keys["public_key"])
            self.clear_results()
            # Simpan teks awal untuk membandingkannya dengan hasil dekripsi nanti.
            self.original, self.ciphertext = text, ciphertext
            self.encrypted_summary.set(f"Voucher Asli: {text}\nNilai ASCII/Unicode: " + " ".join(map(str, values)))
            e, n = self.keys["public_key"]
            self.log("[INFO] Mengubah kode voucher menjadi ASCII/Unicode")
            # Satu baris tabel menunjukkan karakter, nilai angka, rumus, dan hasilnya.
            for character, value, cipher in zip(text, values, ciphertext):
                formula = f"{value}^{e} mod {n}"
                self.encrypt_table.insert("", "end", values=(character, value, formula, cipher))
                self.log(f"[INFO] Karakter {character!r}: M = {value}; C = {formula} = {cipher}")
            self.set_text(self.cipher_output, str(ciphertext), True)
            self.log("[BERHASIL] Voucher berhasil dienkripsi")
            self.progress.set("Ciphertext siap · Kirim ke langkah 3 untuk dekripsi dan pemeriksaan")
            if notify:
                messagebox.showinfo("Berhasil", "Voucher berhasil dienkripsi.", parent=self.root)
            return True
        except ValueError as error:
            self.error(error)
            return False

    def copy_ciphertext(self):
        if not self.ciphertext:
            self.error("Enkripsi voucher terlebih dahulu.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(str(self.ciphertext))
        messagebox.showinfo("Berhasil", "Ciphertext berhasil disalin.", parent=self.root)

    # Pindahkan hasil enkripsi ke input dekripsi agar tidak perlu menyalin manual.
    def send_ciphertext(self):
        if not self.ciphertext:
            self.error("Enkripsi voucher terlebih dahulu.")
            return
        self.set_text(self.cipher_input, str(self.ciphertext))
        self.notebook.select(self.tabs[2])

    def decrypt_voucher(self, notify=True):
        # Bersihkan hasil sebelumnya agar input yang gagal tidak tampak berhasil.
        self.decrypted_summary.set("")
        self.voucher_status.set("Menunggu hasil dekripsi dan pemeriksaan.")
        self.status_label.configure(style="Neutral.TLabel")
        for item in self.decrypt_table.get_children():
            self.decrypt_table.delete(item)
        try:
            self.require_keys()
            ciphertext = parse_ciphertext(self.cipher_input.get("1.0", "end"))
            values, text = decrypt(ciphertext, self.keys["private_key"])
            d, n = self.keys["private_key"]
            self.log("[INFO] Melakukan dekripsi dan mengubah ASCII/Unicode menjadi karakter")
            for cipher, value, character in zip(ciphertext, values, text):
                formula = f"{cipher}^{d} mod {n}"
                self.decrypt_table.insert("", "end", values=(cipher, formula, value, character))
                self.log(f"[INFO] M = {formula} = {value}; karakter = {character!r}")
            result = "Voucher Hasil Dekripsi: " + text
            result += "\nVoucher berhasil didekripsi."
            # Teks yang berhasil didekripsi belum tentu merupakan voucher terdaftar.
            valid, status = check_voucher(text)
            self.voucher_status.set(status)
            self.status_label.configure(style="Valid.TLabel" if valid else "Invalid.TLabel")
            # Bandingkan teks hanya jika ada voucher awal dari proses enkripsi sebelumnya.
            if self.original is not None:
                result += ("\nVerifikasi berhasil: Voucher asli dan voucher hasil dekripsi sama." if text == self.original
                           else "\nVerifikasi: Hasil berbeda dari voucher terakhir yang dienkripsi.")
            self.decrypted_summary.set(result)
            self.log("[BERHASIL] Voucher berhasil dipulihkan")
            self.log(("[VALID] " if valid else "[TIDAK VALID] ") + status)
            self.progress.set("Demo selesai · Voucher " + ("terdaftar dalam daftar resmi" if valid else "tidak terdaftar dalam daftar resmi"))
            if notify:
                messagebox.showinfo("Hasil Dekripsi dan Pemeriksaan Voucher",
                                    "Voucher berhasil didekripsi.\n\n" + status, parent=self.root)
        except ValueError as error:
            self.voucher_status.set("Pemeriksaan belum selesai: " + str(error))
            self.progress.set("Periksa input ciphertext · Dekripsi dan pemeriksaan belum selesai")
            self.error(error)

    def reset(self):
        if not messagebox.askyesno("Konfirmasi Reset", "Hapus seluruh input, kunci, hasil, dan log proses?", parent=self.root):
            return
        self.keys = None
        for variable in (self.p, self.q, self.voucher):
            variable.set("")
        self.public.set("Silakan buat kunci RSA terlebih dahulu.")
        self.private.set("Silakan buat kunci RSA terlebih dahulu.")
        self.calculation.set("Hasil perhitungan akan tampil setelah kunci dibuat.")
        self.clear_results()
        self.progress.set("Mulai di langkah 1 · Gunakan nilai contoh untuk demo")
        self.set_text(self.log_box, "", True)
        self.notebook.select(self.tabs[0])

    def about(self):
        # Ganti Kelompok X, nama mahasiswa, dan NRP dengan identitas kelompok.
        messagebox.showinfo("Identitas Kelompok", "Mata Kuliah: Kriptografi\n\n"
                            "Judul Proyek: Implementasi RSA Manual untuk Pengamanan Kode Voucher Digital\n\n"
                            "Kelompok: Kelompok X\n\nAnggota:\n"
                            "1. Nama Mahasiswa - NRP\n2. Nama Mahasiswa - NRP\n3. Nama Mahasiswa - NRP", parent=self.root)


# Halaman belanja menyimpan pesanan selama aplikasi berjalan.
class StoreApp:
    """Alur pelanggan; perhitungan RSA berlangsung di balik tindakan toko."""

    def __init__(self, root):
        self.root = root
        self.keys = None
        # delivery berisi ciphertext, sedangkan recovered berisi kode yang sudah dibuka.
        self.delivery = []
        self.recovered = None
        self.applied = False
        self.completed = False
        self.detail_window = None
        root.title(f"{STORE_NAME} | Pesanan Anda")
        root.geometry("1020x740")
        root.minsize(920, 700)
        style = ttk.Style(root)
        style.theme_use("clam")
        paper, ink = "#f2eee5", "#27251f"
        root.configure(background=paper)
        style.configure("TFrame", background=paper)
        style.configure("TLabel", background=paper, foreground=ink, font=("Segoe UI", 10))
        style.configure("TButton", background=paper, foreground=ink, padding=(14, 9), font=("Segoe UI", 10))
        style.configure("Shop.Primary.TButton", background=ink, foreground="#fffdf7")
        style.map("Shop.Primary.TButton", background=[("disabled", "#d8d1c4"), ("active", "#4a443a")], foreground=[("disabled", "#777063")])
        style.configure("Shop.Brand.TLabel", font=("Georgia", 28, "bold"))
        style.configure("Shop.Heading.TLabel", font=("Georgia", 18))
        style.configure("Shop.Total.TLabel", font=("Georgia", 23, "bold"))
        style.configure("Shop.Muted.TLabel", foreground="#746e62")
        style.configure("Shop.Card.TFrame", background="#fffdf7")
        style.configure("Shop.Card.TLabel", background="#fffdf7", foreground=ink)
        style.configure("Shop.Code.TLabel", background="#fffdf7", font=("Consolas", 22, "bold"))
        style.configure("TEntry", fieldbackground="#fffdf7", padding=8)
        body = ttk.Frame(root, padding=24)
        body.pack(fill="both", expand=True)
        header = ttk.Frame(body)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text=STORE_NAME, style="Shop.Brand.TLabel").pack(side="left")
        ttk.Label(header, text="Pakaian & aksesori\nToko fiktif / transaksi simulasi", style="Shop.Muted.TLabel", justify="right").pack(side="right")
        ttk.Separator(body).pack(fill="x")
        ttk.Label(body, text="Pesanan Anda", style="Shop.Heading.TLabel").pack(anchor="w", pady=(18, 4))
        ttk.Label(body, text="Periksa barang dan gunakan voucher sebelum menyelesaikan pesanan.", style="Shop.Muted.TLabel").pack(anchor="w")
        content = ttk.Frame(body)
        content.pack(fill="both", expand=True, pady=18)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        ttk.Label(left, text="01 / TAS BELANJA", style="Shop.Muted.TLabel").pack(anchor="w")
        item = ttk.Frame(left, style="Shop.Card.TFrame", padding=18)
        item.pack(fill="x", pady=(10, 22))
        ttk.Label(item, text="Kemeja Katun Nusa", style="Shop.Card.TLabel", font=("Georgia", 17)).pack(anchor="w")
        ttk.Label(item, text="Warna krem / Ukuran M / 1 barang", style="Shop.Card.TLabel").pack(anchor="w", pady=8)
        ttk.Label(item, text="Rp200.000", style="Shop.Card.TLabel", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(left, text="02 / VOUCHER DARI TOKO", style="Shop.Muted.TLabel").pack(anchor="w")
        self.offer = tk.StringVar(value="Ada voucher diskon 50% untuk pesanan ini.\nAmbil voucher agar toko mengirimkannya kepada Anda.")
        ttk.Label(left, textvariable=self.offer, wraplength=460, justify="left").pack(anchor="w", pady=10)
        self.receive_button = ttk.Button(left, text="Ambil voucher saya", style="Shop.Primary.TButton", command=self.receive_voucher)
        self.receive_button.pack(anchor="w")
        self.open_button = ttk.Button(left, text="Buka voucher", style="Shop.Primary.TButton", command=self.open_voucher, state="disabled")
        self.open_button.pack(anchor="w", pady=(8, 0))
        self.code_display = tk.StringVar(value="Kode belum dibuka")
        ttk.Label(left, textvariable=self.code_display, style="Shop.Code.TLabel", padding=12).pack(fill="x", pady=12)
        right = ttk.Frame(content, style="Shop.Card.TFrame", padding=18)
        right.grid(row=0, column=1, sticky="nsew")
        ttk.Label(right, text="Ringkasan pesanan", style="Shop.Card.TLabel", font=("Georgia", 17)).pack(anchor="w")
        ttk.Label(right, text="Subtotal                         Rp200.000", style="Shop.Card.TLabel").pack(anchor="w", pady=(18, 8))
        self.discount_text = tk.StringVar(value="Potongan voucher                  Rp0")
        ttk.Label(right, textvariable=self.discount_text, style="Shop.Card.TLabel").pack(anchor="w")
        ttk.Separator(right).pack(fill="x", pady=18)
        ttk.Label(right, text="Kode voucher", style="Shop.Card.TLabel").pack(anchor="w")
        self.code_input = tk.StringVar()
        self.code_entry = ttk.Entry(right, textvariable=self.code_input)
        self.code_entry.pack(fill="x", pady=8)
        self.apply_button = ttk.Button(right, text="Gunakan voucher", command=self.apply_voucher)
        self.apply_button.pack(fill="x")
        self.feedback = tk.StringVar(value="Ambil dan buka voucher dari toko terlebih dahulu.")
        self.feedback_label = ttk.Label(right, textvariable=self.feedback, style="Shop.Card.TLabel", wraplength=300, justify="left")
        self.feedback_label.pack(anchor="w", pady=12)
        ttk.Separator(right).pack(fill="x", pady=8)
        ttk.Label(right, text="Total belanja", style="Shop.Card.TLabel").pack(anchor="w")
        self.total = tk.StringVar(value="Rp200.000")
        ttk.Label(right, textvariable=self.total, style="Shop.Card.TLabel", font=("Georgia", 23, "bold")).pack(anchor="w", pady=8)
        self.finish_button = ttk.Button(right, text="Selesaikan pesanan simulasi", style="Shop.Primary.TButton", command=self.finish_order)
        self.finish_button.pack(fill="x", pady=8)
        footer = ttk.Frame(body)
        footer.pack(fill="x")
        ttk.Button(footer, text="Lihat proses RSA", command=self.show_details).pack(side="left")
        ttk.Button(footer, text="Identitas Kelompok", command=lambda: VoucherApp.about(self)).pack(side="left", padx=8)
        ttk.Button(footer, text="Mulai pesanan baru", command=self.new_order).pack(side="right")

    # Tombol ambil voucher membuat kiriman terenkripsi untuk pelanggan.
    def receive_voucher(self):
        if self.completed or self.delivery:
            return
        # Di simulasi ini pelanggan memiliki pasangan kunci contoh.
        self.keys = generate_keys(61, 53)
        _, self.delivery = encrypt("DISKON50", self.keys["public_key"])
        self.offer.set("Voucher dari NusaMart sudah diterima dalam bentuk terenkripsi.\nBuka voucher untuk melihat kode Anda.")
        self.receive_button.configure(state="disabled")
        self.open_button.configure(state="normal")

    # Kode baru ditampilkan setelah kiriman dibuka dengan kunci privat pelanggan.
    def open_voucher(self):
        if self.completed or not self.delivery:
            return
        _, self.recovered = decrypt(self.delivery, self.keys["private_key"])
        self.code_display.set(self.recovered)
        self.code_input.set(self.recovered)
        self.offer.set("Voucher berhasil dibuka. Gunakan kode di ringkasan pesanan\nuntuk mendapatkan potongan 50%.")
        self.feedback.set("Kode sudah diisi. Klik Gunakan voucher untuk menerapkan diskon.")
        self.open_button.configure(state="disabled")

    def apply_voucher(self):
        # Pesanan yang selesai atau sudah mendapat diskon tidak diproses lagi.
        if self.completed or self.applied:
            return
        code = self.code_input.get()
        valid, _ = check_voucher(code)
        if not valid:
            self.feedback.set("Kode voucher tidak terdaftar. Periksa kembali kode dari toko.")
            self.feedback_label.configure(foreground="#9b3a28")
            return
        # Kode harus sama dengan voucher yang sudah dibuka pada pesanan ini.
        if self.recovered is None or code != self.recovered:
            self.feedback.set("Ambil dan buka voucher Anda terlebih dahulu.")
            self.feedback_label.configure(foreground="#9b3a28")
            return
        # Tandai pemakaian voucher dan kunci input agar potongan tidak berulang.
        self.applied = True
        self.discount_text.set("Potongan voucher          -Rp100.000")
        self.total.set("Rp100.000")
        self.feedback.set("DISKON50 diterapkan. Anda hemat Rp100.000.")
        self.feedback_label.configure(foreground="#35563d")
        self.code_entry.configure(state="disabled")
        self.apply_button.configure(state="disabled")

    # Selesaikan simulasi dengan mengunci tombol; tidak ada transaksi pembayaran.
    def finish_order(self):
        if self.completed:
            return
        self.completed = True
        self.offer.set("Pesanan simulasi selesai.\nMulai pesanan baru untuk mencoba alur lagi.")
        self.feedback.set("Pesanan tercatat dalam simulasi ini.\nTotal: " + self.total.get() + "\nTidak ada pembayaran nyata.")
        for button in (self.receive_button, self.open_button, self.apply_button, self.finish_button):
            button.configure(state="disabled")
        self.code_entry.configure(state="disabled")

    # Setelah konfirmasi, kosongkan data pesanan dan kembalikan tombol ke kondisi awal.
    def new_order(self):
        if not messagebox.askyesno("Pesanan Baru", "Hapus pesanan simulasi ini dan mulai kembali?", parent=self.root):
            return
        self.keys, self.delivery, self.recovered = None, [], None
        self.applied = self.completed = False
        self.offer.set("Ada voucher diskon 50% untuk pesanan ini.\nAmbil voucher agar toko mengirimkannya kepada Anda.")
        self.code_display.set("Kode belum dibuka")
        self.code_input.set("")
        self.discount_text.set("Potongan voucher                  Rp0")
        self.total.set("Rp200.000")
        self.feedback.set("Ambil dan buka voucher dari toko terlebih dahulu.")
        self.feedback_label.configure(foreground="#27251f")
        for button in (self.receive_button, self.apply_button, self.finish_button):
            button.configure(state="normal")
        self.open_button.configure(state="disabled")
        self.code_entry.configure(state="normal")
        if self.detail_window is not None and self.detail_window.winfo_exists():
            self.detail_window.destroy()

    # Gunakan jendela detail yang masih terbuka agar tidak membuat salinan baru.
    def show_details(self):
        if self.detail_window is not None and self.detail_window.winfo_exists():
            self.detail_window.lift()
            return
        window = tk.Toplevel(self.root)
        self.detail_window = window
        window.title("Detail Pembelajaran RSA")
        details = VoucherApp(window)
        # Isi detail sesuai tahap pesanan: kiriman saja, atau sekaligus hasil dekripsi.
        if self.keys is not None:
            details.example()
            details.make_keys(notify=False)
            details.encrypt_voucher(notify=False)
            details.send_ciphertext()
            if self.recovered is not None:
                details.decrypt_voucher(notify=False)
        window.title("Detail Pembelajaran RSA | " + STORE_NAME)


# Buka halaman belanja saat file dijalankan langsung atau sebagai modul.
if __name__ == "__main__":
    root = tk.Tk()
    StoreApp(root)
    root.mainloop()
