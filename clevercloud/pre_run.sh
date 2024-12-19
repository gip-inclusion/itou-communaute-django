cd secrets-vault || exit
git pull
cd - || exit
sops -d secrets-vault/c3/"$ENVIRONMENT".enc.env > .env
