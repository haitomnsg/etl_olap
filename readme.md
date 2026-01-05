docker exec -it superset superset db reset
docker exec -it superset superset db upgrade
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@superset.com \
  --password admin
docker exec -it superset superset init