---
title: ---
created: 2024-06-13T12:08:01
modified: 2024-06-13T12:08:04
---

---
title: •••••••••••••••••••••••••••••
creation_date: June 13, 2024
modification_date: June 13, 2024
---

# 


•••••••••••••••••••••••••••••
06.11 Tuesday
 
**Steps to systematically enable Dynamic Scaling in 5VMs in Non-Prod**
              

[A] Update role/right of Azure account connected to Turbo
      •  Rama to add two (2) azure access managers to the 06.13 call
                                                                       
[B] In the Turbo console, Adjust rules that delimit the automations
      • Use Tags to create a group
      • Special rules will be created for this group
      • Rules that will protect SLAs
      • Add Cool-off period 
 
[C] Select 5 VM candidates (Vina and Rama)
      • Non-Prod
      • Non-Crown Jewel workload
      • With up/down changes in resource requirements
      • From 5 different Applications
      • Can be disrupted outside of the patching window
      • Being monitored by AppDynamics (Allows to document performance changes)
      • Has a quick reboot time
      • Some candidate VMs could also be Dynamically scale during the day, some only during the night




•••••••••••••••••••••••••••••
05.27 - 06.07

**Non-Prod**

      **• Dynamic Automations** 
            - 5 VMs in the Non-Prod environment
            **- Rama to select 5 good candidates**
            **- Akash to add Dynamic Sizing to the internal PPT**
            - VMs monitored by AppDynamics
            - Staggering PCM & Sizing dynamic Automations 
            - Enabling both, performance and optimization actions
            - Time specific rules can be set up for the Automations 
            - The trial could also be expanded to manage Volume
            - Check for Dev/Test permissions in the Azure account
            - Sizing is just an API in Azure
            - [IBM Documentation](https://www.ibm.com/docs/en/tarm/8.12.4?topic=infrastructure-virtual-machine-cloud)
            - We can set up additional weekly meetings
            - Once automations are enabled, it will feed Reporting
            - AppDynamics has coverage in Prod and non-Prod?
            - Is there a Savings report that needs to be enabled?