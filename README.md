# Termux Public Server

Jalankan server HTTP dari perangkat Android melalui Termux dan bagikan ke internet dengan URL publik sementara.

> **Penting:** ini bukan VPS cloud. Server berjalan di ponsel pengguna, sehingga ponsel harus tetap menyala, Termux tidak dihentikan Android, dan koneksi internet tetap aktif. URL Quick Tunnel dapat berubah ketika server dimulai ulang.

## Fitur

- Instalasi satu perintah dari GitHub.
- Server HTTP contoh berbasis Python.
- Akses publik melalui Cloudflare Quick Tunnel tanpa port-forwarding.
- Mode LAN untuk akses perangkat dalam Wi-Fi yang sama.
- Perintah `start`, `stop`, `status`, `logs`, `update`, dan `uninstall`.
- Tidak membuka SSH, tidak memasang akses root, dan tidak menyimpan kredensial.

## Instalasi

Pasang **Termux dari F-Droid atau GitHub resmi Termux**, bukan sumber APK acak. Lalu jalankan:

```bash
pkg update -y && pkg install -y git
curl -fsSL https://raw.githubusercontent.com/husein2014-well/termux-public-server/main/install.sh | bash
source "$HOME/.termux-public-server/env"
```

Jika repository dipindahkan, ganti URL raw di atas sesuai pemilik/repository baru.

## Mulai server publik

```bash
tps start --public
```

Terminal akan menampilkan URL `https://....trycloudflare.com`. Bagikan URL itu kepada orang lain. Hentikan dengan `Ctrl+C`, atau dari sesi lain:

```bash
tps stop
```

## Mode LAN

Untuk akses dari perangkat yang berada pada Wi-Fi yang sama:

```bash
tps start --lan
```

Buka alamat LAN yang ditampilkan, misalnya `http://192.168.1.20:8080`.

## Perintah

```text
tps start --public   Jalankan server + Cloudflare Quick Tunnel
tps start --lan      Jalankan server hanya di jaringan lokal
tps stop             Hentikan server dan tunnel
tps status           Tampilkan status proses dan alamat terakhir
tps logs             Tampilkan log terakhir
tps update           Ambil pembaruan dari GitHub
tps uninstall        Hapus instalasi kit (data server dapat dipertahankan)
```

## Menyajikan file sendiri

Salin file website ke folder:

```bash
cp -r website/* "$HOME/.termux-public-server/www/"
tps start --public
```

Contoh file ada di `server/www/index.html`.

## Menjalankan aplikasi lain

Kit ini default-nya menyajikan folder statis pada port `8080`. Untuk aplikasi sendiri, jalankan aplikasi pada `0.0.0.0:8080`, lalu gunakan tunnel:

```bash
export TPS_APP_COMMAND='python server.py --host 0.0.0.0 --port 8080'
tps start --public
```

Perintah aplikasi harus dipercaya dan dipahami pengguna. Jangan mengekspos panel admin, database, SSH, atau endpoint yang berisi rahasia.

## Keterbatasan dan keamanan

- Quick Tunnel cocok untuk demo, webhook pengembangan, dan berbagi sementara; bukan SLA produksi.
- URL publik berarti siapa pun yang memiliki URL dapat mengakses layanan. Tambahkan autentikasi di aplikasi bila data sensitif.
- Jangan menjalankan perintah dari pengunjung dan jangan membagikan token, cookie, file pribadi, atau direktori home.
- Android dapat menghentikan proses di latar belakang. Jalankan `termux-wake-lock` bila perlu dan matikan optimasi baterai untuk Termux.
- Penggunaan data, panas, dan baterai menjadi tanggung jawab pengguna.
- Cloudflare Quick Tunnel memakai layanan pihak ketiga; baca syarat layanan mereka sebelum penggunaan produksi.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
