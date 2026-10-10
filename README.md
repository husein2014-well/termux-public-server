# Termux Public Server

Jalankan server HTTP dari perangkat Android melalui Termux dan bagikan ke internet dengan URL publik sementara.

> **Penting:** ini bukan VPS cloud. Server berjalan di ponsel pengguna, sehingga ponsel harus tetap menyala, Termux tidak dihentikan Android, dan koneksi internet tetap aktif. URL Quick Tunnel dapat berubah ketika server dimulai ulang.

## Fitur

- Instalasi satu perintah dari GitHub.
- Server HTTP contoh berbasis Python.
- Akses publik melalui Cloudflare Quick Tunnel tanpa port-forwarding.
- Mode LAN untuk akses perangkat dalam Wi-Fi yang sama.
- Proteksi access key sebelum pengunjung melihat website.
- Halaman admin lokal untuk membuat/merotasi key tanpa mengeksposnya ke internet.
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

## Mulai server publik di background

```bash
tps start --public
```

Server sekarang berjalan di **background dalam tmux**, sehingga jendela/aplikasi Termux dapat ditutup tanpa langsung menghentikan server. URL publik dapat dilihat dengan:

```bash
tps status
tps logs
```

Server akan meminta **access key** sebelum menampilkan halaman. Lihat key aktif dengan:

```bash
tps key show
```

Atau buka halaman pembuat key di perangkat yang menjalankan Termux:

```bash
tps admin
```

Lalu buka `http://127.0.0.1:8090` pada browser Android. Tekan **Buat key baru** untuk merotasi key. Halaman admin hanya listen di `127.0.0.1`, sehingga tidak ikut terbuka lewat URL publik.

Bagikan URL `https://....trycloudflare.com` kepada orang lain. Hentikan dengan:

```bash
tps stop
```

Jika ingin melihat proses secara langsung di terminal, gunakan:

```bash
tps start --public --foreground
```

## Mode LAN

Untuk akses dari perangkat yang berada pada Wi-Fi yang sama:

```bash
tps start --lan
```

Buka alamat LAN yang ditampilkan, misalnya `http://192.168.1.20:8080`.

## Perintah

```text
 tps start --public   Jalankan server + tunnel di background
 tps start --lan      Jalankan server LAN di background
 tps start --public --foreground  Jalankan menempel di terminal
 tps admin            Buka halaman admin key lokal di port 8090
 tps key show         Tampilkan key aktif di terminal
 tps key generate     Buat key baru dan batalkan key lama
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
- Access key disimpan lokal pada `~/.termux-public-server/run/access.key` dengan permission terbatas. Jangan kirim key ke orang yang tidak dipercaya.
- Cookie login berlaku sekitar 24 jam. Setelah merotasi key, sesi lama tidak berlaku lagi.
- Jangan menjalankan perintah dari pengunjung dan jangan membagikan token, cookie, file pribadi, atau direktori home.
- Android dapat menghentikan proses di latar belakang. Jalankan `termux-wake-lock` bila perlu dan matikan optimasi baterai untuk Termux.
- Setelah instalasi, buka **Settings Android → Apps → Termux → Battery → Unrestricted** (nama menu dapat berbeda menurut merek ponsel). Jangan force-stop Termux; gunakan `tps stop` agar proses ditutup dengan benar.
- Mode background memakai `tmux`, dan installer sudah memasang `tmux`. Menutup jendela Termux berbeda dengan menekan **Force stop** pada pengaturan Android.
- Penggunaan data, panas, dan baterai menjadi tanggung jawab pengguna.
- Cloudflare Quick Tunnel memakai layanan pihak ketiga; baca syarat layanan mereka sebelum penggunaan produksi.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
