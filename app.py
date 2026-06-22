"""
Sistem Pakar Deteksi Penyakit Anak
Berbasis: Rule-Based System + Forward Chaining
Referensi: Analisis Komponen Sistem Pakar pada Sistem Deteksi Penyakit Anak
           (Rifky Yudistiansyah - 11123180)
Sumber Jurnal: https://mail.jsisfotek.org/index.php/JSisfotek/article/view/34/34

Catatan:
Kode gejala (L01-L25) dan kode penyakit (T01-T05) pada aplikasi ini dibuat
mengikuti struktur yang dijelaskan dalam jurnal (basis pengetahuan berupa
tabel keputusan yang dikonversi ke 5 rule IF-THEN). Karena detail isi setiap
rule tidak dipublikasikan lengkap di abstrak/ringkasan jurnal, daftar gejala
per penyakit pada aplikasi ini disusun berdasarkan gejala klinis umum yang
relevan dengan kelima penyakit tersebut, agar struktur rule (IF-THEN,
forward chaining) dapat didemonstrasikan secara fungsional.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# BASIS PENGETAHUAN (KNOWLEDGE BASE)
# ---------------------------------------------------------------------------

# Daftar gejala (fakta) L01 - L25
GEJALA = {
    "L01": "Buang air besar (BAB) cair lebih dari 3 kali sehari",
    "L02": "Tinja berlendir atau bercampur darah",
    "L03": "Nyeri / kram pada perut",
    "L04": "Mual dan muntah",
    "L05": "Lemas, mata cekung, bibir kering (tanda dehidrasi)",
    "L06": "Demam tinggi mendadak (lebih dari 38°C)",
    "L07": "Kejang pada seluruh tubuh",
    "L08": "Mata mendelik ke atas saat kejang",
    "L09": "Tubuh kaku kemudian diikuti kelonjotan (kejang klonik)",
    "L10": "Kehilangan kesadaran sesaat saat kejang",
    "L11": "Batuk berdahak",
    "L12": "Sesak napas",
    "L13": "Napas cepat dan pendek (takipnea)",
    "L14": "Terdengar suara napas grok-grok / ronkhi",
    "L15": "Tarikan dinding dada ke dalam saat bernapas",
    "L16": "Sesak napas yang berulang / kambuhan",
    "L17": "Mengi atau bengek saat bernapas (wheezing)",
    "L18": "Batuk terutama pada malam atau dini hari",
    "L19": "Dada terasa berat atau sempit",
    "L20": "Sesak kambuh setelah aktivitas fisik, udara dingin, atau alergen",
    "L21": "Perut tampak buncit atau kembung",
    "L22": "Gatal di sekitar area anus, terutama pada malam hari",
    "L23": "Nafsu makan menurun",
    "L24": "Berat badan sulit naik / tubuh tampak kurus",
    "L25": "Tampak pucat dan lemas (tanda anemia)",
}

# Basis aturan (Rule Base): T01-T05, format IF-THEN
# requires = gejala WAJIB (semua harus terpenuhi agar rule "fully fired")
RULES = {
    "T01": {
        "nama": "Diare",
        "requires": ["L01", "L02", "L03", "L04", "L05"],
        "solusi": [
            "Berikan oralit / cairan rehidrasi oral untuk mencegah dehidrasi.",
            "Tetap berikan ASI/makanan dengan porsi kecil namun sering.",
            "Jaga kebersihan makanan, minuman, dan tangan anak.",
            "Segera bawa ke fasilitas kesehatan jika BAB cair tidak berkurang dalam 2 hari atau muncul tanda dehidrasi berat.",
        ],
    },
    "T02": {
        "nama": "Kejang Demam",
        "requires": ["L06", "L07", "L08", "L09", "L10"],
        "solusi": [
            "Baringkan anak pada posisi miring agar tidak tersedak.",
            "Jangan memasukkan benda apa pun ke dalam mulut anak saat kejang.",
            "Longgarkan pakaian dan singkirkan benda di sekitar yang dapat membahayakan.",
            "Catat lama kejang; bila kejang berlangsung lebih dari 5 menit, segera bawa ke IGD.",
            "Setelah kejang berhenti, kompres anak dengan air hangat dan berikan obat penurun panas sesuai dosis.",
        ],
    },
    "T03": {
        "nama": "Bronchopneumonia",
        "requires": ["L06", "L11", "L12", "L13", "L14", "L15"],
        "solusi": [
            "Segera bawa anak ke dokter/fasilitas kesehatan, terutama bila disertai tarikan dinding dada.",
            "Jaga anak tetap dalam posisi setengah duduk agar lebih mudah bernapas.",
            "Berikan cairan yang cukup dan istirahat total.",
            "Hindari paparan asap rokok dan udara dingin/berdebu.",
        ],
    },
    "T04": {
        "nama": "Asma",
        "requires": ["L16", "L17", "L18", "L19", "L20"],
        "solusi": [
            "Jauhkan anak dari pemicu (debu, asap, udara dingin, bulu hewan).",
            "Bila tersedia, gunakan obat pereda (inhaler) sesuai resep dokter.",
            "Posisikan anak duduk tegak untuk membantu pernapasan saat sesak.",
            "Periksakan ke dokter untuk evaluasi dan penanganan jangka panjang.",
        ],
    },
    "T05": {
        "nama": "Cacingan",
        "requires": ["L21", "L22", "L23", "L24", "L25"],
        "solusi": [
            "Berikan obat cacing sesuai anjuran dokter/puskesmas.",
            "Tingkatkan kebersihan diri: cuci tangan sebelum makan dan setelah dari toilet.",
            "Pastikan anak menggunakan sandal/alas kaki saat bermain di luar.",
            "Perbaiki pola makan agar gizi anak tetap terjaga selama proses pengobatan.",
        ],
    },
}

# ---------------------------------------------------------------------------
# MESIN INFERENSI (FORWARD CHAINING)
# ---------------------------------------------------------------------------

def forward_chaining(fakta_terpilih: set):
    """
    Melakukan penalaran forward chaining sederhana:
    - Menelusuri setiap rule (kondisi IF) dari fakta yang dimasukkan user.
    - Menghitung jumlah gejala yang cocok dan persentase kecocokan tiap rule.
    - Rule yang seluruh syaratnya terpenuhi dianggap "fully fired" (diagnosis pasti).
    """
    hasil = []
    for kode, rule in RULES.items():
        required = set(rule["requires"])
        matched = required & fakta_terpilih
        total = len(required)
        jumlah_cocok = len(matched)
        persentase = (jumlah_cocok / total) * 100 if total else 0
        fully_fired = matched == required and jumlah_cocok > 0
        hasil.append({
            "kode": kode,
            "nama": rule["nama"],
            "matched": sorted(matched),
            "missing": sorted(required - matched),
            "total_gejala_rule": total,
            "jumlah_cocok": jumlah_cocok,
            "persentase": persentase,
            "fully_fired": fully_fired,
            "solusi": rule["solusi"],
        })
    hasil.sort(key=lambda x: x["persentase"], reverse=True)
    return hasil


# ---------------------------------------------------------------------------
# ANTARMUKA (STREAMLIT UI)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Sistem Pakar Deteksi Penyakit Anak", page_icon="🩺", layout="wide")

st.title("🩺 Sistem Pakar Deteksi Penyakit Anak")
st.caption(
    "Rule-Based Expert System dengan mesin inferensi **Forward Chaining** • "
    "Mendeteksi 5 jenis penyakit: Diare, Kejang Demam, Bronchopneumonia, Asma, dan Cacingan."
)

with st.expander("ℹ️ Tentang sistem ini"):
    st.markdown(
        """
        Aplikasi ini merupakan implementasi sederhana dari konsep **Sistem Pakar Diagnosis**
        sebagaimana dijelaskan pada jurnal rujukan:

        - **Basis pengetahuan**: Rule-Based System, disusun dari tabel keputusan menjadi 5 rule IF-THEN.
        - **Kode fakta (gejala)**: L01–L25.
        - **Kode kesimpulan (penyakit)**: T01–T05.
        - **Mesin inferensi**: Forward Chaining — penelusuran dimulai dari fakta/gejala (IF),
          lalu dicocokkan secara maju untuk menguji hipotesis hingga diperoleh kesimpulan (THEN).

        ⚠️ **Disclaimer**: Hasil dari aplikasi ini hanya sebagai simulasi/alat bantu edukasi,
        bukan pengganti diagnosis medis dari dokter atau tenaga kesehatan profesional.
        """
    )

st.markdown("---")
st.subheader("1️⃣ Pilih gejala yang dialami anak")

selected = set()
cols = st.columns(2)
gejala_items = list(GEJALA.items())
half = (len(gejala_items) + 1) // 2

for i, (kode, teks) in enumerate(gejala_items):
    col = cols[0] if i < half else cols[1]
    with col:
        if st.checkbox(f"**{kode}** — {teks}", key=kode):
            selected.add(kode)

st.markdown("---")
col_a, col_b = st.columns([1, 4])
with col_a:
    diagnosa_btn = st.button("🔍 Diagnosis Sekarang", type="primary", use_container_width=True)
with col_b:
    if st.button("↺ Reset Pilihan Gejala"):
        for kode in GEJALA:
            st.session_state[kode] = False
        st.rerun()

if diagnosa_btn:
    if not selected:
        st.warning("Silakan pilih minimal satu gejala terlebih dahulu sebelum melakukan diagnosis.")
    else:
        st.markdown("---")
        st.subheader("2️⃣ Proses Forward Chaining")
        st.write(f"Fakta gejala yang dimasukkan: `{', '.join(sorted(selected))}`")

        hasil = forward_chaining(selected)
        fully_fired = [h for h in hasil if h["fully_fired"]]

        with st.expander("Lihat jejak penalaran (rule trace) untuk setiap rule"):
            for h in hasil:
                status = "✅ Rule terpenuhi penuh (THEN tercapai)" if h["fully_fired"] else "➖ Rule belum terpenuhi penuh"
                st.markdown(
                    f"**Rule {h['kode']} → {h['nama']}** — {status}\n\n"
                    f"- Gejala cocok ({h['jumlah_cocok']}/{h['total_gejala_rule']}): "
                    f"{', '.join(h['matched']) if h['matched'] else '-'}\n"
                    f"- Gejala belum terpenuhi: {', '.join(h['missing']) if h['missing'] else '-'}\n"
                    f"- Persentase kecocokan: {h['persentase']:.0f}%"
                )

        st.markdown("---")
        st.subheader("3️⃣ Hasil Diagnosis")

        if fully_fired:
            for h in fully_fired:
                st.success(
                    f"**Diagnosis: {h['nama']} ({h['kode']})** — seluruh gejala pada rule ini terpenuhi."
                )
                st.markdown("**Solusi / Penanganan Awal:**")
                for s in h["solusi"]:
                    st.markdown(f"- {s}")
        else:
            top = hasil[0]
            if top["persentase"] == 0:
                st.info("Gejala yang dipilih belum cukup sesuai dengan pola penyakit yang dikenali sistem. Disarankan untuk konsultasi langsung dengan dokter.")
            else:
                st.warning(
                    f"Belum ada rule yang terpenuhi secara penuh. Kemungkinan diagnosis tertinggi sementara: "
                    f"**{top['nama']} ({top['kode']})** dengan kecocokan gejala {top['persentase']:.0f}% "
                    f"({top['jumlah_cocok']}/{top['total_gejala_rule']} gejala)."
                )
                st.markdown("**Gejala yang masih perlu diperiksa lebih lanjut untuk memastikan:**")
                st.markdown(", ".join(f"`{g}` - {GEJALA[g]}" for g in top["missing"]))
                st.markdown("**Saran penanganan awal (sementara, berdasarkan kemungkinan tertinggi):**")
                for s in top["solusi"]:
                    st.markdown(f"- {s}")

            st.markdown("##### Peringkat kecocokan seluruh kemungkinan penyakit")
            for h in hasil:
                st.write(f"- {h['kode']} — {h['nama']}: {h['persentase']:.0f}% kecocokan ({h['jumlah_cocok']}/{h['total_gejala_rule']} gejala)")

        st.caption(
            "⚠️ Hasil ini bersifat simulatif berdasarkan basis aturan sederhana dan tidak menggantikan "
            "pemeriksaan medis langsung oleh dokter."
        )

st.markdown("---")
st.caption("Sumber referensi konsep: Analisis Komponen Sistem Pakar pada Sistem Deteksi Penyakit Anak — "
           "https://mail.jsisfotek.org/index.php/JSisfotek/article/view/34/34")
