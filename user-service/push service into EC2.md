Next we need to get the ShopSphere User Service onto EC2. 

Since you already have a Dockerfile locally, the cleanest beginner-friendly approach is:



Your PC

&#x20;  ↓

push code to GitHub

&#x20;  ↓

EC2 clones repository

&#x20;  ↓

docker build

&#x20;  ↓

docker run





Before we do that, make sure your local **user-service/.gitignore** contains:



.venv/

.env

\_\_pycache\_\_/

\*.pyc





**So our next practical steps are:**



1\. Put ShopSphere code on GitHub

2\. Create AWS RDS MySQL

3\. Point User Service DATABASE\_URL to RDS

4\. Clone project on EC2

5\. docker build

6\. docker run

7\. Access FastAPI using EC2 public IP:8000

