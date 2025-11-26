"""
Speech-to-Paste
===============
Application de dictée vocale avec collage automatique.
Raccourci: Ctrl+Shift+D pour activer la dictée.
Raccourci: Ctrl+Shift+Q pour quitter l'application.

Auteur: 91laurent
"""

import sys
import os
import threading
import random
import pyperclip
import keyboard
import speech_recognition as sr
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSystemTrayIcon, QMenu, QStyle
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QAction, QPixmap, QPainter, QColor


class Signals(QObject):
    """Signaux pour communication entre threads."""
    show_popup = pyqtSignal()
    hide_popup = pyqtSignal()
    update_status = pyqtSignal(str)
    paste_text = pyqtSignal()
    update_waveform = pyqtSignal(list)


class WaveformWidget(QWidget):
    """Widget d'analyseur de forme d'onde style Apple."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.bars = [0.1] * 20
        self.setStyleSheet("background: transparent;")

    def update_bars(self, values):
        """Met à jour les barres de l'analyseur."""
        self.bars = values
        self.update()

    def paintEvent(self, event):
        """Dessine l'analyseur."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        bar_count = len(self.bars)
        bar_width = (width - (bar_count - 1) * 3) / bar_count
        max_height = height - 10

        for i, value in enumerate(self.bars):
            x = i * (bar_width + 3)
            bar_height = max(3, value * max_height)
            y = (height - bar_height) / 2

            # Gradient de couleur
            if value > 0.7:
                color = QColor("#ef4444")  # Rouge
            elif value > 0.4:
                color = QColor("#f59e0b")  # Orange
            else:
                color = QColor("#3b82f6")  # Bleu

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 2, 2)

        painter.end()


class DictationPopup(QWidget):
    """Fenêtre popup de dictée."""

    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.drag_position = None
        self.waveform_data = [0] * 20

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        # Configuration de la fenêtre
        self.setWindowTitle("Dictée Vocale")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 160)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Container avec style
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
                border-radius: 16px;
                border: 2px solid #3b82f6;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 15, 20, 15)
        container_layout.setSpacing(8)

        # Titre
        self.title_label = QLabel("🎤 Dictée Vocale")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent; border: none;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status
        self.status_label = QLabel("Parlez maintenant...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #94a3b8; background: transparent; border: none;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Indicateur
        self.indicator = QLabel("●")
        self.indicator.setFont(QFont("Segoe UI", 24))
        self.indicator.setStyleSheet("color: #ef4444; background: transparent; border: none;")
        self.indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget analyseur de forme d'onde
        self.waveform_widget = WaveformWidget()

        container_layout.addWidget(self.title_label)
        container_layout.addWidget(self.indicator)
        container_layout.addWidget(self.waveform_widget)
        container_layout.addWidget(self.status_label)

        layout.addWidget(self.container)
        self.setLayout(layout)

        # Timer pour animation
        self.blink_state = True
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_indicator)

    def connect_signals(self):
        """Connecte les signaux."""
        self.signals.show_popup.connect(self.show_and_listen)
        self.signals.hide_popup.connect(self.hide)
        self.signals.update_status.connect(self.update_status)
        self.signals.paste_text.connect(self.do_paste)
        self.signals.update_waveform.connect(self.update_waveform)

    def show_and_listen(self):
        """Affiche la popup et commence l'écoute."""
        # Centrer sur l'écran
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 3
        self.move(x, y)

        # Réinitialiser l'état
        self.status_label.setText("Parlez maintenant...")
        self.status_label.setStyleSheet("color: #94a3b8; background: transparent; border: none;")
        self.indicator.setStyleSheet("color: #ef4444; background: transparent; border: none;")

        self.show()
        self.blink_timer.start(500)

        # Lancer l'écoute dans un thread séparé
        threading.Thread(target=self.listen, daemon=True).start()

    def blink_indicator(self):
        """Animation de clignotement."""
        if self.blink_state:
            self.indicator.setStyleSheet("color: #ef4444; background: transparent; border: none;")
        else:
            self.indicator.setStyleSheet("color: #7f1d1d; background: transparent; border: none;")
        self.blink_state = not self.blink_state

    def listen(self):
        """Écoute et transcrit la voix."""
        self.is_listening = True

        # Timer pour animer l'analyseur pendant l'écoute
        animation_timer = QTimer()
        animation_timer.timeout.connect(self.animate_waveform)
        animation_timer.start(100)

        try:
            with sr.Microphone() as source:
                # Ajuster pour le bruit ambiant
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                self.signals.update_status.emit("🎧 Écoute en cours...")

                # Écouter
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)

                animation_timer.stop()
                self.signals.update_status.emit("⏳ Transcription...")
                self.blink_timer.stop()
                self.indicator.setStyleSheet("color: #f59e0b; background: transparent; border: none;")

                # Animation de fin
                self.signals.update_waveform.emit([0.1] * 20)

                # Transcrire avec Google
                text = self.recognizer.recognize_google(audio, language="fr-FR")

                if text:
                    # Copier dans le presse-papier
                    pyperclip.copy(text)
                    self.signals.update_status.emit(f"✅ \"{text[:30]}{'...' if len(text) > 30 else ''}\"")

                    # Attendre un peu pour que l'utilisateur voie le résultat
                    QTimer.singleShot(500, self.signals.paste_text.emit)
                    QTimer.singleShot(1500, self.signals.hide_popup.emit)
                else:
                    self.signals.update_status.emit("❌ Aucun texte détecté")
                    QTimer.singleShot(1500, self.signals.hide_popup.emit)

        except sr.WaitTimeoutError:
            animation_timer.stop()
            self.signals.update_status.emit("⏰ Temps écoulé")
            QTimer.singleShot(1500, self.signals.hide_popup.emit)
        except sr.UnknownValueError:
            animation_timer.stop()
            self.signals.update_status.emit("❓ Parole non reconnue")
            QTimer.singleShot(1500, self.signals.hide_popup.emit)
        except sr.RequestError as e:
            animation_timer.stop()
            self.signals.update_status.emit(f"🌐 Erreur réseau")
            QTimer.singleShot(1500, self.signals.hide_popup.emit)
        except Exception as e:
            animation_timer.stop()
            self.signals.update_status.emit(f"❌ Erreur: {str(e)[:20]}")
            QTimer.singleShot(1500, self.signals.hide_popup.emit)
        finally:
            self.is_listening = False
            self.blink_timer.stop()
            if animation_timer.isActive():
                animation_timer.stop()

    def animate_waveform(self):
        """Anime l'analyseur de forme d'onde de manière aléatoire."""
        values = [random.uniform(0.2, 0.9) for _ in range(20)]
        self.signals.update_waveform.emit(values)

    def update_status(self, text):
        """Met à jour le statut."""
        self.status_label.setText(text)
        if "✅" in text:
            self.status_label.setStyleSheet("color: #22c55e; background: transparent; border: none;")
            self.indicator.setStyleSheet("color: #22c55e; background: transparent; border: none;")
        elif "❌" in text or "❓" in text or "⏰" in text:
            self.status_label.setStyleSheet("color: #ef4444; background: transparent; border: none;")

    def update_waveform(self, values):
        """Met à jour l'analyseur de forme d'onde."""
        self.waveform_widget.update_bars(values)

    def do_paste(self):
        """Simule Ctrl+V pour coller."""
        keyboard.press_and_release('ctrl+v')

    def mousePressEvent(self, event):
        """Gère le début du glisser-déposer."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Gère le déplacement de la fenêtre."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Gère la fin du glisser-déposer."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()


class SpeechToPasteApp:
    """Application principale."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.signals = Signals()
        self.popup = DictationPopup(self.signals)

        self.setup_tray()
        self.setup_hotkey()

    def create_icon(self):
        """Crée une icône de micro programmatiquement."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fond bleu arrondi
        painter.setBrush(QColor("#3b82f6"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 64, 64, 12, 12)

        # Micro blanc
        painter.setBrush(QColor("white"))
        # Corps du micro
        painter.drawRoundedRect(24, 12, 16, 28, 8, 8)
        # Support
        painter.drawRect(30, 40, 4, 8)
        # Base
        painter.drawRect(22, 48, 20, 4)

        painter.end()
        return QIcon(pixmap)

    def setup_tray(self):
        """Configure l'icône dans la barre des tâches."""
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.create_icon())
        self.tray.setToolTip("Speech-to-Paste (Ctrl+Shift+D)")

        # Menu
        menu = QMenu()

        activate_action = QAction("🎤 Activer (Ctrl+Shift+D)", menu)
        activate_action.triggered.connect(self.signals.show_popup.emit)
        menu.addAction(activate_action)

        menu.addSeparator()

        quit_action = QAction("❌ Quitter (Ctrl+Shift+Q)", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

        # Notification de démarrage
        self.tray.showMessage(
            "Speech-to-Paste",
            "Ctrl+Shift+D = Dicter\nCtrl+Shift+Q = Quitter",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def setup_hotkey(self):
        """Configure les raccourcis clavier globaux."""
        keyboard.add_hotkey('ctrl+shift+d', self.on_hotkey_dictate, suppress=True)
        keyboard.add_hotkey('ctrl+shift+q', self.on_hotkey_quit, suppress=True)

    def on_hotkey_dictate(self):
        """Appelé quand Ctrl+Shift+D est pressé."""
        if not self.popup.is_listening:
            self.signals.show_popup.emit()

    def on_hotkey_quit(self):
        """Appelé quand Ctrl+Shift+Q est pressé."""
        self.quit()

    def quit(self):
        """Quitte l'application."""
        keyboard.unhook_all()
        self.tray.hide()
        self.app.quit()

    def run(self):
        """Lance l'application."""
        return self.app.exec()


if __name__ == "__main__":
    app = SpeechToPasteApp()
    sys.exit(app.run())
