#!/usr/bin/env python3
import gi
import subprocess
import threading
import shutil
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Gtk, Adw, GLib, Vte


class UpdaterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("EndeavourOS Updater")
        self.set_default_size(720, 700)

        self.running = False
        self._progress_running = False
        self._progress_source_id = None

        # Änderung: getrennte Environments
        # - env_query: für Abfragen (stabil/englisch via LC_ALL=C)
        # - env_run:   für Installation (Systemsprache, z.B. Deutsch)
        self.env_query = dict(os.environ, LC_ALL="C")
        self.env_run = dict(os.environ)

        # Marker für Reboot-Erkennung über pacman.log
        self.update_started_at = None
        self.pacman_log_path = "/var/log/pacman.log"
        self.pacman_log_pos = None

        # ---------- Layout ----------
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # ---------- Toggle ----------
        toggle_box = Gtk.Box(spacing=12)
        toggle_box.set_halign(Gtk.Align.CENTER)

        self.btn_pacman = Gtk.ToggleButton(label="Pacman")
        self.btn_aur = Gtk.ToggleButton(label="AUR")
        self.btn_flatpak = Gtk.ToggleButton(label="Flatpak")

        for b in (self.btn_pacman, self.btn_aur, self.btn_flatpak):
            b.set_active(True)
            toggle_box.append(b)

        box.append(toggle_box)

        # ---------- Status ----------
        self.status = Gtk.Label(label="Bereit")

        self.progress = Gtk.ProgressBar(show_text=True)
        self.progress.set_fraction(0.0)

        box.append(self.status)
        box.append(self.progress)

        # ---------- Terminal ----------
        self.terminal = Vte.Terminal()
        self.terminal.set_scroll_on_output(True)
        self.terminal.set_scrollback_lines(10000)
        self.terminal.set_input_enabled(True)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.terminal)
        box.append(scroll)

        # Starttext
        self.term_clear()
        self.term_write(
            "🖥️ System bereit\r\n\r\n"
            "• Wähle die Update-Quellen\r\n"
            "• Zeige Updates oder installiere sie\r\n"
        )

        # ---------- Buttons ----------
        button_box = Gtk.Box(spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)

        self.search_button = Gtk.Button(label="Verfügbare Updates anzeigen")
        self.search_button.connect("clicked", self.search_updates)

        self.start_button = Gtk.Button(label="Updates installieren")
        self.start_button.connect("clicked", self.start_updates)

        quit_button = Gtk.Button(label="Beenden")
        quit_button.add_css_class("destructive-action")
        quit_button.connect("clicked", self.quit_app)

        button_box.append(self.search_button)
        button_box.append(self.start_button)
        button_box.append(quit_button)

        box.append(button_box)

        # ---------- HeaderBar (NEU) ----------
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title="EndeavourOS Updater", subtitle=""))

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(box)

        self.set_content(toolbar_view)

    # ---------- Terminal helpers ----------

    def term_clear(self):
        self.terminal.reset(True, True)

    def term_write(self, text):
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
        data = text.encode("utf-8", errors="replace")
        try:
            self.terminal.feed(data)
        except TypeError:
            self.terminal.feed(data, len(data))

    def term_write_idle(self, text):
        GLib.idle_add(lambda: (self.term_write(text), False)[1])

    # ---------- Progress ----------

    def start_progress(self):
        self.progress.set_fraction(0.0)
        self.progress.set_text("Arbeitet …")
        self._progress_running = True

        if self._progress_source_id:
            GLib.source_remove(self._progress_source_id)

        def pulse():
            if self._progress_running:
                self.progress.pulse()
                return True
            return False

        self._progress_source_id = GLib.timeout_add(100, pulse)

    def stop_progress(self):
        self._progress_running = False

        if self._progress_source_id:
            GLib.source_remove(self._progress_source_id)
            self._progress_source_id = None

        self.progress.set_fraction(1.0)
        self.progress.set_text("Fertig")

    # ---------- Update Suche ----------

    def search_updates(self, _):
        if self.running:
            return

        self.term_clear()
        self.status.set_label("Suche nach Updates …")
        self.start_progress()

        def worker():
            updates = []

            if self.btn_pacman.get_active():
                r = subprocess.run(
                    ["checkupdates"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("Pacman", r.stdout))

            if self.btn_aur.get_active():
                r = subprocess.run(
                    ["yay", "-Qua"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("AUR", r.stdout))

            if self.btn_flatpak.get_active():
                r = subprocess.run(
                    ["flatpak", "list", "--updates"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("Flatpak", r.stdout))

            def show():
                total = 0

                for src, out in updates:
                    lines = out.strip().splitlines() if out.strip() else []
                    total += len(lines)

                    self.term_write(f"\r\n{src}:\r\n")

                    if lines:
                        for line in lines[:30]:
                            self.term_write(f"  {line}\r\n")
                    else:
                        self.term_write("  System aktuell\r\n")

                if total == 0:
                    self.term_write("\r\n✅ System ist vollständig aktuell\r\n")

                self.stop_progress()
                self.status.set_label("Bereit")

            GLib.idle_add(show)

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Start Updates ----------

    def start_updates(self, _):
        if self.running:
            return

        dialog = Adw.AlertDialog(
            heading="Updates installieren?",
            body="Es wird empfohlen vorher einen Snapshot zu erstellen.",
        )
        dialog.add_response("no", "Nein")
        dialog.add_response("yes", "Ja")
        dialog.set_default_response("yes")
        dialog.set_close_response("no")

        def response(dlg, result):
            resp = dlg.choose_finish(result)
            if resp != "yes":
                return

            self.running = True

            # Zeitpunkt + pacman.log Marker setzen
            self.update_started_at = GLib.get_real_time()  # Mikrosekunden
            self.pacman_log_pos = None
            try:
                with open(self.pacman_log_path, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    self.pacman_log_pos = f.tell()
            except Exception:
                self.pacman_log_pos = None

            self.term_clear()
            self.status.set_label("Installiere Updates …")
            self.start_progress()

            self.term_write("🔐 sudo Passwort ggf. unten eingeben\r\n\r\n")
            GLib.idle_add(lambda: (self.terminal.grab_focus(), False)[1])

            self.run_update_chain()

        dialog.choose(self, None, response)

    # ---------- Update Chain ----------

    def run_update_chain(self):
        steps = []

        if self.btn_pacman.get_active():
            steps.append((["sudo", "pacman", "-Syu"], "Pacman Update"))

        if self.btn_aur.get_active():
            steps.append((["yay", "-Sua"], "AUR Update"))

        if self.btn_flatpak.get_active():
            # verhindert Hängenbleiben an Prompts
            steps.append((["flatpak", "update", "-y", "--noninteractive"], "Flatpak Update"))

        def run_next(i=0):
            if i >= len(steps):
                self.finish_updates()
                return

            cmd, title = steps[i]
            self.run_terminal_command(cmd, title, lambda status: run_next(i + 1))

        run_next()

    # ---------- Terminal Command ----------

    def run_terminal_command(self, cmd, title, callback):
        self.term_write(f"\r\n=== {title} ===\r\n")
        self.term_write(f"$ {' '.join(cmd)}\r\n\r\n")

        def exited(term, status):
            if status == 0:
                self.term_write("✔ Schritt abgeschlossen\r\n")
            else:
                self.term_write(f"❌ Fehler (Code {status})\r\n")

            term.disconnect(handler)
            callback(status)

        handler = self.terminal.connect("child-exited", exited)

        # WICHTIG: Environment explizit übergeben (stabiler für flatpak/yay usw.)
        # Änderung: Installation läuft mit env_run (Systemsprache)
        envv = [f"{k}={v}" for k, v in self.env_run.items()]

        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            cmd,
            envv,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            None,
            None,
        )

    # ---------- Kritische Updates / Reboot-Erkennung ----------

    def _read_pacman_log_since_marker(self):
        """
        Liest neue pacman.log-Zeilen seit self.pacman_log_pos.
        Gibt Liste von geänderten Paketnamen zurück (installed/upgraded/downgraded).
        """
        if self.pacman_log_pos is None:
            return []

        try:
            with open(self.pacman_log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self.pacman_log_pos)
                new = f.read()
        except Exception:
            return []

        pkgs = []
        for line in new.splitlines():
            line = line.strip()
            for verb in ("upgraded", "installed", "downgraded"):
                token = f"] [ALPM] {verb} "
                if token in line:
                    part = line.split(token, 1)[1]
                    pkg = part.split(" ", 1)[0].strip()
                    if pkg:
                        pkgs.append(pkg)
                    break

        seen = set()
        uniq = []
        for p in pkgs:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        return uniq

    def _critical_packages_hit(self, pkgs):
        """
        Entscheidet, ob Reboot-Hinweis nötig ist, basierend auf Paketnamen.
        """
        exact = {
            "systemd", "systemd-libs", "systemd-sysvcompat",
            "glibc", "linux-api-headers",
            "mkinitcpio", "mkinitcpio-busybox", "mkinitcpio-openswap",
            "pacman", "util-linux", "dbus",
        }

        prefixes = (
            "linux",   # linux, linux-lts, linux-zen, linux-firmware, ...
            "nvidia",  # oft reboot-relevant nach Treiberwechsel (optional)
        )

        hits = []
        for p in pkgs:
            if p in exact:
                hits.append(p)
                continue
            for pref in prefixes:
                if p.startswith(pref):
                    hits.append(p)
                    break

        seen = set()
        hits_uniq = []
        for h in hits:
            if h not in seen:
                seen.add(h)
                hits_uniq.append(h)

        return hits_uniq

    def maybe_show_reboot_dialog_from_pacman_log(self):
        """
        Zeigt Dialog nur, wenn Kernel/systemkritische Pakete seit Marker aktualisiert wurden.
        """
        def worker():
            pkgs = self._read_pacman_log_since_marker()
            hits = self._critical_packages_hit(pkgs)

            if hits:
                details = (
                    "Folgende systemkritische Pakete wurden aktualisiert:\n- "
                    + "\n- ".join(hits)
                )
                GLib.idle_add(lambda: (self.show_reboot_dialog(details), False)[1])

        threading.Thread(target=worker, daemon=True).start()

    def show_reboot_dialog(self, details=""):
        body = "Bitte starten Sie das System neu."
        if details:
            body = f"{body}\n\n{details}"

        dlg = Adw.AlertDialog(
            heading="Systemkritisches Update",
            body=body,
        )
        dlg.add_response("ok", "Verstanden")
        dlg.set_default_response("ok")
        dlg.set_close_response("ok")

        dlg.choose(self, None, lambda d, res: d.choose_finish(res))

    # ---------- Erweiterung: saubere Zusammenfassung ----------

    def show_post_update_summary(self, after_done=None):
        """
        Zeigt am Ende die gleiche Übersicht wie bei 'Verfügbare Updates anzeigen'.
        Vorher wird einmal gecleart, damit es sauber aussieht.
        """
        def worker():
            updates = []

            if self.btn_pacman.get_active():
                r = subprocess.run(
                    ["checkupdates"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("Pacman", r.stdout))

            if self.btn_aur.get_active():
                r = subprocess.run(
                    ["yay", "-Qua"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("AUR", r.stdout))

            if self.btn_flatpak.get_active():
                r = subprocess.run(
                    ["flatpak", "list", "--updates"],
                    capture_output=True,
                    text=True,
                    env=self.env_query,
                )
                updates.append(("Flatpak", r.stdout))

            def show():
                self.term_clear()
                self.term_write("\r\n\r\n📌 Status nach dem Update:\r\n")
                total = 0

                for src, out in updates:
                    lines = out.strip().splitlines() if out.strip() else []
                    total += len(lines)

                    self.term_write(f"\r\n{src}:\r\n")
                    if lines:
                        for line in lines[:30]:
                            self.term_write(f"  {line}\r\n")
                    else:
                        self.term_write("  System aktuell\r\n")

                if total == 0:
                    self.term_write("\r\n✅ System ist vollständig aktuell\r\n")

                if after_done:
                    after_done()

            GLib.idle_add(show)

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Finish ----------

    def finish_updates(self):
        self.running = False
        self.stop_progress()
        self.status.set_label("Fertig")

        # Erst die saubere Status-Übersicht anzeigen (mit clear),
        # danach ggf. Reboot-Dialog für kritische Updates
        self.show_post_update_summary(after_done=self.maybe_show_reboot_dialog_from_pacman_log)

    # ---------- Quit ----------

    def quit_app(self, _):
        self.running = False
        self.get_application().quit()


class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id="de.endeavouros.updater")

    def do_activate(self):
        UpdaterWindow(self).present()


def main():
    app = App()
    raise SystemExit(app.run(None))


if __name__ == "__main__":
    main()

