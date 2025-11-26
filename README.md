# Dictée Vocale 🎤

Application de dictée vocale avec reconnaissance vocale Google, disponible en **version web** et **version desktop**.

## 🌐 Version Web (PWA)

Application web progressive installable sur tous les appareils.

**Accès direct :** [https://91laurent.github.io/dictee-vocale/](https://91laurent.github.io/dictee-vocale/)

### Fonctionnalités Web
- ✅ Fonctionne sur tous les navigateurs (Chrome, Edge, Safari, Firefox)
- ✅ Installable comme application (PWA)
- ✅ Compatible mobile et desktop
- ✅ Multi-plateforme (Windows, Mac, Linux, Android, iOS)
- ✅ Copie automatique dans le presse-papier

### Utilisation Web
1. Ouvrir [https://91laurent.github.io/dictee-vocale/](https://91laurent.github.io/dictee-vocale/)
2. Cliquer sur le bouton micro
3. Parler clairement
4. Le texte apparaît et est copié automatiquement

---

## 🖥️ Version Desktop (Windows)

Application Windows native avec collage automatique et raccourcis globaux.

**Téléchargement :** [Releases](https://github.com/91laurent/dictee-vocale/releases)

### Fonctionnalités Desktop
- ✅ Raccourci global **Ctrl+Shift+D** pour dicter n'importe où
- ✅ **Collage automatique** du texte dicté
- ✅ Fenêtre déplaçable avec analyseur visuel animé
- ✅ Fonctionne en arrière-plan (system tray)
- ✅ Interface moderne avec animations

### Utilisation Desktop

**"Lancez SpeechToPaste.exe, placez votre curseur où vous voulez écrire, appuyez sur Ctrl+Shift+D, parlez, et le texte se colle automatiquement."**

**Raccourcis :**
- `Ctrl+Shift+D` : Activer la dictée vocale
- `Ctrl+Shift+Q` : Quitter l'application

### Installation Desktop

1. Télécharger `SpeechToPaste.exe` depuis les [Releases](https://github.com/91laurent/dictee-vocale/releases)
2. Double-cliquer sur le fichier
3. L'icône apparaît dans la barre des tâches
4. Utiliser `Ctrl+Shift+D` dans n'importe quelle application

---

## 📋 Comparaison des versions

| Fonctionnalité | Web | Desktop |
|---|---|---|
| Multi-plateforme | ✅ | ❌ (Windows uniquement) |
| Installation requise | ❌ | ✅ |
| Collage automatique | ❌ | ✅ |
| Raccourci global | ❌ | ✅ (Ctrl+Shift+D) |
| Fonctionne hors ligne | ✅ (après 1ère visite) | ✅ |
| Analyseur visuel | ❌ | ✅ |

---

## 🛠️ Développement

### Version Desktop - Code Source

```bash
cd desktop
pip install -r requirements.txt
pythonw speech_to_paste.pyw
```

### Compiler l'exécutable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="SpeechToPaste" speech_to_paste.pyw
```

---

## 📝 Auteur

**91laurent**
- GitHub: [@91laurent](https://github.com/91laurent)
- Email: laurent91210@gmail.com

---

## 📄 Licence

MIT License - Libre d'utilisation et de modification
