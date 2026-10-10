# Operasi

## Menjaga proses tetap hidup

Di Termux, jalankan `termux-wake-lock` (paket `termux-api` opsional) dan nonaktifkan battery optimization untuk Termux di pengaturan Android. Jangan menghapus notifikasi Termux bila Android masih menghentikan proses.

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
