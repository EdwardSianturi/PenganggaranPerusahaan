from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# ----------------------------
# ROUTE: Halaman Utama
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------------------
# ROUTE: Halaman Tentang
# ----------------------------
@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

# ----------------------------
# ROUTE: Halaman Kontak
# ----------------------------
@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

# ----------------------------
# ROUTE: Hasil Perhitungan
# ----------------------------
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ambil input pengguna
        jenis = request.form['jenis']
        penjualan = request.form['penjualan'].replace('.', '').replace(',', '')
        pembelian = request.form['pembelian'].replace('.', '').replace(',', '')
        biaya = request.form['biaya'].replace('.', '').replace(',', '')

        # Ubah ke float
        penjualan = float(penjualan) if penjualan else 0
        pembelian = float(pembelian) if pembelian else 0
        biaya = float(biaya) if biaya else 0

        # Hitung hasil utama
        laba_kotor = penjualan - pembelian
        laba_bersih = laba_kotor - biaya
        persen = 0 if penjualan == 0 else (laba_bersih / penjualan) * 100
        kondisi = "UNTUNG" if laba_bersih > 0 else "RUGI"
        warna = "#00B050" if laba_bersih > 0 else "#FF0000"

        # ----------------------------
        # ANALISIS & SARAN OTOMATIS
        # ----------------------------
        saran = ""
        if jenis.lower() == "dagang":
            if laba_bersih > 0:
                analisis = (
                    "Perusahaan dagang Anda menunjukkan performa positif. "
                    "Keuntungan diperoleh dari margin antara pembelian dan penjualan barang."
                )
                saran = (
                    "Pertahankan kontrol stok dan evaluasi harga jual secara berkala. "
                    "Gunakan sebagian laba untuk meningkatkan promosi atau menambah variasi produk."
                )
            else:
                analisis = (
                    "Perusahaan dagang Anda mengalami kerugian. "
                    "Hal ini dapat disebabkan oleh biaya pembelian yang tinggi atau penurunan penjualan."
                )
                saran = (
                    "Kurangi biaya pembelian dengan mencari pemasok yang lebih murah, "
                    "lakukan promosi agresif, serta kurangi biaya operasional yang tidak mendesak."
                )
        else:
            if laba_bersih > 0:
                analisis = (
                    "Perusahaan jasa Anda dalam kondisi menguntungkan. "
                    "Efisiensi layanan dan kepuasan pelanggan tampak berjalan baik."
                )
                saran = (
                    "Pertahankan efisiensi tim, kembangkan paket layanan premium, "
                    "dan berinvestasi dalam peningkatan kualitas layanan."
                )
            else:
                analisis = (
                    "Perusahaan jasa Anda mengalami kerugian. "
                    "Kemungkinan biaya tenaga kerja atau operasional terlalu tinggi."
                )
                saran = (
                    "Evaluasi beban tenaga kerja, kurangi waktu idle, "
                    "dan fokus pada peningkatan produktivitas tim serta pemasaran digital."
                )

        # ----------------------------
        # TITIK IMPAS (Break-Even)
        # ----------------------------
        if pembelian + biaya > 0:
            titik_impas = pembelian + biaya
            rekomendasi = f"Untuk mencapai titik impas, pendapatan minimal yang dibutuhkan adalah Rp {titik_impas:,.0f}."
        else:
            titik_impas = 0
            rekomendasi = "Data terlalu kecil untuk menghitung titik impas."

        # ----------------------------
        # TABEL HASIL
        # ----------------------------
        tabel = f"""
        <table border='1' cellpadding='8'>
        <tr><th>Keterangan</th><th>Nilai (Rp)</th></tr>
        <tr><td>Jenis Perusahaan</td><td>{jenis.capitalize()}</td></tr>
        <tr><td>Pendapatan Kotor</td><td>{penjualan:,.0f}</td></tr>
        <tr><td>Pembelian</td><td>{pembelian:,.0f}</td></tr>
        <tr><td>Biaya Operasional</td><td>{biaya:,.0f}</td></tr>
        <tr><td>Laba Kotor</td><td>{laba_kotor:,.0f}</td></tr>
        <tr><td>Laba Bersih</td><td>{laba_bersih:,.0f}</td></tr>
        <tr><td>Persentase {kondisi}</td><td>{persen:.2f}%</td></tr>
        </table>
        """

        # ----------------------------
        # DETAIL LANGKAH
        # ----------------------------
        detail = [
            f"Pendapatan Kotor = Rp {penjualan:,.0f}",
            f"Laba Kotor = {penjualan:,.0f} - {pembelian:,.0f} = Rp {laba_kotor:,.0f}",
            f"Laba Bersih = {laba_kotor:,.0f} - {biaya:,.0f} = Rp {laba_bersih:,.0f}",
            f"Persentase {kondisi} = ({laba_bersih:,.0f} / {penjualan:,.0f}) × 100 = {persen:.2f}%",
            rekomendasi
        ]

        # ----------------------------
        # GRAFIK VISUALISASI
        # ----------------------------
        fig, ax = plt.subplots(figsize=(6, 4))
        kategori = ['Pendapatan', 'Pembelian', 'Biaya Operasional', 'Laba Bersih']
        nilai = [penjualan, pembelian, biaya, laba_bersih]
        warna_grafik = ['#007bff', '#ffc107', '#dc3545', '#28a745']
        ax.bar(kategori, nilai, color=warna_grafik)
        ax.set_title('Visualisasi Keuangan')
        ax.set_ylabel('Nilai (Rp)')
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # ----------------------------
        # WAKTU CETAK
        # ----------------------------
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Render ke halaman hasil
        return render_template(
            'result.html',
            jenis=jenis.capitalize(),
            kondisi=f"{kondisi} sebesar {abs(persen):.2f}%",
            analisis=analisis,
            warna=warna,
            tables=tabel,
            detail=detail,
            waktu=waktu,
            plot_url=plot_url,
            saran=saran
        )

    except Exception as e:
        return f"<h3 style='color:red'>Terjadi kesalahan: {str(e)}</h3><br><a href='/'>Kembali</a>"


if __name__ == '__main__':
    app.run(debug=True)
