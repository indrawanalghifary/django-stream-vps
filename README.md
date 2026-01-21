# Deployment Aplikasi Django dengan Docker

Dokumentasi ini menjelaskan langkah-langkah untuk menjalankan aplikasi Django ini di VPS hingga production.

## Prasyarat

Sebelum memulai, pastikan VPS Anda memiliki:

- Sistem operasi Linux (disarankan Ubuntu 20.04 LTS atau lebih baru)
- Hak akses root atau sudo
- Port 22 (SSH), 80 (HTTP), dan 443 (HTTPS) terbuka

## Instalasi Dependencies

### 1. Update sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instal Docker
```bash
# Install Docker dari repositori resmi
sudo apt install ca-certificates curl gnupg lsb-release -y

# Tambahkan GPG key Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update paket dan instal Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 3. Atur Docker agar berjalan otomatis
```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

## Deployment Aplikasi

### 1. Clone repository
```bash
git clone <URL_REPOSITORY_ANDA>
cd <NAMA_REPOSITORY>
```

### 2. Siapkan file konfigurasi lingkungan
```bash
# Salin contoh file .env
cp .env.example .env
```

### 3. Edit file .env sesuai kebutuhan Anda
```bash
nano .env
```

Pastikan untuk mengganti nilai-nilai berikut:
- `SECRET_KEY`: Generate secret key baru untuk production (gunakan situs seperti https://djecrety.ir/)
- `POSTGRES_PASSWORD`: Password database yang kuat
- `DEBUG`: Set ke `False` untuk production
- `ALLOWED_HOSTS`: Daftar domain/IP yang diizinkan mengakses aplikasi

Contoh konfigurasi .env untuk production:
```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,ip-address
POSTGRES_DB=django_prod_db
POSTGRES_USER=django_prod_user
POSTGRES_PASSWORD=your-very-secure-password
REDIS_HOST=redis
REDIS_PORT=6379
NGINX_PORT=80
DB_HOST=db
DB_PORT=5432
```

### 4. Jalankan aplikasi dengan Docker Compose
```bash
# Build dan jalankan aplikasi dalam mode production
docker-compose -f production.yml up -d --build
```

### 5. Lakukan migrasi database
```bash
# Masuk ke container web
docker-compose -f production.yml exec web bash

# Jalankan migrasi database
python manage.py migrate

# Keluar dari container
exit
```

### 6. (Opsional) Buat superuser admin
```bash
# Masuk ke container web
docker-compose -f production.yml exec web bash

# Buat superuser admin
python manage.py createsuperuser

# Keluar dari container
exit
```

## Konfigurasi SSL (HTTPS)

Untuk mengamankan koneksi, Anda perlu mengkonfigurasi SSL. Berikut adalah langkah-langkah menggunakan Certbot dan Let's Encrypt:

### 1. Instal Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Dapatkan sertifikat SSL
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Ikuti instruksi yang muncul di layar untuk menyelesaikan proses.

### 3. Perbarui konfigurasi nginx.conf untuk menangani HTTPS
Anda perlu memperbarui file nginx.conf untuk menangani redirect HTTP ke HTTPS dan konfigurasi SSL. Berikut adalah contoh konfigurasi lengkap:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django_app {
        server web:8000;
    }

    # Redirect semua permintaan HTTP ke HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # Server HTTPS
    server {
        listen 443 ssl;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        
        # Konfigurasi SSL yang aman
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 1d;
            add_header Cache-Control "public";
        }

        location / {
            proxy_pass http://django_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout dan buffering
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            proxy_buffering on;
        }
    }
}
```

Setelah memperbarui nginx.conf, restart layanan:
```bash
docker-compose -f production.yml restart nginx
```

## Manajemen Aplikasi

### Melihat log aplikasi
```bash
# Lihat log semua layanan
docker-compose -f production.yml logs

# Lihat log layanan tertentu (misalnya web)
docker-compose -f production.yml logs web
```

### Restart aplikasi
```bash
docker-compose -f production.yml restart
```

### Update aplikasi
```bash
# Pull kode terbaru dari repository
git pull origin main

# Rebuild dan restart aplikasi
docker-compose -f production.yml up -d --build
```

### Backup database
```bash
# Masuk ke container database
docker-compose -f production.yml exec db bash

# Backup database
pg_dump -U django_prod_user django_prod_db > backup.sql

# Keluar dari container
exit

# Salin file backup ke host
docker-compose -f production.yml cp db:/backup.sql ./backup.sql
```

## Monitoring dan Troubleshooting

### Cek status layanan
```bash
docker-compose -f production.yml ps
```

### Cek resource usage
```bash
docker stats
```

### Masuk ke container untuk troubleshooting
```bash
# Masuk ke container web
docker-compose -f production.yml exec web bash

# Masuk ke container database
docker-compose -f production.yml exec db bash

# Masuk ke container nginx
docker-compose -f production.yml exec nginx bash
```

## Penjadwalan Renewal SSL Otomatis

Certbot akan membuat cron job otomatis, tetapi Anda bisa memverifikasi dengan:
```bash
sudo crontab -l -u root
```

Atau tambahkan manual ke crontab:
```bash
sudo crontab -e -u root
```

Tambahkan baris berikut untuk pengecekan renewal dua kali sehari:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Penutup

Aplikasi sekarang harus dapat diakses melalui domain yang telah dikonfigurasi. Pastikan untuk:

1. Menyimpan file .env dengan aman
2. Melakukan backup rutin database
3. Memantau log aplikasi secara berkala
4. Memperbarui sistem dan dependensi secara berkala
5. Mengikuti praktik keamanan terbaik untuk production

Jika Anda mengalami masalah, periksa log aplikasi dan pastikan semua port yang diperlukan terbuka di firewall VPS Anda.