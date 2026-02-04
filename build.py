import PyInstaller.__main__
import os
import shutil
import customtkinter

def build():
    print("🚀 Starting Build Process...")

    # Get customtkinter path for data inclusion
    ctk_path = os.path.dirname(customtkinter.__file__)
    print(f"📦 CustomTkinter found at: {ctk_path}")

    # Define PyInstaller arguments
    args = [
        'gui.py',                        # Main script
        '--name=FacebookBotManager',     # Name of the executable
        '--onedir',                      # Create a directory (not single file)
        '--noconsole',                   # Hide the console window
        f'--add-data={ctk_path}{os.pathsep}customtkinter', # Add CTK assets
        '--clean',                       # Clean cache
        '--confirm',                     # Overwrite output directory

        # Explicit hidden imports to ensure they are packed
        '--hidden-import=tenacity',
        '--hidden-import=psutil',
        '--hidden-import=undetected_chromedriver',
        '--hidden-import=docx',
        '--hidden-import=pdfplumber',
        '--hidden-import=googleapiclient',
        '--hidden-import=PIL',           # Used by CTK
        '--hidden-import=threading',
        '--hidden-import=multiprocessing',
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print("\n✅ Build Successful!")
    print("📂 Output directory: dist/FacebookBotManager")

    # Post-build: Create a README or copy essential files if they exist
    dist_dir = os.path.join("dist", "FacebookBotManager")

    # Copy .env if exists (as a template)
    if os.path.exists(".env"):
        shutil.copy(".env", os.path.join(dist_dir, ".env"))
        print("✓ Copied .env to dist folder")

    # Create a README with instructions
    readme_content = """
    FACEBOOK BOT MANAGER - SETUP
    ============================

    1. Asigurați-vă că fișierul '.env' este configurat corect.
    2. Copiați fișierul 'service_account.json' (Google Credentials) în acest folder.
    3. Copiați folderul 'chrome_data' aici dacă doriți să păstrați sesiunile anterioare (sau va fi creat automat).
    4. Porniți 'FacebookBotManager.exe'.

    ATENȚIE:
    - Nu ștergeți folderele '_internal' sau alte fișiere .dll.
    - Pentru a actualiza codul, rulați din nou scriptul de build.
    """

    with open(os.path.join(dist_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✓ Created README.txt in dist folder")

if __name__ == "__main__":
    build()
