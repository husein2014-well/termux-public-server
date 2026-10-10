# Operasi

## Menjaga proses tetap hidup setelah Termux ditutup

`tps start --public` dan `tps start --lan` otomatis membuat sesi **tmux** bernama `tps-server`, jadi terminal dapat ditutup tanpa menghentikan server.

```bash
tps start --public
tps status
tps logs
```

## Access key dari website admin

Website publik selalu meminta access key. Untuk melihat key aktif dari terminal:

```bash
tps key show
```

Untuk membuat key dari website:

```bash
tps admin
```

Buka `http://127.0.0.1:8090` pada browser Android. Klik **Buat key baru**, lalu gunakan key yang ditampilkan pada halaman login website publik. Admin hanya listen di localhost dan tidak diteruskan oleh Cloudflare Tunnel.

Alternatif rotasi dari terminal:

```bash
tps key generate
```

Rotasi key akan membatalkan key lama dan sesi login lama.

Untuk menghentikan server dan tunnel:

```bash
tps stop
```

Agar Android tidak membunuh proses:

1. Buka pengaturan aplikasi **Termux**.
2. Pilih **Battery/Baterai**.
3. Pilih **Unrestricted/Tidak dibatasi** atau matikan optimasi baterai.
4. Jangan gunakan **Force stop**. Gunakan `tps stop`.
5. Jika tersedia, jalankan `termux-wake-lock` ketika membutuhkan server aktif lama.

Catatan: Android tetap dapat menghentikan proses karena mode hemat daya, RAM penuh, reboot, atau force-stop. Untuk otomatis hidup setelah reboot, gunakan aplikasi **Termux:Boot** dan buat skrip startup terpisah; fitur itu tidak dipasang otomatis oleh kit ini.

## Jika URL tidak muncul

1. Jalankan `tps logs`.
2. Pastikan `curl` dan `python` bisa dipanggil.
3. Pastikan koneksi internet aktif.
4. Jalankan ulang `tps stop` lalu `tps start --public`.

## Jika port 8080 dipakai

```bash
export TPS_PORT=9090
export TPS_APP_COMMAND='python -m http.server 9090 --bind 0.0.0.0 --directory "$HOME/.termux-public-server/www"'
tps start --public
```

Quick Tunnel harus mengarah ke port yang sama dengan aplikasi.
