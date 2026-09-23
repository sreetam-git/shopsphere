Step 1 — Create Dockerfile
--------------------------
Inside user-service/, create a file named:
Dockerfile

Step 2 — Create .dockerignore
-----------------------------
Also inside user-service/:

Step 3 — Build the Docker image
-------------------------------
From inside user-service:
docker build -t shopsphere-user-service .

On Windows Docker Desktop, change your .env database host from:
localhost 
to:
host.docker.internal

Then Run:
----------\
docker run --env-file .env -p 8000:8000 shopsphere-user-service