# Operasi

## Menjaga server tetap hidup

`tps-public start --public` dan `tps-public start --lan` membuat sesi tmux `tps-server`. `tps-admin start` membuat sesi terpisah `tps-admin`.

```bash
tps-public start --public
tps-public status
tps-public logs
```

Untuk menghentikan hanya server publik:

```bash
tps-public stop
```

Agar Android tidak membunuh proses, buka pengaturan Termux → Battery/Baterai → Unrestricted/Tidak dibatasi. Jangan gunakan Force stop. Jika tersedia, jalankan `termux-wake-lock` untuk operasi lama.

## Menjalankan tools admin

```bash
tps-admin start
```

Buka browser pada perangkat yang sama dan kunjungi `http://127.0.0.1:8090`. Halaman admin ini hanya listen di localhost. Gunakan halaman tersebut untuk melihat key, membuat key baru, atau mengatur masa aktif key.

Perintah terminal yang tersedia:

```bash
tps-admin status
tps-admin key show
tps-admin key info
tps-admin key generate 24h
tps-admin key set-expiry 7d
tps-admin stop
```

`tps-admin stop` hanya menghentikan admin; server publik tetap berjalan.

## Jika URL tidak muncul

1. Jalankan `tps-public logs`.
2. Pastikan `curl` dan `python` bisa dipanggil.
3. Pastikan koneksi internet aktif.
4. Jalankan `tps-public stop` lalu `tps-public start --public`.

## Jika port 8080 dipakai

```bash
export TPS_PORT=9090
export TPS_APP_COMMAND='python -m http.server 9090 --bind 0.0.0.0 --directory "$HOME/.termux-public-server/www"'
tps-public start --public
```

Quick Tunnel harus mengarah ke port yang sama dengan aplikasi.
