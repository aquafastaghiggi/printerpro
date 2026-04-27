#!/bin/sh
set -e

echo "Aguardando o banco e aplicando migrations..."
until python -m alembic upgrade head; do
  echo "Banco ainda nao esta pronto. Tentando novamente em 2s..."
  sleep 2
done

if [ "${AUTO_CREATE_ADMIN:-true}" = "true" ]; then
  echo "Garantindo tenant e admin iniciais..."
  python scripts/create_admin.py
fi

exec "$@"
