import sys
from datetime import datetime
from pathlib import Path

from config.settings import IMPORTS_DIR
from modules.analysis import determine_stock_status
from modules.forecasting import calculate_demand_statistics, exponential_smoothing, moving_average
from modules.report import (
    ascii_bar_chart,
    format_table,
    generate_inventory_summary_report,
    generate_stock_chart,
    save_text_report,
)
from modules.validation import (
    validate_non_empty_string,
    validate_non_negative_number,
    validate_positive_number,
    validate_sku,
)
from repositories.analysis_repository import AnalysisRepository
from repositories.product_repository import ProductRepository
from repositories.sales_repository import SalesRepository
from repositories.supplier_repository import SupplierRepository
from repositories.transaction_repository import TransactionRepository
from services.export_service import ExportService
from services.import_service import ImportService
from services.inventory_service import InventoryService


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title.center(56)}")
    print("=" * 60)


def prompt_string(prompt: str, default: str = "") -> str:
    val = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
    return val if val else default


def prompt_float(prompt: str, default: float = 0.0, allow_zero: bool = True) -> float:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return float(default)
        try:
            val = float(raw)
            if not allow_zero and val <= 0:
                print("Nilai harus lebih besar dari 0.")
                continue
            if val < 0:
                print("Nilai tidak boleh negatif.")
                continue
            return val
        except ValueError:
            print("Masukkan angka yang valid.")


