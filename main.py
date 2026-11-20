import sys


def jalankan_utama():
    if "--cli" in sys.argv:
        from modules.cli_menu import jalankan_cli

        print("=" * 45)
        print("  Selamat Datang Di Aplikasi SMARTSTOCK CLI")
        print("  Sistem Management Stok Barang")
        print("=" * 45)

        try:
            jalankan_cli()
        except KeyboardInterrupt:
            print("\n\nAplikasi dihentikan oleh pengguna.")
        except Exception as kesalahan:
            print(f"\nTerjadi kesalahan: {kesalahan}")
        finally:
            print("\nTerima kasih telah menggunakan aplikasi SMARTSTOCK CLI.")
            print("Sampai jumpa lagi!")
    else:
        # Default: Membuka antarmuka Desktop GUI (Tkinter)
        from gui.app import jalankan_gui

        try:
            jalankan_gui()
        except KeyboardInterrupt:
            pass
        except Exception as kesalahan:
            print(f"Gagal membuka antarmuka GUI: {kesalahan}")
            print("Menjalankan dalam mode CLI sebagai alternatif...")
            from modules.cli_menu import jalankan_cli

            jalankan_cli()


if __name__ == "__main__":
    jalankan_utama()
