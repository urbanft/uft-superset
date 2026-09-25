# Docker build
```
docker build -f Dockerfile.uft -t uft-superset:develop .

```

# Docker Compose
```
docker compose -f docker-compose.uft.yml up -d
```

# UFT Superset Init Database & Import Dashboard
```

Inside Superset container, run the following commands to initialize the database and import the dashboard:

#Initialize the database
```
/app/scripts/superset-init.sh
```

```
#Import the dashboard
```
/app/scripts/superset-import.sh
```
