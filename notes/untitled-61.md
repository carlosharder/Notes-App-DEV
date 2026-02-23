---
title: ---
created: 2024-07-01T09:42:35
modified: 2024-07-02T07:05:51
---

---
title: 2024 IBM - Farmers
creation_date: July 1, 2024
modification_date: July 2, 2024
---





Most of the on-premise machines are
 
model name      : Intel(R) Xeon(R) Gold 5320 CPU @ 2.20GHz
[Intel® Xeon® Gold 5320 Processor](https://www.intel.com/content/www/us/en/products/sku/215285/intel-xeon-gold-5320-processor-39m-cache-2-20-ghz/specifications.html)



 
the AWS EC2’s are r6i.xlarge, r6i.2xlarge, r6i.4xlarge etc
[Amazon EC2 R6i Instances – Compute –Amazon Web Services](https://aws.amazon.com/ec2/instance-types/r6i/)





We need a bit more help understanding how this deployment will be/is architected.
**For example: Will you be managing from Z to distributed or will it be architect so that it is managed from distributed to Z (with the master fully on distributed)?**


Thanks for your email. The deployment will be 100% on distributed env.IBM Z is out of scope for this licensing/installation.







••••••••••••••••••


* If they have their DR set up Active Active, then it needs to be licensed as well. 
* Wherever the Master runs, if it is not on Z, it needs be licensed. 
* He has not seen any of the pricing for the AWS stuff. 



![A50AE67F-C01A-44DB-995F-EC9E3E11D81A](images/A50AE67F-C01A-44DB-995F-EC9E3E11D81A.png)


![085E45B0-66E3-4720-B211-87FF740A7A7E](images/085E45B0-66E3-4720-B211-87FF740A7A7E.png)
••••••••••••••••••••








![3C2DC558-80A1-4953-B64C-1B73162BD007](images/3C2DC558-80A1-4953-B64C-1B73162BD007.png)

![8DDDD451-981E-46D0-B5F9-A10A8106E791](images/8DDDD451-981E-46D0-B5F9-A10A8106E791.png)
https://fastpass.w3cloud.ibm.com/sales/fastpass/page/EntitlemtSalesTransForPart?cust_num=0007105273&part_num=D56MTLL&sap_ctrct_num=0000073102&fromSubstitution=No&program=PA&cust_type=NAV
[FastPass | Entitlements - All sales transactions for site and part (ibm.com)](https://fastpass.w3cloud.ibm.com/sales/fastpass/page/EntitlemtSalesTransForPart?cust_num=0007105273&part_num=D56MTLL&sap_ctrct_num=0000073102&fromSubstitution=No&program=PA&cust_type=NAV)



that would be Anant Bharadwaj ... and he is the guy i would engage first
 
David Munson
[anantb@hcl-software.com](mailto:anantb@hcl-software.com)





![E64340E0-AED0-41DF-9B7A-4EDA2422138B](images/E64340E0-AED0-41DF-9B7A-4EDA2422138B.png)


[93B69977-DBF3-4E9F-901A-54EDD3472AFD](attachments/93B69977-DBF3-4E9F-901A-54EDD3472AFD.PDF)



[6FAF3F33-3812-41EF-A21E-6199BAE8B17E](attachments/6FAF3F33-3812-41EF-A21E-6199BAE8B17E.PDF)