class SmartStockCLI:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.supplier_repo = SupplierRepository()
        self.transaction_repo = TransactionRepository()
        self.sales_repo = SalesRepository()
        self.analysis_repo = AnalysisRepository()

        self.import_service = ImportService(self.product_repo, self.supplier_repo)
        self.export_service = ExportService(
            self.product_repo,
            self.transaction_repo,
            self.sales_repo,
            self.analysis_repo,
        )
        self.inventory_service = InventoryService(
            self.product_repo,
            self.sales_repo,
            self.analysis_repo,
        )

    def run(self):
        while True:
            print("\n" + "=" * 60)
            print("         SMARTSTOCK CLI - SISTEM MANAJEMEN INVENTARIS")
            print("=" * 60)
            print("1. Kelola Produk (Tambah / Lihat / Edit / Hapus)")
            print("2. Kelola Supplier (Tambah / Lihat)")
            print("3. Transaksi Persediaan (Stok Masuk / Stok Keluar)")
            print("4. Riwayat Penjualan (Catat Penjualan / Lihat Riwayat)")
            print("5. Analisis Persediaan (Hitung EOQ, SS & Reorder Point)")
            print("6. Peramalan Permintaan (Demand Forecasting)")
            print("7. Laporan & Visualisasi Grafik")
            print("8. Import & Export Data CSV")
            print("0. Keluar")
            print("-" * 60)

            choice = input("Pilih menu [0-8]: ").strip()

            if choice == "0":
                print("\nTerima kasih telah menggunakan SmartStock CLI.")
                break
            elif choice == "1":
                self.menu_products()
            elif choice == "2":
                self.menu_suppliers()
            elif choice == "3":
                self.menu_transactions()
            elif choice == "4":
                self.menu_sales()
            elif choice == "5":
                self.menu_analysis()
            elif choice == "6":
                self.menu_forecasting()
            elif choice == "7":
                self.menu_reports()
            elif choice == "8":
                self.menu_import_export()
            else:
                print("Pilihan tidak valid. Silakan pilih 0-8.")

    # ==================== 1. PRODUK ====================
    def menu_products(self):
        while True:
            print_header("MANAJEMEN DATA PRODUK")
            print("1. Lihat Semua Produk")
            print("2. Tambah Produk Baru")
            print("3. Perbarui Data Produk")
            print("4. Hapus Produk")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.list_products()
            elif ch == "2":
                self.add_product()
            elif ch == "3":
                self.update_product()
            elif ch == "4":
                self.delete_product()

    def list_products(self):
        products = self.product_repo.get_all()
        if not products:
            print("\nBelum ada produk yang terdaftar di database.")
            return

        headers = ["ID", "SKU", "Nama Produk", "Kategori", "Stok", "Satuan", "Harga Modal", "Harga Jual", "Min. Stok"]
        rows = []
        for p in products:
            rows.append([
                p["product_id"],
                p["sku"],
                p["name"][:22],
                p.get("category") or "-",
                f"{float(p['stock_quantity']):.2f}",
                p.get("unit", "pcs"),
                f"Rp {float(p['unit_cost']):,.0f}",
                f"Rp {float(p['selling_price']):,.0f}",
                f"{float(p['minimum_stock']):.2f}",
            ])
        print("\n" + format_table(headers, rows))

    def add_product(self):
        print_header("TAMBAH PRODUK BARU")
        try:
            sku = validate_sku(input("Masukkan SKU (contoh: BRG-003): "))
            if self.product_repo.get_by_sku(sku):
                print(f"[Error] Produk dengan SKU '{sku}' sudah ada.")
                return

            name = validate_non_empty_string(input("Nama Produk: "), "Nama Produk")
            category = prompt_string("Kategori (opsional)")
            unit = prompt_string("Satuan", "pcs")

            # Tampilkan supplier yang tersedia
            suppliers = self.supplier_repo.get_all()
            supplier_id = None
            if suppliers:
                print("\nDaftar Supplier:")
                for s in suppliers:
                    print(f"  [{s['supplier_id']}] {s['supplier_code']} - {s['name']}")
                sup_input = input("Pilih ID Supplier (kosongkan jika tanpa supplier): ").strip()
                if sup_input.isdigit():
                    supplier_id = int(sup_input)

            initial_stock = prompt_float("Stok Awal", 0.0)
            unit_cost = prompt_float("Harga Modal/Beli per Unit (Rp)", 0.0)
            selling_price = prompt_float("Harga Jual per Unit (Rp)", 0.0)
            min_stock = prompt_float("Batas Minimum Stok", 5.0)

            prod = self.product_repo.create(
                sku=sku,
                name=name,
                category=category or None,
                supplier_id=supplier_id,
                unit=unit,
                stock_quantity=initial_stock,
                unit_cost=unit_cost,
                selling_price=selling_price,
                minimum_stock=min_stock,
            )
            print(f"\n[SUKSES] Produk '{prod['name']}' (SKU: {prod['sku']}) berhasil disimpan ke database!")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    def update_product(self):
        print_header("PERBARUI DATA PRODUK")
        self.list_products()
        prod_id_str = input("\nMasukkan ID Produk yang ingin diubah: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        print(f"\nMengedit Produk: {prod['name']} (SKU: {prod['sku']})")
        name = prompt_string("Nama Produk", prod["name"])
        category = prompt_string("Kategori", prod.get("category") or "")
        unit = prompt_string("Satuan", prod.get("unit") or "pcs")
        unit_cost = prompt_float("Harga Modal per Unit", float(prod["unit_cost"]))
        selling_price = prompt_float("Harga Jual per Unit", float(prod["selling_price"]))
        min_stock = prompt_float("Batas Minimum Stok", float(prod["minimum_stock"]))

        try:
            self.product_repo.update(
                product_id=prod["product_id"],
                name=name,
                category=category or None,
                supplier_id=prod.get("supplier_id"),
                unit=unit,
                unit_cost=unit_cost,
                selling_price=selling_price,
                minimum_stock=min_stock,
            )
            print("\n[SUKSES] Data produk berhasil diperbarui.")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    def delete_product(self):
        print_header("HAPUS PRODUK")
        prod_id_str = input("Masukkan ID Produk yang ingin dihapus: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        confirm = input(f"Yakin ingin menghapus produk '{prod['name']}'? (y/n): ").strip().lower()
        if confirm == "y":
            try:
                success = self.product_repo.delete(int(prod_id_str))
                if success:
                    print("\n[SUKSES] Produk berhasil dihapus.")
                else:
                    print("\n[Gagal] Produk tidak dapat dihapus.")
            except Exception as err:
                print(f"\n[Gagal] Tidak dapat menghapus produk: {err}")

    # ==================== 2. SUPPLIER ====================
    def menu_suppliers(self):
        while True:
            print_header("MANAJEMEN DATA SUPPLIER")
            print("1. Lihat Semua Supplier")
            print("2. Tambah Supplier Baru")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.list_suppliers()
            elif ch == "2":
                self.add_supplier()

    def list_suppliers(self):
        suppliers = self.supplier_repo.get_all()
        if not suppliers:
            print("\nBelum ada data supplier di database.")
            return

        headers = ["ID", "Kode Supplier", "Nama Supplier", "Kontak Person", "No. Telepon", "Alamat"]
        rows = [
            [
                s["supplier_id"],
                s["supplier_code"],
                s["name"],
                s.get("contact_name") or "-",
                s.get("phone") or "-",
                (s.get("address") or "-")[:25],
            ]
            for s in suppliers
        ]
        print("\n" + format_table(headers, rows))

    def add_supplier(self):
        print_header("TAMBAH SUPPLIER BARU")
        try:
            code = validate_non_empty_string(input("Kode Supplier (contoh: SUP-002): "), "Kode").upper()
            if self.supplier_repo.get_by_code(code):
                print(f"[Error] Supplier dengan kode '{code}' sudah ada.")
                return

            name = validate_non_empty_string(input("Nama Perusahaan/Pemasok: "), "Nama Supplier")
            contact = prompt_string("Nama Kontak")
            phone = prompt_string("Nomor Telepon")
            address = prompt_string("Alamat")

            sup = self.supplier_repo.create(
                supplier_code=code,
                name=name,
                contact_name=contact or None,
                phone=phone or None,
                address=address or None,
            )
            print(f"\n[SUKSES] Supplier '{sup['name']}' berhasil disimpan ke database!")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    # ==================== 3. TRANSAKSI ====================
    def menu_transactions(self):
        while True:
            print_header("MANAJEMEN TRANSAKSI PERSEDIAAN")
            print("1. Lihat Riwayat Transaksi")
            print("2. Catat Stok Masuk (IN)")
            print("3. Catat Stok Keluar / Penyesuaian (OUT)")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.list_transactions()
            elif ch == "2":
                self.record_inventory_movement("IN")
            elif ch == "3":
                self.record_inventory_movement("OUT")

    def list_transactions(self):
        txns = self.transaction_repo.get_all(limit=50)
        if not txns:
            print("\nBelum ada riwayat transaksi.")
            return

        headers = ["Kode Transaksi", "Waktu", "SKU", "Nama Produk", "Tipe", "Jumlah", "Biaya Satuan", "Catatan"]
        rows = []
        for t in txns:
            dt_str = t["transaction_date"].strftime("%Y-%m-%d %H:%M") if t.get("transaction_date") else "-"
            rows.append([
                t["transaction_code"],
                dt_str,
                t["sku"],
                t["product_name"][:20],
                t["transaction_type"],
                f"{float(t['quantity']):.2f}",
                f"Rp {float(t['unit_cost']):,.0f}",
                (t.get("notes") or "-")[:20],
            ])
        print("\n" + format_table(headers, rows))

    def record_inventory_movement(self, t_type: str):
        label = "STOK MASUK (IN)" if t_type == "IN" else "STOK KELUAR (OUT)"
        print_header(f"CATAT {label}")

        self.list_products()
        prod_id_str = input("\nMasukkan ID Produk: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        qty = prompt_float(f"Jumlah Kuantitas {t_type}", 1.0, allow_zero=False)
        unit_cost = prompt_float("Biaya per unit (Rp)", float(prod["unit_cost"]))
        notes = prompt_string("Catatan Transaksi", f"Transaksi {t_type}")

        # Kode transaksi unik
        timestamp_code = datetime.now().strftime("%Y%m%d%H%M%S")
        txn_code = f"TXN-{t_type}-{timestamp_code}"

        try:
            txn = self.transaction_repo.create(
                transaction_code=txn_code,
                product_id=prod["product_id"],
                transaction_type=t_type,
                quantity=qty,
                unit_cost=unit_cost,
                supplier_id=prod.get("supplier_id") if t_type == "IN" else None,
                notes=notes,
            )
            updated_prod = self.product_repo.get_by_id(prod["product_id"])
            print(f"\n[SUKSES] Transaksi {txn['transaction_code']} berhasil dicatat!")
            print(f"Stok terbaru untuk '{updated_prod['name']}': {float(updated_prod['stock_quantity']):.2f} {updated_prod.get('unit', 'pcs')}")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    # ==================== 4. PENJUALAN ====================
    def menu_sales(self):
        while True:
            print_header("MANAJEMEN RIWAYAT PENJUALAN")
            print("1. Lihat Riwayat Penjualan")
            print("2. Catat Penjualan Baru")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.list_sales()
            elif ch == "2":
                self.record_new_sale()

    def list_sales(self):
        sales = self.sales_repo.get_all(limit=50)
        if not sales:
            print("\nBelum ada riwayat penjualan di database.")
            return

        headers = ["ID Sales", "Kode Transaksi", "Waktu Penjualan", "SKU", "Produk", "Qty Terjual", "Harga Jual", "Total"]
        rows = []
        for s in sales:
            qty = float(s["quantity_sold"])
            price = float(s["unit_price"])
            dt_str = s["sale_date"].strftime("%Y-%m-%d %H:%M") if s.get("sale_date") else "-"
            rows.append([
                s["sales_id"],
                s["transaction_code"],
                dt_str,
                s["sku"],
                s["product_name"][:20],
                f"{qty:.2f}",
                f"Rp {price:,.0f}",
                f"Rp {qty * price:,.0f}",
            ])
        print("\n" + format_table(headers, rows))

    def record_new_sale(self):
        print_header("CATAT PENJUALAN BARU")
        self.list_products()
        prod_id_str = input("\nMasukkan ID Produk yang Terjual: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        curr_stock = float(prod["stock_quantity"])
        print(f"Produk: {prod['name']} | Stok Tersedia: {curr_stock:.2f} {prod.get('unit', 'pcs')}")

        qty = prompt_float("Kuantitas Terjual", 1.0, allow_zero=False)
        selling_price = prompt_float("Harga Jual per Unit (Rp)", float(prod["selling_price"]))
        notes = prompt_string("Catatan Penjualan (opsional)", "Penjualan Pelanggan")

        try:
            sale = self.sales_repo.record_sale(
                product_id=prod["product_id"],
                quantity_sold=qty,
                unit_price=selling_price,
                notes=notes,
            )
            updated_prod = self.product_repo.get_by_id(prod["product_id"])
            total_rev = qty * selling_price
            print(f"\n[SUKSES] Penjualan berhasil dicatat! Total Penjualan: Rp {total_rev:,.0f}")
            print(f"Sisa Stok '{updated_prod['name']}': {float(updated_prod['stock_quantity']):.2f}")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    # ==================== 5. ANALISIS PERSEDIAAN ====================
    def menu_analysis(self):
        while True:
            print_header("OPTIMASI PERSEDIAAN (EOQ, SAFETY STOCK & ROP)")
            print("1. Hitung & Simpan Analisis untuk Satu Produk")
            print("2. Jalankan Analisis Otomatis untuk Seluruh Produk")
            print("3. Lihat Hasil Analisis & Rekomendasi Terakhir")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.run_single_product_analysis()
            elif ch == "2":
                self.run_batch_analysis()
            elif ch == "3":
                self.show_latest_analysis()

    def run_single_product_analysis(self):
        print_header("ANALISIS PERSEDIAAN PRODUK")
        self.list_products()
        prod_id_str = input("\nMasukkan ID Produk untuk dianalisis: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        print(f"\nParameter Optimasi untuk: {prod['name']}")
        s_cost = prompt_float("Biaya Pemesanan per Order (Rp) [S]", 50000.0)
        lead_time = prompt_float("Waktu Tunggu Pengiriman/Lead Time (hari) [L]", 5.0)
        h_rate = prompt_float("Tarif Biaya Simpan per Tahun (% dari harga barang)", 20.0) / 100.0
        z_val = prompt_float("Z-score Tingkat Pelayanan (1.65 = ~95% service level)", 1.65)
        manual_demand = prompt_float("Permintaan Tahunan (D) - Kosongkan/0 untuk hitung otomatis dari penjualan", 0.0)

        try:
            res = self.inventory_service.analyze_product(
                product_id=prod["product_id"],
                ordering_cost=s_cost,
                holding_cost_rate=h_rate,
                lead_time_days=lead_time,
                z_score=z_val,
                manual_annual_demand=manual_demand if manual_demand > 0 else None,
            )

            a = res["analysis"]
            rec = res["recommendation"]
            costs = res["costs"]

            print("\n" + "=" * 60)
            print("                 HASIL PERHITUNGAN INVENTORY")
            print("=" * 60)
            print(f"Produk                    : {prod['name']} (SKU: {prod['sku']})")
            print(f"Permintaan Tahunan (D)    : {float(a['annual_demand']):,.2f} unit/tahun")
            print(f"Biaya Pesan (S)           : Rp {float(a['ordering_cost']):,.2f}")
            print(f"Biaya Simpan/Unit/Thn (H) : Rp {float(a['holding_cost_per_unit_year']):,.2f}")
            print("-" * 60)
            print(f"1. Economic Order Qty (EOQ): {float(a['eoq']):,.2f} unit (Jumlah pesan optimal)")
            print(f"2. Safety Stock (SS)      : {float(a['safety_stock']):,.2f} unit (Persediaan pengaman)")
            print(f"3. Reorder Point (ROP)     : {float(a['reorder_point']):,.2f} unit (Titik order kembali)")
            print("-" * 60)
            print(f"Frekuensi Pemesanan/Tahun  : {costs['number_of_orders_per_year']} kali/tahun")
            print(f"Siklus Pemesanan           : Setiap ~{costs['order_cycle_days']} hari")
            print(f"Total Biaya Persediaan/Thn : Rp {costs['total_cost']:,.2f}")
            print("-" * 60)
            print(f"STATUS STOK SAAT INI      : [{rec['status']}] (Stok Fisik: {rec['current_stock']:.2f})")
            print(f"REKOMENDASI SISTEM        : {rec['action']}")
            print("=" * 60)
            print("[Info] Hasil analisis berhasil disimpan ke tabel inventory_analysis.")
        except Exception as err:
            print(f"\n[Gagal] {err}")

    def run_batch_analysis(self):
        print("\nMenjalankan analisis otomatis untuk seluruh produk...")
        results = self.inventory_service.analyze_all_products()
        success_count = sum(1 for r in results if "error" not in r)
        print(f"\n[SUKSES] Selesai menganalisis {success_count} dari {len(results)} produk.")
        self.show_latest_analysis()

    def show_latest_analysis(self):
        analyses = self.analysis_repo.get_all_latest()
        if not analyses:
            print("\nBelum ada riwayat hasil analisis di database.")
            return

        headers = ["SKU", "Nama Produk", "Stok", "EOQ", "Safety Stock", "Reorder Point", "Status", "Tgl Analisis"]
        rows = []
        for a in analyses:
            stock = float(a["stock_quantity"])
            rop = float(a["reorder_point"])
            ss = float(a["safety_stock"])
            status = determine_stock_status(stock, rop, ss)
            dt_str = str(a.get("analysis_date", "-"))
            rows.append([
                a["sku"],
                a["product_name"][:20],
                f"{stock:.1f}",
                f"{float(a['eoq']):.1f}",
                f"{ss:.1f}",
                f"{rop:.1f}",
                status,
                dt_str,
            ])
        print("\n" + format_table(headers, rows))

    # ==================== 6. PERAMALAN (FORECASTING) ====================
    def menu_forecasting(self):
        print_header("PERAMALAN PERMINTAAN (DEMAND FORECASTING)")
        self.list_products()
        prod_id_str = input("\nMasukkan ID Produk untuk melihat peramalan: ").strip()
        if not prod_id_str.isdigit():
            print("ID produk tidak valid.")
            return

        prod = self.product_repo.get_by_id(int(prod_id_str))
        if not prod:
            print("Produk tidak ditemukan.")
            return

        daily_sales = self.sales_repo.get_daily_sales(prod["product_id"], days=90)
        if not daily_sales:
            print(f"\nBelum ada riwayat penjualan untuk produk '{prod['name']}' dalam 90 hari terakhir.")
            print("Peramalan memerlukan data riwayat penjualan (Menu 4).")
            return

        history_quantities = [float(row["total_quantity"]) for row in daily_sales]
        stats = calculate_demand_statistics(history_quantities)

        ma_3 = moving_average(history_quantities, window_size=3)
        ma_7 = moving_average(history_quantities, window_size=7)
        ses = exponential_smoothing(history_quantities, alpha=0.3)

        print("\n" + "=" * 60)
        print(f"             HASIL PERAMALAN: {prod['name']}")
        print("=" * 60)
        print(f"Jumlah Hari dengan Penjualan : {len(history_quantities)} hari")
        print(f"Rata-rata Permintaan Harian  : {stats['average_daily_demand']:.2f} unit/hari")
        print(f"Standar Deviasi Permintaan   : {stats['daily_demand_stddev']:.2f}")
        print(f"Proyeksi Permintaan Tahunan  : {stats['annual_demand']:,.2f} unit/tahun")
        print("-" * 60)
        print(f"Forecast Moving Average (3 periode) : {ma_3:.2f} unit/hari")
        print(f"Forecast Moving Average (7 periode) : {ma_7:.2f} unit/hari")
        print(f"Forecast Exponential Smoothing (α=0.3): {ses:.2f} unit/hari")
        print("=" * 60)

    # ==================== 7. LAPORAN & GRAFIK ====================
    def menu_reports(self):
        while True:
            print_header("LAPORAN & GRAFIK")
            print("1. Ringkasan Status & Nilai Inventaris")
            print("2. Laporan Produk Perlu Reorder / Kritis")
            print("3. Visualisasi Grafik Stok Barang (ASCII & PNG)")
            print("4. Ekspor Laporan Lengkap ke File Teks (output/reports/)")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                self.show_inventory_summary()
            elif ch == "2":
                self.show_reorder_report()
            elif ch == "3":
                self.show_visual_chart()
            elif ch == "4":
                self.export_text_report()

    def show_inventory_summary(self):
        products = self.product_repo.get_all()
        report = generate_inventory_summary_report(products)
        print("\n" + report)

    def show_reorder_report(self):
        analyses = self.analysis_repo.get_all_latest()
        reorder_list = []
        for a in analyses:
            stock = float(a["stock_quantity"])
            rop = float(a["reorder_point"])
            ss = float(a["safety_stock"])
            status = determine_stock_status(stock, rop, ss)
            if status in ("HABIS", "KRITIS", "PERLU REORDER"):
                reorder_list.append((a, status))

        if not reorder_list:
            print("\nSemua stok produk saat ini dalam batas aman!")
            return

        headers = ["SKU", "Nama Produk", "Stok Fisik", "Reorder Point", "EOQ (Order)", "Status"]
        rows = [
            [
                a["sku"],
                a["product_name"][:22],
                f"{float(a['stock_quantity']):.2f}",
                f"{float(a['reorder_point']):.2f}",
                f"{float(a['eoq']):.0f}",
                status,
            ]
            for a, status in reorder_list
        ]
        print_header("DAFTAR PRODUK YANG HARUS DIORDER KEMBALI")
        print(format_table(headers, rows))

    def show_visual_chart(self):
        products = self.product_repo.get_all()
        if not products:
            print("Belum ada data produk.")
            return

        # Tampilkan ASCII bar chart di terminal
        items = [(p["name"][:18], float(p.get("stock_quantity", 0))) for p in products]
        print(ascii_bar_chart("GRAFIK BATANG TINGKAT STOK BARANG", items))

        # Simpan PNG chart jika matplotlib ada
        png_path = generate_stock_chart(products)
        if png_path:
            print(f"\n[Info] Grafik PNG berhasil dibuat dan disimpan ke: {png_path}")
        else:
            print("\n[Catatan] Library matplotlib tidak terinstall, grafik ditampilkan via ASCII.")

    def export_text_report(self):
        products = self.product_repo.get_all()
        content = generate_inventory_summary_report(products)
        filepath = save_text_report(content, filename_prefix="laporan_inventaris")
        print(f"\n[SUKSES] Laporan tersimpan di: {filepath}")

    # ==================== 8. IMPORT & EXPORT CSV ====================
    def menu_import_export(self):
        while True:
            print_header("LAYANAN IMPORT & EXPORT CSV")
            print("1. Export Seluruh Data Produk ke CSV (storage/exports/backups/)")
            print("2. Export Riwayat Transaksi ke CSV (storage/exports/backups/)")
            print("3. Export Riwayat Penjualan ke CSV (storage/exports/reports/)")
            print("4. Export Hasil Analisis Optimasi ke CSV (storage/exports/reports/)")
            print("5. Import Data Produk dari CSV (storage/imports/)")
            print("6. Import Data Supplier dari CSV (storage/imports/)")
            print("7. Buat Contoh Template File CSV di storage/imports/")
            print("0. Kembali ke Menu Utama")

            ch = input("Pilihan: ").strip()
            if ch == "0":
                break
            elif ch == "1":
                path = self.export_service.export_products_csv()
                print(f"\n[SUKSES] File produk diekspor ke: {path}")
            elif ch == "2":
                path = self.export_service.export_transactions_csv()
                print(f"\n[SUKSES] File transaksi diekspor ke: {path}")
            elif ch == "3":
                path = self.export_service.export_sales_csv()
                print(f"\n[SUKSES] File penjualan diekspor ke: {path}")
            elif ch == "4":
                path = self.export_service.export_inventory_analysis_csv()
                print(f"\n[SUKSES] File analisis diekspor ke: {path}")
            elif ch == "5":
                self.import_products_flow()
            elif ch == "6":
                self.import_suppliers_flow()
            elif ch == "7":
                self.import_service.generate_sample_templates()
                print(f"\n[SUKSES] Template dibuat di direktori: {IMPORTS_DIR}")

    def import_products_flow(self):
        files = list(IMPORTS_DIR.glob("*.csv"))
        if not files:
            print(f"\nTidak ada file CSV di direktori: {IMPORTS_DIR}")
            print("Silakan letakkan file CSV Anda di direktori tersebut atau buat template (Pilihan 7).")
            return

        print("\nDaftar File CSV di folder storage/imports/:")
        for idx, f in enumerate(files, start=1):
            print(f"  {idx}. {f.name}")

        choice = input("Pilih nomor file: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
            print("Pilihan nomor tidak valid.")
            return

        target_file = files[int(choice) - 1]
        print(f"\nMemproses import dari: {target_file.name} ...")
        success, fail, errors = self.import_service.import_products_from_csv(target_file)
        print(f"\n[HASIL IMPORT PRODUK]")
        print(f"- Sukses disimpan : {success} baris")
        print(f"- Gagal / Duplikat: {fail} baris")
        if errors:
            print("\nRincian pesan:")
            for err in errors[:10]:
                print(f"  * {err}")

    def import_suppliers_flow(self):
        files = list(IMPORTS_DIR.glob("*.csv"))
        if not files:
            print(f"\nTidak ada file CSV di direktori: {IMPORTS_DIR}")
            return

        print("\nDaftar File CSV di folder storage/imports/:")
        for idx, f in enumerate(files, start=1):
            print(f"  {idx}. {f.name}")

        choice = input("Pilih nomor file: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
            print("Pilihan nomor tidak valid.")
            return

        target_file = files[int(choice) - 1]
        print(f"\nMemproses import dari: {target_file.name} ...")
        success, fail, errors = self.import_service.import_suppliers_from_csv(target_file)
        print(f"\n[HASIL IMPORT SUPPLIER]")
        print(f"- Sukses disimpan : {success} baris")
        print(f"- Gagal / Duplikat: {fail} baris")
        if errors:
            print("\nRincian pesan:")
            for err in errors[:10]:
                print(f"  * {err}")


def run_cli():
    cli = SmartStockCLI()
    cli.run()
