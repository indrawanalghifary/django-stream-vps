import subprocess
import os
import logging
import shlex
from django.conf import settings

# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/django_services.log'),
        logging.StreamHandler()  # Juga mencetak ke konsol
    ]
)

logger = logging.getLogger(__name__)

def run_ffmpeg_nohup(ffmpeg_command, output_log=None):
    """
    Menjalankan ffmpeg dengan subprocess nohup

    Args:
        ffmpeg_command (str): Perintah ffmpeg yang ingin dijalankan
        output_log (str): Path file untuk menyimpan output log (optional)

    Returns:
        int: Process ID dari ffmpeg yang sedang berjalan
    """
    try:
        logger.info(f"Menjalankan perintah ffmpeg: {ffmpeg_command}")

        if output_log is None:
            output_log = "/dev/null"

        # Gunakan pendekatan dengan temporary file untuk menyimpan PID
        import tempfile
        import os
        import time

        # Buat file sementara untuk menyimpan PID
        pid_file = tempfile.mktemp()

        # Buat perintah untuk menjalankan ffmpeg di background dan menyimpan PID
        full_command = f"({ffmpeg_command}) > {output_log} 2>&1 & echo $! > {pid_file}"

        # Eksekusi perintah
        os.system(full_command)

        # Tunggu sebentar agar proses bisa mulai
        time.sleep(0.5)

        # Baca PID dari file
        try:
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid_content = f.read().strip()

                # Hapus file sementara
                os.remove(pid_file)

                if pid_content.isdigit():
                    ffmpeg_pid = int(pid_content)
                    logger.info(f"Proses ffmpeg dimulai dengan PID: {ffmpeg_pid}")
                    return ffmpeg_pid
                else:
                    logger.error(f"Tidak bisa membaca PID dari file, isi: {pid_content}")
                    return None
            else:
                logger.error("File PID tidak ditemukan setelah eksekusi perintah")
                return None
        except Exception as e:
            logger.error(f"Error membaca file PID: {str(e)}")
            if os.path.exists(pid_file):
                os.remove(pid_file)
            return None

    except Exception as e:
        logger.error(f"Error running ffmpeg: {str(e)}")
        return None


# Contoh penggunaan:
# run_ffmpeg_nohup("ffmpeg -i input.mp4 output.mp3", "/tmp/ffmpeg.log")

def stop_process(pid):
    """
    Menghentikan proses berdasarkan PID

    Args:
        pid (int): Process ID yang ingin dihentikan

    Returns:
        bool: True jika proses berhasil dihentikan, False jika gagal
    """
    try:
        logger.info(f"Menghentikan proses dengan PID: {pid}")
        os.kill(pid, 9)  # Mengirim sinyal SIGKILL
        logger.info(f"Proses {pid} berhasil dihentikan")
        return True
    except OSError as e:
        logger.error(f"Error stopping process {pid}: {str(e)}")
        return False


def is_process_running(pid):
    """
    Memeriksa apakah proses dengan PID tertentu sedang berjalan

    Args:
        pid (int): Process ID yang ingin diperiksa

    Returns:
        bool: True jika proses sedang berjalan, False jika tidak
    """
    try:
        os.kill(pid, 0)  # Mengirim sinyal 0 untuk memeriksa keberadaan proses
        logger.debug(f"Proses {pid} sedang berjalan")
        return True
    except OSError:
        logger.debug(f"Proses {pid} tidak berjalan")
        return False


def start_live_stream(input_source, output_rtmp, ffmpeg_params):
    """
    Memulai streaming langsung menggunakan ffmpeg

    Args:
        input_source (str): Sumber input (file atau URL)
        output_rtmp (str): URL RTMP tujuan
        ffmpeg_params (str): Parameter tambahan untuk ffmpeg

    Returns:
        int: Process ID dari ffmpeg yang sedang berjalan
    """
    logger.info(f"Memulai live stream: input={input_source}, output={output_rtmp}, params={ffmpeg_params}")

    # Deteksi apakah input adalah file media atau URL
    is_media_file = not input_source.startswith(('http://', 'https://', 'rtmp://', 'rtsp://'))

    if is_media_file:
        logger.info("Input terdeteksi sebagai file media lokal")

        # Normalisasi path input - hapus leading slash dan prefix media/ jika ada
        normalized_path = input_source.strip('/')
        if normalized_path.startswith('media/'):
            normalized_path = normalized_path[6:]  # Hilangkan 'media/'

        file_path = os.path.join(settings.MEDIA_ROOT, normalized_path)
        logger.debug(f"Path file media: {file_path}")

        # Verifikasi bahwa file benar-benar ada
        if not os.path.exists(file_path):
            logger.error(f"File tidak ditemukan: {file_path}")
            return None

        # Gunakan shlex.quote hanya untuk input file, bukan untuk output URL
        quoted_input = shlex.quote(file_path)

        # Tangani kasus di mana ffmpeg_params mungkin kosong
        if ffmpeg_params.strip():
            # Gabungkan parameter ffmpeg dengan output RTMP
            # Gunakan format FLV untuk streaming RTMP
            ffmpeg_command = f"ffmpeg -re -stream_loop -1 -i {quoted_input} {ffmpeg_params} -f flv \"{output_rtmp}\""
        else:
            # Jika tidak ada parameter tambahan, gunakan parameter standar untuk RTMP
            ffmpeg_command = f"ffmpeg -re -stream_loop -1 -i {quoted_input} -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -f flv \"{output_rtmp}\""
    else:
        logger.info("Input terdeteksi sebagai URL/streaming")
        # Untuk URL, kita sesuaikan parameter
        # Gunakan shlex.quote hanya untuk input, bukan untuk output URL
        quoted_input = shlex.quote(input_source)

        # Tangani kasus di mana ffmpeg_params mungkin kosong
        if ffmpeg_params.strip():
            # Gabungkan parameter ffmpeg dengan output RTMP
            # Gunakan format FLV untuk streaming RTMP
            ffmpeg_command = f"ffmpeg -i {quoted_input} {ffmpeg_params} -f flv \"{output_rtmp}\""
        else:
            # Jika tidak ada parameter tambahan, gunakan parameter standar untuk RTMP
            ffmpeg_command = f"ffmpeg -i {quoted_input} -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -f flv \"{output_rtmp}\""

    logger.debug(f"Perintah ffmpeg lengkap: {ffmpeg_command}")

    pid = run_ffmpeg_nohup(ffmpeg_command, output_log="/tmp/ffmpeg_live.log")

    if pid:
        logger.info(f"Live stream dimulai dengan PID: {pid}")
    else:
        logger.error("Gagal memulai live stream")

    return pid


# if __name__ == '__main__':

#     start_live_stream("/media/indrawan/MULTIMEDIA/KODING/belajar-django/belajar1/test.mp4", "rtmp://demo.flashphoner.com:1935/live/live_stream", "-c:v libx264 -b:v 3000k -c:a aac -b:a 160k")
