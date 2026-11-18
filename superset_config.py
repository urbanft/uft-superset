import os
from flask_appbuilder.security.manager import AUTH_LDAP, AUTH_DB

# --------------------------------------------------
# PostgreSQL - Superset metadata database
# --------------------------------------------------

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]
POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DATABASE}"
)


# --------------------------------------------------
# Superset security
# --------------------------------------------------

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

ENABLE_PROXY_FIX = True

# --------------------------------------------------
# Embedded Superset
# --------------------------------------------------

FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
}

GUEST_ROLE_NAME = "Gamma"

GUEST_TOKEN_JWT_SECRET = os.environ["GUEST_TOKEN_JWT_SECRET"]
GUEST_TOKEN_JWT_AUDIENCE = os.environ["GUEST_TOKEN_JWT_AUDIENCE"]

GUEST_TOKEN_JWT_ALGO = "HS256"

GUEST_TOKEN_JWT_EXP_SECONDS = 3600


# --------------------------------------------------
# CORS
# --------------------------------------------------

ENABLE_CORS = True

FAB_API_SWAGGER_UI = True

CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": ["*"],
    "allow_headers": ["*"],
    "resources": ["*"],
}


# --------------------------------------------------
# Embedding
# --------------------------------------------------

TALISMAN_ENABLED = False


WTF_CSRF_ENABLED = False

WTF_CSRF_EXEMPT_LIST = [
    "superset.security.api.guest_token",
]

AUTH_TYPE = (AUTH_LDAP if os.getenv("SUPERSET_AUTH_TYPE", "db").lower() == "ldap" else AUTH_DB)

AUTH_USER_REGISTRATION = True

AUTH_LDAP_SERVER = os.getenv("AUTH_LDAP_SERVER")
AUTH_LDAP_USE_TLS = os.getenv("AUTH_LDAP_USE_TLS", "false").lower() == "true"

AUTH_LDAP_SEARCH = os.getenv("AUTH_LDAP_SEARCH")

AUTH_LDAP_BIND_USER = os.getenv("AUTH_LDAP_BIND_USER")
AUTH_LDAP_BIND_PASSWORD = os.getenv("AUTH_LDAP_BIND_PASSWORD")

AUTH_LDAP_UID_FIELD = os.getenv("AUTH_LDAP_UID_FIELD","sAMAccountName",)

AUTH_LDAP_FIRSTNAME_FIELD = os.getenv("AUTH_LDAP_FIRSTNAME_FIELD","givenName",)

AUTH_LDAP_LASTNAME_FIELD = os.getenv("AUTH_LDAP_LASTNAME_FIELD","sn",)

AUTH_LDAP_EMAIL_FIELD = os.getenv("AUTH_LDAP_EMAIL_FIELD","mail",)

AUTH_LDAP_TLS_DEMAND = False

AUTH_LDAP_ALLOW_LOCAL_DB = True

AUTH_USER_REGISTRATION_ROLE = "InternalUser"

AUTH_ROLES_MAPPING = {
    "Domain Admins": ["Admin"],
    "Administrators": ["Admin"],
    "Devadmins": ["Admin"],
}

AUTH_ROLES_SYNC_AT_LOGIN = True
