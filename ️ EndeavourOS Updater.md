# 🖥️ EndeavourOS Updater (GTK4 / libadwaita)

Der **EndeavourOS Updater** ist eine moderne grafische Update-Anwendung für **Arch Linux**, **EndeavourOS** und kompatible Distributionen.

Die Anwendung kombiniert eine GTK4/libadwaita Oberfläche mit einem integrierten Terminal (VTE), sodass alle Updates **transparent sichtbar** ausgeführt werden.

Keine versteckten Hintergrundprozesse — jede Aktion ist nachvollziehbar.

---

## ✨ Features

* ✅ GTK4 + libadwaita Oberfläche
* ✅ integriertes Terminal (VTE)
* ✅ Pacman Updates
* ✅ AUR Updates (yay)
* ✅ Flatpak Updates
* ✅ Update-Vorschau (ohne Installation)
* ✅ Fortschrittsanzeige
* ✅ automatische Systemstatus-Zusammenfassung
* ✅ Erkennung systemkritischer Updates
* ✅ Reboot-Hinweis bei Kernel/System-Updates

---

## 🧩 Unterstützte Updatequellen

* **Pacman**
* **AUR (yay)**
* **Flatpak**

Alle Quellen können unabhängig voneinander aktiviert werden.

---

## 📦 Voraussetzungen

### Benötigte Pakete

```bash
sudo pacman -S python gtk4 libadwaita vte3 python-gobject
```

### Optional (empfohlen)

```bash
sudo pacman -S pacman-contrib flatpak
yay -S yay
```

| Tool         | Zweck                |
| ------------ | -------------------- |
| checkupdates | Pacman Updateprüfung |
| yay          | AUR Updates          |
| flatpak      | Flatpak Updates      |
| sudo         | Systemupdates        |
| bash         | Command Execution    |

---

## ⚙️ Installation

Die Installation erfolgt ausschließlich über das Installationsscript.

### 1. Repository klonen

```bash
git clone <REPO-URL>
cd endeavour-updater
```

### 2. Installationsscript ausführbar machen

```bash
chmod +x install.sh
```

### 3. Installation starten

```bash
sudo ./install.sh
```

Das Script installiert:

* Programmdateien nach `/opt/endeavour-updater`
* Starter nach `/usr/local/bin/endeavour-updater`
* Desktop-Eintrag ins Systemmenü

---

## ▶️ Anwendung starten

Nach erfolgreicher Installation:

```bash
endeavour-updater
```

oder über das Anwendungsmenü deiner Desktopumgebung.

---

## 🚀 Nutzung

### Updates anzeigen

1. Updatequellen auswählen
2. **„Verfügbare Updates anzeigen“** klicken

Es werden nur verfügbare Updates angezeigt — nichts wird installiert.

---

### Updates installieren

1. Quellen auswählen
2. **„Updates installieren“** klicken
3. Sicherheitsdialog bestätigen
4. sudo Passwort im Terminal eingeben (falls nötig)

Die Updates werden nacheinander ausgeführt:

1. Pacman (`pacman -Syu`)
2. AUR (`yay -Sua`)
3. Flatpak (`flatpak update`)

---

## 🔐 Sicherheit & Verhalten

* sudo wird nur bei Bedarf abgefragt
* Terminal zeigt alle Befehle live
* keine automatischen Neustarts
* Snapshot wird vor Updates empfohlen

---

## 🔄 Automatische Reboot-Erkennung

Nach Updates analysiert der Updater automatisch:

```
/var/log/pacman.log
```

Wenn systemkritische Pakete aktualisiert wurden, erscheint ein Hinweisdialog.

### Erkannte kritische Updates

* Kernel (`linux*`)
* systemd
* glibc
* mkinitcpio
* pacman
* dbus
* util-linux
* NVIDIA Treiber

👉 In diesem Fall wird ein Neustart empfohlen.

---

## 📊 Statusübersicht nach Updates

Nach Abschluss zeigt die Anwendung automatisch:

* verbleibende Pacman Updates
* AUR Updates
* Flatpak Updates
* Gesamtstatus des Systems

---

## ❌ Deinstallation

Die vollständige Entfernung erfolgt über das bereitgestellte Script.

### 1. Script ausführbar machen

```bash
chmod +x uninstall.sh
```

### 2. Deinstallation starten

```bash
sudo ./uninstall.sh
```

Dabei werden entfernt:

* `/opt/endeavour-updater`
* `/usr/local/bin/endeavour-updater`
* Desktop-Eintrag

Benutzerdaten bleiben unverändert.

---

## 🐞 Troubleshooting

### AUR Updates funktionieren nicht

`yay` fehlt:

```bash
yay -S yay
```

---

### Pacman Updates werden nicht angezeigt

Installiere:

```bash
sudo pacman -S pacman-contrib
```

---

### Flatpak wird übersprungen

```bash
sudo pacman -S flatpak
```

---

### GTK Fehler beim Start

Teste GI Installation:

```bash
python -c "import gi"
```

---

## 📁 Projektstruktur

```
endeavour-updater/
│
├── endeavour_updater.py
├── install.sh
├── uninstall.sh
└── README.md
```

---

## 🧪 Getestet auf

* EndeavourOS
* Arch Linux
* GNOME (Wayland & X11)

Sollte mit allen GTK4 Desktopumgebungen funktionieren.

---

## 📜 Lizenz

Freie Nutzung für private und Open-Source Projekte.

(Lizenz hier eintragen, z.B. MIT)

---

## ❤️ Ziel des Projekts

Dieser Updater wurde entwickelt, um Arch-basierte Systeme sicher und transparent zu aktualisieren — ohne Blackbox-Verhalten klassischer GUI-Updater.

Alle Aktionen bleiben jederzeit sichtbar und kontrollierbar.

