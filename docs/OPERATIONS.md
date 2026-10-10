# Operasi

## Menjaga server tetap hidup

` tps-public start --public` dan `tps-public start --lan` membuat sesi tmux `tps-server`. `tps-admin start` membuat sesi terpisah `tps-admin`.

```bash
tps-public start --public
tps-public status
tps-public logs
```

Untuk menghentikan hanya server publik:

```bash
tps-public stop
```

Untuk menghentikan hanya admin:

```bash
tps-admin stop
```

Agar Android tidak membunuh proses, buka pengaturan Termux → Battery/Baterai → Unrestricted/Tidak dibatasi. Jangan gunakan Force stop. Jika tersedia, jalankan `termux-wake-lock` untuk operasi lama.

## Access key dari website admin

Jalankan tools admin:

```bash
tps-admin start
```

Buka `http://127.0.0.1:8090` pada browser Android. Pilih masa aktif key (1 jam, 24 jam, 7 hari, 30 hari, atau tanpa kedaluwarsa), lalu klik **Simpan masa aktif** atau **Buat key baru**. Admin hanya listen di localhost.

Alternatif dari terminal:

```bash
tps-admin key show
tps-admin key info
tps-admin key generate
tps-admin key generate 24h
tps-admin key set-expiry 7d
tps-admin key set-expiry never
```

Durasi yang didukung adalah `1h`, `24h`, `7d`, `30d`, dan `never` (CLI juga menerima durasi menit/jam/hari sampai 365 hari). Rotasi key membatalkan key lama dan sesi login lama. `set-expiry` hanya mengubah masa aktif key yang sedang dipakai.

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
