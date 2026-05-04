import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class ScbAuthConfig:
    """
    Singleton de configuration de scb_auth.

    Instancié une seule fois en bas de ce fichier sous le nom ``scb_config``.
    La méthode ``validate()`` est appelée par ``AppConfig.ready()`` au
    démarrage de Django : toute erreur de configuration stoppe le serveur.

    Utilisation dans le code :
        from scb_auth.conf import scb_config

        scb_config.get("OTP_DIGITS")
        scb_config.is_field_enabled("otp_secret")
        scb_config.get_username_field()
    """

    _DEFAULTS: dict = {
        "OPTIONAL_FIELDS": [],
        "CREDENTIALS_SUPERUSER": {
            "username": "admin",
            "password": "admin",
        },
        "USERNAME_FIELD":  "phone_number",
        "OTP_LIFETIME":    300,
        "OTP_DIGITS":      6,
        "USE_OTP":         True,
        "JWT_HTTP_ONLY":     True,
        "JWT_COOKIE_JSON":   False,
    }

    AVAILABLE_OPTIONAL_FIELDS: set = {"otp_secret", "status_verified"}
    AVAILABLE_USERNAME_FIELDS: set = {"phone_number", "email"}

    # Cache interne : None = pas encore résolu
    _resolved: dict | None = None

    def _raw(self) -> dict:
        """Retourne le dict SCB_AUTH brut depuis settings (jamais None)."""
        return getattr(settings, "SCB_AUTH", {})

    def get(self, key: str):
        """
        Retourne la valeur de *key* (depuis SCB_AUTH ou la valeur par défaut).

        Le cache est rempli lors du premier appel si validate() n'a pas encore
        été appelé (cas des imports effectués avant AppConfig.ready()).
        """
        if self._resolved is None:
            self._resolved = {**self._DEFAULTS, **self._raw()}
        return self._resolved.get(key, self._DEFAULTS[key])

   
    def optional_fields_enabled(self) -> set:
        """Ensemble des champs optionnels valides déclarés dans SCB_AUTH."""
        return set(self.get("OPTIONAL_FIELDS")) & self.AVAILABLE_OPTIONAL_FIELDS

    def is_field_enabled(self, field_name: str) -> bool:
        """True si *field_name* est actif (absent de OPTIONAL_FIELDS)."""
        return field_name not in self.optional_fields_enabled()

    def get_username_field(self) -> str:
        """Retourne USERNAME_FIELD validé (la validation stricte est dans validate())."""
        return self.get("USERNAME_FIELD")

    def validate(self) -> None:
        raw   = self._raw()
        errors: list[str] = []

        unknown_keys = set(raw) - set(self._DEFAULTS)
        if unknown_keys:
            errors.append(
                f"Clés inconnues : {unknown_keys}. "
                f"Clés valides : {set(self._DEFAULTS)}"
            )

        # validation de OPTIONAL_FIELDS
        optional_fields = raw.get("OPTIONAL_FIELDS", self._DEFAULTS["OPTIONAL_FIELDS"])
        if not isinstance(optional_fields, (list, tuple, set)):
            errors.append(
                f"'OPTIONAL_FIELDS' doit être une liste, "
                f"reçu : {type(optional_fields).__name__}"
            )
        else:
            bad = set(optional_fields) - self.AVAILABLE_OPTIONAL_FIELDS
            if bad:
                errors.append(
                    f"'OPTIONAL_FIELDS' contient des valeurs invalides : {bad}. "
                    f"Valeurs acceptées : {self.AVAILABLE_OPTIONAL_FIELDS}"
                )

        # verificatino de CREDENTIALS_SUPERUSER
        credentials_superuser = raw.get(
            "CREDENTIALS_SUPERUSER", self._DEFAULTS["CREDENTIALS_SUPERUSER"]
        )
        if not isinstance(credentials_superuser, dict):
            errors.append(
                f"'CREDENTIALS_SUPERUSER' doit être un dict, "
                f"reçu : {type(credentials_superuser).__name__}"
            )
        else:
            bad = set(credentials_superuser) - {"username", "password"}
            if bad:
                errors.append(
                    f"'CREDENTIALS_SUPERUSER' contient des clés invalides : {bad}. "
                    f"Clés acceptées : {'username', 'password'}"
                )

       # validation de USERNAME_FIELD
        username_field = raw.get("USERNAME_FIELD", self._DEFAULTS["USERNAME_FIELD"])
        if username_field not in self.AVAILABLE_USERNAME_FIELDS:
            errors.append(
                f"'USERNAME_FIELD' = '{username_field}' est invalide. "
                f"Valeurs acceptées : {self.AVAILABLE_USERNAME_FIELDS}"
            )

        # validation de OTP_DIGITS qui doit etre un entier entre 4 et 10
        otp_digits = raw.get("OTP_DIGITS", self._DEFAULTS["OTP_DIGITS"])
        if not isinstance(otp_digits, int) or not (4 <= otp_digits <= 10):
            errors.append(
                f"'OTP_DIGITS' doit être un entier entre 4 et 10, "
                f"reçu : {otp_digits!r}"
            )

        # validation de OTP_LIFETIME qui doit etre un entier positif superieur a 0
        otp_lifetime = raw.get("OTP_LIFETIME", self._DEFAULTS["OTP_LIFETIME"])
        if not isinstance(otp_lifetime, int) or otp_lifetime <= 0:
            errors.append(
                f"'OTP_LIFETIME' doit être un entier positif, "
                f"reçu : {otp_lifetime!r}"
            )

        # validation de USE_OTP
        use_otp = raw.get("USE_OTP", self._DEFAULTS["USE_OTP"])
        if not isinstance(use_otp, bool):
            errors.append(
                f"'USE_OTP' doit être un booléen (True/False), "
                f"reçu : {type(use_otp).__name__}"
            )
            
        # validation de JWT_HTTP_ONLY
        jwt_http_only = raw.get("JWT_HTTP_ONLY", self._DEFAULTS["JWT_HTTP_ONLY"])
        if not isinstance(jwt_http_only, bool):
            errors.append(
                f"'JWT_HTTP_ONLY' doit être un booléen (True/False), "
                f"reçu : {type(jwt_http_only).__name__}"
            )
            
        # validation JWT_COOKIE_JSON
        jwt_cookie_json = raw.get("JWT_COOKIE_JSON", self._DEFAULTS["JWT_COOKIE_JSON"])
        if not isinstance(jwt_cookie_json, bool):
            errors.append(
                f"'JWT_COOKIE_JSON' doit être un booléen (True/False), "
                f"reçu : {type(jwt_cookie_json).__name__}"
            )

        # Résultat
        if errors:
            bullet_list = "\n".join(f"  • {e}" for e in errors)
            raise ImproperlyConfigured(
                f"Configuration SCB_AUTH invalide ({len(errors)} erreur(s)) :\n"
                + bullet_list
            )

        # Mise en cache après validation réussie
        self._resolved = {**self._DEFAULTS, **raw}
        logger.debug("scb_auth – configuration SCB_AUTH validée avec succès.")


    def reset(self) -> None:
        """
        Vide le cache interne.
        Utile dans les tests qui modifient settings via @override_settings.
        """
        self._resolved = None


# Singleton partagé — à importer partout dans le projet
scb_config = ScbAuthConfig()