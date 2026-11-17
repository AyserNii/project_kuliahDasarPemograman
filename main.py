from modules.cli_menu import run_cli

def main():
    print("=" * 45)
    print("  Selamat Datang Di Aplikasi SMARTSTOCK CLI")
    print("  Sistem Management Stok Barang")
    print("=" * 45)

    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\nAplikasi dihentikan oleh pengguana.")

    except Exception as error:
        print(f"\nTerjadi kesalahan: {error}")

    finally:
        print("\nTerima kasih telah menggunakan aplikasi SMARTSTOCK CLI.")
        print("Sampai jumpa lagi!")

if __name__ == "__main__":
    main()