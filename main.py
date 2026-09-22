"""
main.py
=======
Main application entry point for S3802 Bluetooth Controller & Protocol Lab.
"""

from gui.app import S3802App


def main():
    app = S3802App()
    app.mainloop()


if __name__ == "__main__":
    main()