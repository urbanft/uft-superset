import os


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
