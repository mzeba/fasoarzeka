#!/usr/bin/env bash
# Compile les catalogues .po en .mo (fichiers livrés avec le package).
# Nécessite gettext (msgfmt) : brew install gettext / apt install gettext
set -euo pipefail

cd "$(dirname "$0")/.."

LOCALES_DIR="src/fasoarzeka/locales"
DOMAIN="fasoarzeka"

found=0
for po in "$LOCALES_DIR"/*/LC_MESSAGES/"$DOMAIN".po; do
  [ -e "$po" ] || continue
  found=1
  mo="${po%.po}.mo"
  echo "Compilation de $po -> $mo"
  msgfmt --check --statistics -o "$mo" "$po"
done

if [ "$found" -eq 0 ]; then
  echo "Aucun catalogue .po trouvé dans $LOCALES_DIR" >&2
  exit 1
fi

echo "Compilation terminée."
