git clone "$ITOU_SECRETS_HTTPS_REPO_URL" secrets-vault
sops -d secrets-vault/c3/"$ENVIRONMENT".enc.env > .env
