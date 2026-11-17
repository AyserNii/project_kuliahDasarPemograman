def run_cli():
    while True:
        print("\nMenu SmartStock")
        print("1. Kelola produk")
        print("2. Analisis persediaan")
        print("3. Lihat laporan")
        print("0. Keluar")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "0":
            print("Keluar dari aplikasi.")
            return
        if pilihan == "1":
            print("Fitur kelola produk belum tersedia.")
        elif pilihan == "2":
            print("Fitur analisis persediaan belum tersedia.")
        elif pilihan == "3":
            print("Fitur laporan belum tersedia.")
        else:
            print("Pilihan tidak valid. Masukkan angka 0 sampai 3.")