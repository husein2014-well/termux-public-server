# Termux Public Server

Jalankan server HTTP dari perangkat Android melalui Termux dan bagikan ke internet melalui URL publik sementara.

> **Penting:** ini bukan VPS cloud. Server berjalan di ponsel pengguna, sehingga ponsel harus menyala, Termux tidak di-force-stop, dan koneksi internet tetap aktif.

## Fitur

- Instalasi satu perintah dari GitHub.
- Server HTTP contoh berbasis Python.
- Akses publik melalui Cloudflare Quick Tunnel tanpa port-forwarding.
- Mode LAN untuk jaringan Wi-Fi yang sama.
- Proteksi access key sebelum pengunjung melihat website.
- **Tools dipisah:** `tps-public` untuk layanan publik dan `tps-admin` untuk admin/key.
- Server berjalan di tmux sehingga terminal Termux dapat ditutup.

## Instalasi

Pasang Termux dari F-Droid atau GitHub resmi Termux, lalu jalankan:

```bash
pkg update -y && pkg install -y git
curl -fsSL https://raw.githubusercontent.com/husein2014-well/termux-public-server/main/install.sh | bash
source "$HOME/.termux-public-server/env"
```

## Tools public

Jalankan server publik di background:

```bash
tps-public start --public
```

Cek URL dan status:

```bash
tps-public status
tps-public logs
```

Hentikan hanya server/tunnel publik:

```bash
tps-public stop
```

Untuk mode LAN:

```bash
tps-public start --lan
```

Untuk menjalankan menempel di terminal:

```bash
tps-public start --public --foreground
```

## Tools admin

Jalankan halaman admin lokal:

```bash
tps-admin start
```

Buka alamat ini pada browser Android:

```text
http://127.0.0.1:8090
```

Halaman admin hanya listen di localhost dan tidak diteruskan ke tunnel publik. Gunakan halaman tersebut untuk membuat/merotasi access key dan memilih masa aktif **1 jam, 24 jam, 7 hari, 30 hari, atau tanpa kedaluwarsa**.

Perintah admin lainnya:

```bash
tps-admin status
tps-admin key show
tps-admin key info
tps-admin key generate
tps-admin key generate 24h
tps-admin key set-expiry 7d
tps-admin key set-expiry never
tps-admin stop
```

Setiap kali key dirotasi, key lama dan sesi login lama tidak berlaku lagi. `set-expiry` mengubah masa aktif key saat ini tanpa mengganti key.

## Perintah lengkap

```text
tps-public start --public       Jalankan website + tunnel publik
tps-public start --lan          Jalankan website di LAN
tps-public stop                 Hentikan hanya layanan publik
tps-public status               Status dan URL publik
tps-public logs                 Log publik
tps-public update               Perbarui tools dari GitHub

tps-admin start                 Jalankan admin lokal
tps-admin stop                  Hentikan hanya admin
tps-admin status                Status admin
tps-admin key show              Tampilkan key aktif
tps-admin key info              Tampilkan masa aktif key
tps-admin key generate 24h      Buat key aktif 24 jam
tps-admin key set-expiry 7d     Atur key saat ini aktif 7 hari
```

Perintah `tps` lama tetap tersedia sebagai kompatibilitas, tetapi penggunaan yang disarankan adalah `tps-public` dan `tps-admin`.

## Menyajikan website sendiri

Salin file website ke folder runtime:

```bash
cp -r website/* "$HOME/.termux-public-server/www/"
tps-public start --public
```

Pengunjung tetap harus memasukkan access key sebelum melihat website.

## Keamanan dan keterbatasan

- URL publik dapat diakses siapa pun yang memilikinya; access key melindungi isi website, bukan menyembunyikan URL.
- Access key disimpan lokal di `~/.termux-public-server/run/access.key` dengan permission terbatas.
- Metadata masa aktif disimpan di `~/.termux-public-server/run/access.json`.
- Jangan membagikan key kepada orang yang tidak dipercaya.
- Cookie login berlaku sekitar 24 jam.
- Jangan mengekspos panel admin, database, SSH, file pribadi, token, atau cookie.
- Quick Tunnel cocok untuk demo dan webhook pengembangan, bukan SLA produksi.
- Atur **Settings Android → Apps → Termux → Battery → Unrestricted** agar Android tidak mematikan proses.
- Gunakan `tps-public stop` dan `tps-admin stop`, bukan Force stop Termux.
- Penggunaan data, panas, dan baterai menjadi tanggung jawab pengguna.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
