from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulasi')
def simulasi():
    return render_template('simulasi.html')

@app.route('/tentang')
def tentang():
    return render_template('tentang.html')

@app.route('/kontak')
def kontak():
    return render_template('kontak.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ambil input dari form
        jenis = request.form['jenis']
        penjualan_raw = request.form['penjualan'].replace('.', '').replace(',', '')
        pembelian_raw = request.form.get('pembelian', '').replace('.', '').replace(',', '')
        biaya_raw = request.form['biaya'].replace('.', '').replace(',', '')

        penjualan = float(penjualan_raw) if penjualan_raw else 0.0
        pembelian = float(pembelian_raw) if pembelian_raw else 0.0
        biaya = float(biaya_raw) if biaya_raw else 0.0

        # Perhitungan laba
        laba_kotor = penjualan - pembelian
        laba_bersih = laba_kotor - biaya
        persen = 0.0 if penjualan == 0 else (laba_bersih / penjualan) * 100.0
        kondisi = "UNTUNG" if laba_bersih > 0 else "RUGI"
        warna = "#00B050" if laba_bersih > 0 else "#FF0000"

        # Langkah perhitungan
        langkah = [
            f"1) Pendapatan (Total penjualan): Rp {penjualan:,.0f}.",
            f"2) Laba Kotor = Pendapatan - Pembelian.",
            f"   Rumus: Laba Kotor = {penjualan:,.0f} - {pembelian:,.0f} = Rp {laba_kotor:,.0f}.",
            f"3) Laba Bersih = Laba Kotor - Biaya Operasional.",
            f"   Rumus: Laba Bersih = {laba_kotor:,.0f} - {biaya:,.0f} = Rp {laba_bersih:,.0f}.",
            f"4) Persentase = (Laba Bersih ÷ Pendapatan) × 100% = {persen:.2f}%. Kondisi: {kondisi}."
        ]

        # Analisis berdasarkan jenis perusahaan
        jenis_lower = jenis.lower()
        if jenis_lower == "dagang":
            analisis = (
                "Perusahaan dagang berfokus pada pembelian dan penjualan barang. "
                "Manajemen stok, harga jual, dan efisiensi operasional sangat berpengaruh terhadap laba akhir."
            )
        elif jenis_lower == "jasa":
            analisis = (
                "Perusahaan jasa menekankan efisiensi pelayanan dan kepuasan pelanggan "
                "sebagai kunci menjaga pendapatan yang stabil."
            )
        elif jenis_lower == "manufaktur":
            analisis = (
                "Perusahaan manufaktur menghasilkan produk melalui proses produksi. "
                "Efisiensi bahan baku, biaya produksi, dan kontrol mutu sangat penting untuk menjaga keuntungan."
            )
        elif jenis_lower == "konstruksi":
            analisis = (
                "Perusahaan konstruksi mengandalkan manajemen proyek yang baik. "
                "Ketepatan waktu, pengendalian biaya, dan kualitas hasil pekerjaan menentukan profitabilitas."
            )
        else:
            analisis = "Jenis perusahaan belum dikenali. Harap pilih kategori yang sesuai."

        # Tips sederhana
        tips = (
            "🎉 Selamat! Usaha Anda dalam kondisi menguntungkan. Pertahankan strategi dan pertimbangkan ekspansi."
            if kondisi == "UNTUNG"
            else "⚠️ Usaha sedang rugi. Periksa struktur biaya dan upayakan efisiensi."
        )

        # Grafik keuangan
        fig, ax = plt.subplots(figsize=(7, 4))
        kategori = ['Pendapatan', 'Pembelian', 'Biaya', 'Laba Bersih']
        nilai = [penjualan, pembelian, biaya, laba_bersih]
        warna_grafik = ['#007bff', '#ffc107', '#dc3545', '#28a745']
        ax.bar(kategori, nilai, color=warna_grafik)
        ax.set_title('Visualisasi Keuangan')
        ax.set_ylabel('Nilai (Rp)')
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)

        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        return render_template(
            'result.html',
            jenis=jenis.capitalize(),
            kondisi=f"{kondisi} sebesar {abs(persen):.2f}%",
            analisis=analisis,
            tips=tips,
            warna=warna,
            langkah=langkah,
            plot_url=plot_url,
            penjualan=penjualan,
            pembelian=pembelian,
            biaya=biaya,
            laba_bersih=laba_bersih,
            persen=persen,
            waktu=waktu
        )

    except Exception as e:
        return f"<h3 style='color:red'>Terjadi kesalahan: {str(e)}</h3><br><a href='/simulasi'>Kembali</a>"


# === BAGIAN PENTING UNTUK RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
