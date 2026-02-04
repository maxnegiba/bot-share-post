import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sys
import threading
import time
import multiprocessing
import signal
from dotenv import load_dotenv, set_key

# Import main logic
import main

# Configurare aspect GUI
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class BotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Facebook Bot Manager v12.1")
        self.geometry("900x700")

        # Variabila pentru procesul botului
        self.bot_process = None
        self.log_file = "bot_stealth_v12.log"
        self.running = False

        # Layout grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_config = self.tabview.add("Configurare")
        self.tab_control = self.tabview.add("Control & Loguri")

        # --- TAB 1: CONFIGURARE ---
        self.setup_config_tab()

        # --- TAB 2: CONTROL ---
        self.setup_control_tab()

        # Load initial values
        self.load_env_values()

        # Start log updater
        self.update_logs_flag = True
        self.log_thread = threading.Thread(target=self.tail_logs, daemon=True)
        self.log_thread.start()

    def setup_config_tab(self):
        # Scrollable frame pentru configurare
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_config, label_text="Editare Variabile .env")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Dicționar pentru a păstra referințe la input-uri
        self.entries = {}

        # Categorii de variabile
        self.add_section("Credențiale Facebook")
        self.add_entry("Email", "FB_EMAIL")
        self.add_entry("Parolă", "FB_PASSWORD", show="*")
        self.add_entry("Nume Pagină (Opțional)", "FB_PAGE_NAME")

        self.add_section("Google & Drive")
        self.add_entry("Fișier Credențiale (JSON)", "GOOGLE_CREDENTIALS_FILE")
        self.add_entry("Nume Fișier DOCX (Drive)", "DRIVE_FILENAME_DOCX")
        self.add_entry("Nume Fișier PDF (Drive)", "DRIVE_FILENAME_PDF")

        self.add_section("Proxy & Rețea")
        self.add_entry("Proxy URL", "PROXY_URL")
        self.add_entry("Timezone Proxy", "PROXY_TIMEZONE")

        self.add_section("Limite & Grupuri")
        self.add_entry("Limită Grupuri/Zi", "DAILY_GROUP_LIMIT")
        self.add_entry("Max Grupuri în Pool", "MAX_GROUPS_POOL")
        self.add_entry("Max Reîncercări (Retries)", "MAX_RETRIES")

        self.add_section("Pauze & Timing (Secunde/Ore)")
        self.add_entry("Pauză Minimă (sec)", "DELAY_MIN_SEC")
        self.add_entry("Pauză Maximă (sec)", "DELAY_MAX_SEC")
        self.add_entry("Refresh Sesiune (ore)", "SESSION_REFRESH_HOURS")

        self.add_section("Setări Sistem")
        self.add_entry("Cale Profil Chrome", "CHROME_PROFILE_PATH")
        self.add_entry("Folder Temp", "TEMP_DOWNLOAD_DIR")
        self.add_entry("Warmup (True/False)", "DO_WARMUP")

        # Buton Salvare
        self.save_btn = ctk.CTkButton(self.tab_config, text="💾 Salvează Configurația", command=self.save_config, height=40, font=("Arial", 14, "bold"))
        self.save_btn.pack(pady=10, padx=20, fill="x")

    def add_section(self, title):
        label = ctk.CTkLabel(self.scroll_frame, text=title, font=("Arial", 16, "bold"), anchor="w")
        label.pack(fill="x", pady=(15, 5), padx=5)

    def add_entry(self, label_text, env_key, show=None):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=2, padx=5)

        lbl = ctk.CTkLabel(frame, text=label_text, width=200, anchor="w")
        lbl.pack(side="left", padx=5)

        entry = ctk.CTkEntry(frame, show=show)
        entry.pack(side="right", expand=True, fill="x", padx=5)

        self.entries[env_key] = entry

    def load_env_values(self):
        load_dotenv(override=True)
        for key, entry in self.entries.items():
            val = os.getenv(key, "")
            entry.delete(0, "end")
            entry.insert(0, val)

    def save_config(self):
        env_path = ".env"
        # Dacă nu există, îl creăm
        if not os.path.exists(env_path):
            with open(env_path, "w") as f: f.write("")

        try:
            for key, entry in self.entries.items():
                val = entry.get().strip()
                # set_key actualizează fisierul .env
                set_key(env_path, key, val)

            messagebox.showinfo("Succes", "Configurația a fost salvată cu succes!\n(Reporniți botul pentru a aplica schimbările)")
            # Reîncărcăm în memorie pentru a fi siguri
            load_dotenv(override=True)
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut salva configuratia:\n{str(e)}")

    def setup_control_tab(self):
        # Butoane Start/Stop
        btn_frame = ctk.CTkFrame(self.tab_control)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_start = ctk.CTkButton(btn_frame, text="▶ PORNEȘTE BOT", command=self.start_bot, fg_color="green", hover_color="darkgreen", height=50)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = ctk.CTkButton(btn_frame, text="⏹ OPREȘTE BOT", command=self.stop_bot, fg_color="darkred", hover_color="maroon", state="disabled", height=50)
        self.btn_stop.pack(side="right", expand=True, fill="x", padx=5)

        # Log Viewer
        self.log_textbox = ctk.CTkTextbox(self.tab_control, font=("Consolas", 12))
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_textbox.insert("1.0", "--- Așteptare loguri ---\n")

    def start_bot(self):
        if self.running:
            return

        # Verificări sumare
        if not os.path.exists(".env"):
             messagebox.showwarning("Atenție", "Fisierul .env lipsește! Salvează configurația întâi.")
             return

        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.log_textbox.insert("end", f"\n>>> [{time.strftime('%H:%M:%S')}] PORNIM PROCESUL BOTULUI...\n")

        # Lansăm procesul
        # Important: folosim un wrapper care setează environment-ul corect dacă e nevoie
        self.bot_process = multiprocessing.Process(target=run_bot_process, daemon=True)
        self.bot_process.start()

    def stop_bot(self):
        if not self.running or not self.bot_process:
            return

        if messagebox.askyesno("Confirmare", "Sigur vrei să oprești botul?"):
            self.kill_process()

    def kill_process(self):
        if self.bot_process and self.bot_process.is_alive():
            self.log_textbox.insert("end", f"\n>>> [{time.strftime('%H:%M:%S')}] PRIMIT COMANDĂ OPRIRE. SE INCHIDE...\n")
            self.bot_process.terminate()
            self.bot_process.join(timeout=3)
            if self.bot_process.is_alive():
                self.bot_process.kill()

        self.running = False
        self.bot_process = None
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.log_textbox.insert("end", f">>> [{time.strftime('%H:%M:%S')}] BOT OPRIT.\n")

    def tail_logs(self):
        last_pos = 0
        while self.update_logs_flag:
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, "r", encoding="utf-8", errors='ignore') as f:
                        f.seek(last_pos)
                        new_data = f.read()
                        if new_data:
                            last_pos = f.tell()
                            # Update GUI thread-safe
                            self.log_textbox.after(0, self.append_log, new_data)
                except Exception:
                    pass
            time.sleep(1)

    def append_log(self, text):
        self.log_textbox.insert("end", text)
        self.log_textbox.see("end")

    def on_close(self):
        if self.running:
            if messagebox.askokcancel("Ieșire", "Botul rulează. Vrei să îl oprești și să ieși?"):
                self.kill_process()
                self.update_logs_flag = False
                self.destroy()
        else:
            self.update_logs_flag = False
            self.destroy()

def run_bot_process():
    # Această funcție rulează în proces separat
    # Reîncărcăm environment-ul să fim siguri
    load_dotenv(override=True)

    # Pornim main-ul
    try:
        main.main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Eroare fatală proces: {e}")

if __name__ == "__main__":
    multiprocessing.freeze_support()

    app = BotGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
