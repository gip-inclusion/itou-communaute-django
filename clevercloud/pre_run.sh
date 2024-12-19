cd secrets-vault || exit
git pull
cd - || exit
sops -d secrets-vault/c1/"$ENVIRONMENT".enc.env > .env
