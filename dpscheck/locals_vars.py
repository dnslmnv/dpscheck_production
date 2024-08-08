# locals_vars.py
SECRET_KEY = 'django-insecure-wa#75l@ub0+vr1_q^(34nvew(-6$v&lk^vhgbxj5#1z7+q+%65'
PG_NAME = 'deploy-db' # as a POSTGRES_DB in .pg-env
PG_USER = 'deploy-test-user' # as in  POSTGRES_USER in .pg-env
PG_PASSWORD = 'your-deploy-test-password' # as a POSTGRES_PASSWORD  in .pg-env
PG_HOST = 'postgresql-db' # as the DB's service name in docker-compose.yml
