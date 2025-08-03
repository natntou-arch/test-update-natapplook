import os
import shutil
import zipfile
import requests
import tempfile
caca
# === CONFIGURATION ===
GITHUB_USER = "natntou-arch"
GITHUB_REPO = "test-update-natapplook"
BRANCH = "main"
INSTALL_DIR = r"C:\NetAppMonitor"
VERSION_FILE_LOCAL = os.path.join(INSTALL_DIR, "version.txt")
VERSION_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/version.txt"
ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"

EXCLUSIONS = {"update_from_github.py", "config.ini", "version.txt"}

def get_local_version():
    try:
        with open(VERSION_FILE_LOCAL, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    r = requests.get(VERSION_FILE_URL)
    if r.status_code != 200:
        raise Exception(f"Impossible de lire la version distante ({r.status_code})")
    return r.text.strip()

def version_plus_recente(v1, v2):
    """Renvoie True si v2 > v1"""
    def parse(v):
        return [int(x) for x in v.strip().split(".")]
    return parse(v2) > parse(v1)

def download_zip():
    print("[INFO] Téléchargement de la nouvelle version...")
    r = requests.get(ZIP_URL)
    if r.status_code != 200:
        raise Exception(f"Erreur de téléchargement : {r.status_code}")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp.write(r.content)
    tmp.close()
    return tmp.name

def safe_delete_all(path):
    for item in os.listdir(path):
        if item in EXCLUSIONS:
            continue
        full = os.path.join(path, item)
        if os.path.isdir(full):
            shutil.rmtree(full)
        else:
            os.remove(full)

def copy_all(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def apply_update(zip_path):
    print("[INFO] Application de la mise à jour...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        tmp_extract = tempfile.mkdtemp()
        zip_ref.extractall(tmp_extract)
        extracted_folder = os.path.join(tmp_extract, f"{GITHUB_REPO}-{BRANCH}")
        safe_delete_all(INSTALL_DIR)
        copy_all(extracted_folder, INSTALL_DIR)
        shutil.rmtree(tmp_extract)
        os.remove(zip_path)
        print("[OK] Mise à jour terminée.")

def main():
    print("=== Vérification des mises à jour ===")
    local = get_local_version()
    print(f"[INFO] Version actuelle : {local}")
    try:
        remote = get_remote_version()
        print(f"[INFO] Version distante : {remote}")
        if version_plus_recente(local, remote):
            print("[INFO] Mise à jour disponible !")
            zip_path = download_zip()
            apply_update(zip_path)
            with open(VERSION_FILE_LOCAL, "w") as f:
                f.write(remote)
        else:
            print("[OK] Le programme est déjà à jour.")
    except Exception as e:
        print(f"[ERREUR] {e}")

if __name__ == "__main__":
    main()

