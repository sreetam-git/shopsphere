Windows has permissive default file permissions on NTFS drives, which OpenSSH rejects as insecure. 

You need to remove inherited permissions and restrict access exclusively to your Windows user account.   



Run the following commands directly in your current Command Prompt window (E:\\Pem Keys\\Shopsphere>):   



**1. Reset permissions and remove inheritance**



icacls "shopsphere-key.pem" /reset

icacls "shopsphere-key.pem" /inheritance:r



**2. Grant exclusive Read access to your Windows user**



icacls "shopsphere-key.pem" /grant:r "%USERNAME%:R"



**3. Connect again**



ssh -i shopsphere-key.pem ec2-user@13.126.223.191

