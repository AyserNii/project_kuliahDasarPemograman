from modules.cli_menu import jalankan_cli

def jalankan_utama():
    print("=" * 45)
    print("  Selamat Datang Di Aplikasi SMARTSTOCK CLI")
    print("  Sistem Management Stok Barang")
    print("=" * 45)

    try:
        jalankan_cli()
    except KeyboardInterrupt:
        print("\n\nAplikasi dihentikan oleh pengguana.")

    except Exception as kesalahan:
        print(f"\nTerjadi kesalahan: {kesalahan}")

    finally:
        print("\nTerima kasih telah menggunakan aplikasi SMARTSTOCK CLI.")
        print("Sampai jumpa lagi!")

if __name__ == "__main__":
    jalankan_utama()