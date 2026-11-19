#!/usr/bin/env bash
# Extrait les messages marqués avec _() dans le modèle .pot,
# puis met à jour chaque catalogue .po existant.
# Nécessite gettext (xgettext, msgmerge) : brew install gettext / apt install gettext
set -euo pipefail

cd "$(dirname "$0")/.."

PKG_DIR="src/fasoarzeka"
LOCALES_DIR="$PKG_DIR/locales"
DOMAIN="fasoarzeka"
POT_FILE="$LOCALES_DIR/$DOMAIN.pot"

mkdir -p "$LOCALES_DIR"

echo "Extraction des messages vers $POT_FILE"
xgettext --language=Python --keyword=_ --from-code=UTF-8 \
  --package-name="$DOMAIN" \
  --msgid-bugs-address="https://github.com/mzeba/fasoarzeka/issues" \
  --no-wrap -o "$POT_FILE" "$PKG_DIR"/*.py

for po in "$LOCALES_DIR"/*/LC_MESSAGES/"$DOMAIN".po; do
  [ -e "$po" ] || continue
  echo "Mise à jour de $po"
  msgmerge --quiet --update --backup=none --no-fuzzy-matching --no-wrap "$po" "$POT_FILE"
done

echo "Terminé. Traduisez les entrées vides, puis lancez scripts/compile_messages.sh"
