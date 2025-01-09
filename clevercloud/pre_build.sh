git clone "$ITOU_SECRETS_HTTPS_REPO_URL" secrets-vault
sops -d secrets-vault/c3/"$ENVIRONMENT".enc.env > .env

# generate requirements file to let clevercloud know which packages to install
uv export --format requirements-txt --no-dev --frozen > requirements.txt
