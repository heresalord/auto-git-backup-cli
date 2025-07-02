# 🔄 Auto Git Backup CLI

> Un outil open source développé par **KMS STUDIO DEV** pour automatiser les sauvegardes Git locales avec restauration et monitoring intelligent.

## 🇫🇷 Description

Auto Git Backup est un outil CLI interactif qui vous permet de :

- Détecter automatiquement les changements dans vos fichiers
- Commiter les modifications avec un horodatage clair
- Gérer une branche dédiée à vos sauvegardes
- Pousser automatiquement vers un dépôt distant (facultatif)
- Restaurer une ancienne version
- Exclure certains fichiers grâce à `.backupignore`

✨ Convient aux développeurs, créateurs de contenu, ou pour suivre l’évolution d’un projet local sans effort.

---

## 🇬🇧 Description

Auto Git Backup is a smart CLI tool made by **KMS STUDIO DEV** to automatically backup your local changes using Git with intelligent file monitoring and optional auto-push.

### Features

- Detect local changes in real-time
- Commit them with a clean timestamp
- Use a dedicated backup branch
- Auto-push if desired
- Restore a previous state in one command
- Skip files and folders using `.backupignore`

---

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/auto-git-backup-cli.git
cd auto-git-backup-cli
pip install -r requirements.txt
