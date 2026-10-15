import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# =========================================================
# KONFIGURASI APLIKASI
# =========================================================
st.set_page_config(
    page_title="Visualisasi Data Khayla",
    page_icon="📊",
    layout="wide"
)

URL = (
    "https://raw.githubusercontent.com/Alam-A99/DATAAKSI/"
    "refs/heads/main/dataset_fiskal_97_hipoFull.csv"
)

st.title("📊 Dashboard Visualisasi Data")
st.caption("Visualisasi dataset fiskal dan contoh data penjualan.")

# =========================================================
# MEMUAT DATASET
# =========================================================
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

with st.spinner("Memuat dataset dari GitHub..."):
    try:
        df = load_data(URL)
        data_error = None
    except Exception as e:
        df = pd.DataFrame()
        data_error = str(e)

if data_error:
    st.error(
        "Dataset tidak berhasil dimuat dari GitHub. "
        "Periksa koneksi internet atau URL dataset."
    )
    with st.expander("Detail error"):
        st.code(data_error)
else:
    st.success(f"Dataset berhasil dimuat: {df.shape[0]} baris dan {df.shape[1]} kolom.")

    # Sidebar
    st.sidebar.header("Pengaturan")
    menu = st.sidebar.radio(
        "Pilih visualisasi",
        [
            "Ringkasan Dataset",
            "Grafik Dataset Fiskal",
            "Contoh Grafik Penjualan"
        ]
    )

    # =====================================================
    # 1. RINGKASAN DATASET
    # =====================================================
    if menu == "Ringkasan Dataset":
        st.subheader("🔎 10 Data Pertama")
        st.dataframe(df.head(10), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Jumlah Baris", f"{df.shape[0]:,}")
        col2.metric("Jumlah Kolom", f"{df.shape[1]:,}")
        col3.metric("Kolom Numerik", str(len(df.select_dtypes(include="number").columns)))

        st.subheader("Informasi Kolom")
        info_df = pd.DataFrame({
            "Nama Kolom": df.columns,
            "Tipe Data": [str(dtype) for dtype in df.dtypes],
            "Jumlah Data Kosong": [int(df[col].isna().sum()) for col in df.columns]
        })
        st.dataframe(info_df, use_container_width=True)

    # =====================================================
    # 2. GRAFIK DATASET FISKAL
    # =====================================================
    elif menu == "Grafik Dataset Fiskal":
        st.subheader("✨ Visualisasi Dataset Fiskal")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            st.warning("Dataset tidak memiliki kolom numerik yang dapat digrafikkan.")
        else:
            selected_col = st.selectbox(
                "Pilih kolom numerik yang ingin divisualisasikan",
                numeric_cols
            )
            n_rows = st.slider(
                "Jumlah baris yang ditampilkan",
                min_value=5,
                max_value=min(100, len(df)),
                value=min(10, len(df))
            )

            df_plot = df.head(n_rows).copy()
            df_plot["Urutan Data"] = range(1, len(df_plot) + 1)

            st.write(f"Grafik kolom **{selected_col}** untuk {n_rows} baris pertama.")
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor("#FFF0F5")
            ax.set_facecolor("#FFFBF0")

            ax.plot(
                df_plot["Urutan Data"],
                df_plot[selected_col],
                marker="o",
                markersize=8,
                color="#FF69B4",
                linewidth=2.5,
                markerfacecolor="#FFB6C1",
                markeredgecolor="#8B008B",
                label=selected_col
            )

            ax.set_title(
                f"{n_rows} Data Pertama: {selected_col}",
                fontsize=14,
                fontweight="bold",
                color="#C71585"
            )
            ax.set_xlabel("Urutan Data")
            ax.set_ylabel(selected_col)
            ax.grid(True, linestyle=":", alpha=0.5)
            ax.legend()
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            st.subheader("Grafik Interaktif")
            fig_interaktif = px.line(
                df_plot,
                x="Urutan Data",
                y=selected_col,
                markers=True,
                title=f"Perubahan {selected_col} pada {n_rows} Data Pertama",
                template="plotly_white"
            )
            fig_interaktif.update_traces(
                line=dict(color="#FF69B4", width=3),
                marker=dict(size=9, color="#4169E1")
            )
            fig_interaktif.update_layout(
                xaxis_title="Urutan Data",
                yaxis_title=selected_col
            )
            st.plotly_chart(fig_interaktif, use_container_width=True)

            # Nilai tertinggi; abaikan nilai kosong
            valid = df_plot[selected_col].dropna()
            if not valid.empty:
                max_idx = valid.idxmax()
                max_val = valid.loc[max_idx]
                st.metric("Nilai Tertinggi pada Data yang Ditampilkan", f"{max_val:,.4g}")
                st.caption(
                    f"Nilai tertinggi tersebut berasal dari indeks data {max_idx} "
                    "(indeks asli DataFrame dimulai dari 0)."
                )

            st.subheader("Data yang Digunakan")
            st.dataframe(df_plot.drop(columns=["Urutan Data"]), use_container_width=True)

            csv = df_plot.drop(columns=["Urutan Data"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh data yang ditampilkan (CSV)",
                data=csv,
                file_name="data_fiskal_terpilih.csv",
                mime="text/csv"
            )

    # =====================================================
    # 3. CONTOH GRAFIK PENJUALAN
    # =====================================================
    elif menu == "Contoh Grafik Penjualan":
        st.subheader("🛍️ Contoh Penjualan per Bulan")

        sales_df = pd.DataFrame({
            "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Juni", "Juli"],
            "Penjualan": [150, 200, 180, 250, 125, 200, 130]
        })

        fig_bar = px.bar(
            sales_df,
            x="Bulan",
            y="Penjualan",
            text="Penjualan",
            title="Penjualan per Bulan",
            color="Penjualan",
            color_continuous_scale="RdPu"
        )
        fig_bar.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Jumlah Penjualan",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=sales_df,
            x="Bulan",
            y="Penjualan",
            color="#FFB6C1",
            ax=ax
        )
        ax.plot(
            range(len(sales_df)),
            sales_df["Penjualan"],
            color="#4169E1",
            marker="o",
            linewidth=2,
            label="Perubahan Penjualan"
        )
        ax.set_title("Penjualan per Bulan dengan Garis Penghubung", fontweight="bold")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Jumlah Penjualan")
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.info(
            "Catatan: data penjualan di halaman ini adalah data contoh, "
            "bukan bagian dari dataset fiskal GitHub."
        )
        st.dataframe(sales_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Dibuat untuk tugas visualisasi data.")
