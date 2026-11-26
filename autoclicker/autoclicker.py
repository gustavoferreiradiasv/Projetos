import threading
import time
import tkinter as tk
import keyboard
import pyautogui

pyautogui.FAILSAFE = True


class AutoclickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Autoclicker com Atalho")
        self.root.geometry("310x230")
        self.root.resizable(False, False)

        self.clicando = False
        self.app_rodando = True
        self._lock = threading.Lock()

        self._construir_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        keyboard.add_hotkey("F6", self._on_hotkey_f6)

        self.thread_cliques = threading.Thread(
            target=self._worker_autoclicker, daemon=True
        )
        self.thread_cliques.start()

    def _construir_ui(self) -> None:
        tk.Label(
            self.root,
            text="Python Autoclicker",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        self.lbl_status = tk.Label(
            self.root,
            text="Status: PARADO",
            font=("Arial", 11),
            fg="red",
        )
        self.lbl_status.pack(pady=5)

        frame_intervalo = tk.Frame(self.root)
        frame_intervalo.pack(pady=6)

        tk.Label(frame_intervalo, text="Intervalo (s): ").pack(side=tk.LEFT)
        self.entry_intervalo = tk.Entry(frame_intervalo, width=10)
        self.entry_intervalo.insert(0, "0.1")
        self.entry_intervalo.pack(side=tk.LEFT)

        self.btn_toggle = tk.Button(
            self.root,
            text="Ativar (F6)",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            command=self.alternar_estado,
        )
        self.btn_toggle.pack(pady=14)

    def _obter_intervalo(self) -> float:
        raw = self.entry_intervalo.get().strip().replace(",", ".")
        try:
            valor = float(raw)
            if valor <= 0:
                return 0.1
            return valor
        except ValueError:
            return 0.1

    def _on_hotkey_f6(self) -> None:
        if self.app_rodando:
            self.root.after(0, self.alternar_estado)

    def alternar_estado(self) -> None:
        with self._lock:
            self.clicando = not self.clicando
            ativo = self.clicando
        self._atualizar_interface(ativo)

    def _atualizar_interface(self, ativo: bool) -> None:
        if ativo:
            self.lbl_status.config(text="Status: ATIVADO (Rodando)", fg="green")
            self.btn_toggle.config(text="Desativar (F6)", bg="#ff4d4d", fg="white")
        else:
            self.lbl_status.config(text="Status: PARADO", fg="red")
            self.btn_toggle.config(text="Ativar (F6)", bg="#4CAF50", fg="white")

    def _worker_autoclicker(self) -> None:
        while self.app_rodando:
            with self._lock:
                ativo = self.clicando

            if ativo:
                intervalo = self.root.after(0, self._obter_intervalo)
                # Lê o valor diretamente da entrada com segurança básica
                raw = self.entry_intervalo.get().strip().replace(",", ".")
                try:
                    tempo = float(raw)
                    if tempo <= 0:
                        tempo = 0.1
                except ValueError:
                    tempo = 0.1

                try:
                    pyautogui.click()
                except pyautogui.FailSafeException:
                    with self._lock:
                        self.clicando = False
                    self.root.after(0, lambda: self._atualizar_interface(False))
                    time.sleep(0.2)
                    continue

                time.sleep(tempo)
            else:
                time.sleep(0.1)

    def ao_fechar(self) -> None:
        self.app_rodando = False
        with self._lock:
            self.clicando = False
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    AutoclickerApp(janela)
    janela.mainloop()
