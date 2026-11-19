"""
Internationalisation (i18n) des messages de fasoarzeka.

Les messages d'erreur de la bibliothèque sont écrits en anglais et marqués
avec ``_()``. Par défaut, aucune traduction n'est active : les messages
restent en anglais, comme dans les versions précédentes.

Une application active les traductions livrées avec le package en appelant
:func:`install_translations` une fois au démarrage :

    >>> from fasoarzeka import install_translations
    >>> install_translations("fr")

La traduction est propre à la bibliothèque : elle ne modifie ni les
builtins Python ni le domaine gettext global de l'application.
"""

import gettext
import os
from typing import Optional

DOMAIN = "fasoarzeka"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")

_translation: gettext.NullTranslations = gettext.NullTranslations()


def install_translations(lang: Optional[str] = None) -> gettext.NullTranslations:
    """
    Active la traduction des messages de fasoarzeka.

    Args:
        lang: Code de langue (ex. ``"fr"`` ou ``"fr_FR"``). Si ``None``, la
            langue est déterminée par les variables d'environnement
            ``LANGUAGE``, ``LC_ALL``, ``LC_MESSAGES`` puis ``LANG``.

    Returns:
        L'objet de traduction actif. Si aucune traduction n'existe pour la
        langue demandée, un ``NullTranslations`` est renvoyé et les messages
        restent en anglais.
    """
    global _translation

    languages = [lang] if lang else None
    _translation = gettext.translation(
        DOMAIN, localedir=LOCALE_DIR, languages=languages, fallback=True
    )
    return _translation


def _(message: str) -> str:
    """Traduit ``message`` avec la traduction active de la bibliothèque."""
    return _translation.gettext(message)
