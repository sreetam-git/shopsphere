Great. Now we connect to the EC2 instance and install Docker.

STEP -1
----------

From your Windows terminal, go to the folder where your .pem key is saved, then run:

ssh -i shopsphere-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
for example
------------
ssh -i shopsphere-key.pem ec2-user@13.126.223.191

Note: Replace YOUR_EC2_PUBLIC_IP with the instance’s Public IPv4 address from the EC2 console.

STEP -2
----------

If Windows complains about key permissions, run this first in PowerShell:

icacls .\shopsphere-key.pem /inheritance:r
icacls .\shopsphere-key.pem /grant:r "$($env:USERNAME):(R)"

Once connected, your prompt should look roughly like:
[ec2-user@ip-xxx-xxx-xxx-xxx ~]$

STEP -3
---------
Then install Docker:

sudo dnf update -y
sudo dnf install docker -y
sudo systemctl start docker
sudo systemctl enable docker

STEP -4
---------
Add your EC2 user to the Docker group:

sudo usermod -aG docker ec2-user

Then exit:
---
exit

STEP -5
---------
SSH back in:
ssh -i shopsphere-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

Now Test
--------
docker --version














