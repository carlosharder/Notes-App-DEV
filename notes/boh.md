---
title: +BoH
created: 2024-03-18T10:14:09
modified: 2024-08-21T17:26:56
---

[[I]]





![E273B74A-DFDA-4CDF-A210-A7E821B160DE](images/E273B74A-DFDA-4CDF-A210-A7E821B160DE.png)

[FinOps @ Bank of Hawaii | Opportunity | Salesforce](https://ibmsc.lightning.force.com/lightning/r/Opportunity/0063h00000MRZOoAAP/view)

[[VanceJones]]

#squad54 

[[< Turbonomic]]

<> Milestones
* Turbonomic Installed in environment

<> Key Actors
* Vance Jones, CTO.
* Mike Wu, VMware Admin
* Christine Hirano, VP of Infra

<> Metrics
?
?


<> Economic Buyer
* Vance Jones, CTO.

<> Decision Criteria
* Does it help with VMware migration

<> Decision - Process
* Mike and Christine will give recommendation to Vance

<> Paper process
* Vance does not need an Ok from the board

<> Pain
* Increase cost in VMware licensing 

<> Champion
* Vance……..if it works as promised
	
<> Competition

<> Critical Event

<> Use Case
* Ability to map a migration strategy
* Turbonomic not creating enough value



<> Risks
* Turbonomic not creating enough value









- [ ] Reach out to Folds



[19884F60-A1D3-4627-A944-72D39C1CF4DD](attachments/19884F60-A1D3-4627-A944-72D39C1CF4DD.mp4)





![B872AF74-42DA-442E-9D19-CD8E16BB5A90](images/B872AF74-42DA-442E-9D19-CD8E16BB5A90.png)



* Meeting with the CTO
* He wants to know the our POV on Cloud Migration
* They are 50% on the cloud (SaaS) but no workloads in on the Cloud
* Important for them to be Cloud Agnostic
* Cost reduction, due to economic challenges in Hawaii
* Broadcom Aquisition of VMware
* They are a very heavy VMware shop.
* Explain that we have aquired most of the FinOps and AIOPs leaders. We are not mainFrame
* BoH is in the middle of a dead-stage modernization and WKC (IBM knowledge Center)
* They were more or less succesfful with WKC.
* They have 2+ Data centers. It is unclear their locations


* Vance Jones, is the CTO.
* Cheryl Shozuya is the new boss for Mary Lee
* Torrie is moving to a new role
* Tood is meeting with Vance Jones next week.


Mary Lee Young, VP of Data and ETL 

Torrie Inouye, Chief Data Officer


Torrie is mo

——————————————
[Link to meeting notes about Broadcome acquisition use case.](applenotes:note/ba76319d-9989-4d4b-9ac6-3a111e8b50b3?ownerIdentifier=_dc281716ed0adf10c195661b79ef25d1)


https://otter.ai/u/Bsj3XoA9iK9E6RRHvIVC2rCAvS4?tab=chat
[24.01.31 QBR great data on key accounts - Otter.ai](https://otter.ai/u/Bsj3XoA9iK9E6RRHvIVC2rCAvS4?tab=chat)
Minute 11

Notes on QBR Q1 2023

Vijay Gupta 
* Has a deal in Q1. 
* Pitch them the Next Data sate SaaS Solution
* They have stand alone data stage
* Data State SaaS
* There is also amount data band in that deal
* Renewal of Manta
* Manta in now IBM. 
* He presented a proposal 
* Mary said we don’t have any money int he bank
* For the Data Stage he is using the business partner N-folds https://www.nfold.com/
* [Home – nFold](https://www.nfold.com/)



FSM
This was a specific conversation on the Turbonomic Development team. 
https://ec.yourlearning.ibm.com/w3/event/10406575
[Turbonomic Offering Team Call (Biweekly) • 10406575 • E&C (ibm.com)](https://ec.yourlearning.ibm.com/w3/event/10406575)


- Pouya Safa
- Sharon Cocco had info
- Jason Hamilton (asked the question)
- Thi 
- This use case needs to be studied. 







———————————————


AIOps+FinOps

* Key assumptions.
	* Workloads running on VMware in an on-prem environment.
	* The bank still has control over provisioning, placement actions.
	* Cloud infrestrucutre consist mainly of SaaS services, with a limited number of workloads direcly managed by the IT team.
	* Workloads mainly live in VM, not contererized inviroments.
	* There is a concern that either/or pricing and support challenges will emerge during the incorporation of VMware into Broadcom. (VMturbo)
	* APM (Application Performance Management)??
IBM's POV regarding Cloud Transformation


Interdisciplinary > App-Centered > Automation



Interdisciplinary
* During the last 3 year, IBM has acquired, developed and integrated technologies that transform IT from a cost to a profit center.
* What if we could map every IT resource (direct & indirect) to specific bottom line or top line achievements, to specify specific project, LOBs.
App-Centered
* Other platforms, such as VMware its family of solutions, do an amazing job providing performance, risk insights about specific parts of the infrastructure, such as VMs.
* What if in addition to having visibility at the VM or container level, we could map in real time the health of every resource, every interdependency that supports each application.
Automation
* Achieving and maintaining an interdisciplinary and App-centered is part of the foundation to drive a digital transformation.
* Thanks to automation it is possible these possible with achieve without a net increase in headcount.


How does this shape our perspective regarding Cloud Migration/Transformation


* We've reached the connclusing that a good first step is to Map, Measure, Visualize you existing infrastructure based on an App-Centered Interdisciplinary approach.

* Right now you have an X number of VMs Managed on-prem using a solution that gives you great risk and performance at the VM level.
* We see great value in mapping not only the VMs, but also the storage, network resources as much as possible in terms of specific applications.
* This automated mapping will give you data points to reach defensible conclusions as to where, how, when to move to the Cloud.
* Another good practices that we've seen with other clients is to organize an interdisciplinary FinOps, Cloud Cost Management or Cloud Center of Excellence team before the migration to the Cloud.
* I don't know if this obsession with interdisciplinary, app-centered approach part of the IBM culture was already.
* I do know that IBM AIOps+FinOps made up mainly of SaaS, CloudNative organizations, the App-centered, Interdisciplinary approach embedded in our organizational DNA.
* team






visibility but 





* We recommend to re-map you pre infrastructure in terms of applications.
				* Map Depencides, with the application at the top a supply chain or a Stack of the specific resources used by the application.
				* VMware does give you great insights the health of each VM.
				* What is a particular state does for the VM, but also what that does to the other VMs and just the ecosystem in general.
* This greater visibility in terms of interdependencies, performance.
				* Give you data points to reach defensible decisions of where, how, when to move to the Cloud.
* We are Cloud Agnostic.
				* The solution that creates the application dependency map, also can create in 10 minutes, a forcast of what it would cost to relcoate a specific set of VM from onprem to Google, Amazon or Azure.

* **Automatic to Autonomic**
* **My goal was to give you the highlights and then have a conversation about about the areas that you want.**

		* The VMware solutions does provide amazing reports, but they are VM specific.
				* The questions that VMware solutions ask about the behivior of the VM
		* Allow the system to quantify and map optimization opportunities.
				* Review feasibility of these optimizations.
		* With a greater understanding of application dependencies, you team can decide what the next environment should look like.
Beware of Lift and 
* AIOps+FinOps













Combine the power of AIOPs and FinOps to assure application performance at the most optimal cost. 

Everything is application centered. 










![3FBE9883-FBCE-4205-807E-61C7A43B8269](images/3FBE9883-FBCE-4205-807E-61C7A43B8269.png)

|                                                                        | Contacts                                                               |                                                                        |                                                                        |                                                                        |
|------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------|
| Wes Kurakake                                                           | Bank of Hawaii                                                         | VP, Network Administration                                             | wesley.kurakake@boh.com                                                | 808-694-5211                                                           |
| Robin Stoddard                                                         | Bank of Hawaii                                                         | Information Systems Architect                                          | rstoddard@boh.com                                                      | 808-694-4531                                                           |
| Thinzar Nyun                                                           | Bank of Hawaii                                                         | Business Intelligence Analyst                                          | thinzar.nyun@boh.com                                                   | (888) 643-3888                                                         |
| Sheri Matsuda                                                          | Bank of Hawaii                                                         | Project Manager                                                        | sheri.matsuda@boh.com                                                  | (888) 643-3888                                                         |
| David Li                                                               | Bank of Hawaii                                                         | Audit Consultant                                                       | dli@boh.com                                                            | (888) 643-3888                                                         |
| Joe Tham                                                               | Bank of Hawaii                                                         | Senior System Consultant                                               | joe.tham@boh.com                                                       | (808) 848-5802                                                         |
| Charles Buxmann Jr                                                     | Bank of Hawaii                                                         | AVP                                                                    | cbuxmann@boh.com                                                       | (808) 694-5707                                                         |
| Heather Thomas                                                         | Bank of Hawaii                                                         | Manager - IT Infrastructure and Cloud Operations                       | hthomas@boh.com                                                        | (808) 694-4899                                                         |
| Glen Edelo                                                             | Bank of Hawaii                                                         | Senior System Consultant                                               | gleno.edelo@boh.com                                                    | (808) 538-4171                                                         |
|                                                                        |                                                                        | LEADS                                                                  |                                                                        |                                                                        |
| Agatha Viernes-LeGros                                                  | Vice President                                                         | Bank of Hawaii                                                         | agatha.viernes@boh.com                                                 | (808) 694-8343                                                         |
| Alessa Stecher                                                         | Senior Applications IT Administrator                                   | Bank of Hawaii                                                         | alessa.stecher@boh.com                                                 | (808) 537-8580                                                         |
| Alexander Easley                                                       | Application Administrator                                              | Bank of Hawaii                                                         | alexander.easley@boh.com                                               | (808) 537-8580                                                         |
| asd asd                                                                | Tecnico                                                                | Bank of Hawaii                                                         | asd@boh.com                                                            |                                                                        |
| Barryn Chun                                                            | Manager, Process & Information Technology Change Management            | Bank of Hawaii                                                         | barryn.chun@boh.com                                                    | (808) 643-3888                                                         |
| Brendon Lee                                                            | Systems Analyst                                                        | Bank of Hawaii                                                         | brendon.lee@boh.com                                                    | (808) 694-4615                                                         |
| Chad Yoshino                                                           | Vice President, Corporate Comm                                         | Bank of Hawaii                                                         | cyoshino@boh.com                                                       | (808) 694-5877                                                         |
| Chris Glavin                                                           | Servicing Systems                                                      | Bank of Hawaii                                                         | christopher.glavin@boh.com                                             | (808) 694-5658                                                         |
| Christine Hirano                                                       | Manager, IT Server Administration                                      | Bank of Hawaii                                                         | christine.hirano@boh.com                                               | (808) 694-5201                                                         |
| Claire Shimizu                                                         |                                                                        | Bank of Hawaii                                                         | claire.shimizu@boh.com                                                 | +1 888-643-3888                                                        |
| Craig Ito                                                              | VP, Hawaii Dealer Indirect Lending Manager                             | Bank of Hawaii                                                         | craig.ito@boh.com                                                      | +1 888-643-3888                                                        |
| D. Graves                                                              | EVP, Chief Technology Officer                                          | Bank of Hawaii                                                         | d.graves@boh.com                                                       |                                                                        |
| D. Jeff Graves                                                         | EVP, Chief Technology Officer                                          | Bank of Hawaii                                                         | djeff.graves@boh.com                                                   | (808) 537-8580                                                         |
| David Higgins                                                          | Architect IT Content & Collaboration                                   | Bank of Hawaii                                                         | david.higgins@boh.com                                                  | (808) 643-3888                                                         |
| Forrest Dell                                                           | Automation Vice President, Data & Manager, Reporting Data Governance   | Bank of Hawaii Corporation                                             | forrest.dell@boh.com                                                   | (808) 694-8613                                                         |
| Fran Taba                                                              | SVP Trust Operations Administration                                    | Bank of Hawaii                                                         | fran.taba@boh.com                                                      | +1 888-643-3888                                                        |
| Guy Davison                                                            | Shared Systems Applications Administrator                              | Bank of Hawaii                                                         | guy.davison@boh.com                                                    | (808) 694-5267                                                         |
| Heather Thomas                                                         | IT Infrastructure Application Services Manager                         | Bank of Hawaii                                                         | heaher.thomas@boh.com                                                  | +1.808.973.4440                                                        |
| Heather Thomas                                                         | Manager, IT infrastructure Application Services                        | Bank of Hawaii                                                         | heather.thomas@boh.com                                                 | (808) 643-3888                                                         |
| Janna Sye                                                              | VP, Commercial Banking Systems, Data & Analytics Manager               | Bank of Hawaii                                                         | janna.sye@boh.com                                                      | +1 888-643-3888                                                        |
| Jason Mecham                                                           | Director, IT Service Management                                        | Bank of Hawaii                                                         | jason.mecham@boh.com                                                   | (808) 694-5667                                                         |
| Jeff Graves                                                            | EVP, Chief Technology Officer                                          | Bank of Hawaii                                                         | jeff.graves@boh.com                                                    | +1.808.973.4440                                                        |
| Jennifer Kuon                                                          | Fraud Manager                                                          | Bank of Hawaii                                                         | jennifer.kuon@boh.com                                                  | +1 888-643-3888                                                        |
| Jessica Perkins                                                        | Vice President, Enterprise Application Management                      | Bank of Hawaii                                                         | jessica.perkins@boh.com                                                | (808) 643-3888                                                         |
| John Werverd                                                           | Vice President, Information Technology                                 | Bank of Hawaii                                                         | vence.jonce@boh.com                                                    | (808) 643-3888                                                         |
| Jose Lopez                                                             | Manager, Technical Support                                             | Bank of Hawaii Corporation                                             | jose.lopez@boh.com                                                     | 808-694-5872                                                           |
| Joseph Francher                                                        |                                                                        | Bank of Hawaii                                                         | joseph.francher@boh.com                                                | +1 888-643-3888                                                        |
| Julie Yu                                                               | Manager, Treasury Systems                                              | Bank of Hawaii                                                         | julie.yu@boh.com                                                       | (808) 694-8347                                                         |
| Justin Ankeny                                                          | Vice President of Information Technology Service Management            | Bank of Hawaii                                                         | justin.ankeny@boh.com                                                  | (808) 643-3888                                                         |
| Kevin Byrne                                                            | Vice President, ECM Business Applications                              | Bank of Hawaii                                                         | kevin.byrne@boh.com                                                    | (808) 694-5665                                                         |
| Kim Morrissey                                                          | Operations IT Manager, Digital Channels                                | Bank of Hawaii                                                         | kim.morrissey@boh.com                                                  | (808) 537-8580                                                         |
| Linda Bernal                                                           | VP Loan and Deposit Operations                                         | Bank of Hawaii                                                         | linda.bernal@boh.com                                                   | +1 888-643-3888                                                        |
| Lori Nishino                                                           | Manager, IT Application Development                                    | Bank of Hawaii                                                         | lnishino@boh.com                                                       | (808) 693-1520                                                         |
| Lynette Sakamoto                                                       | VP, Systems Manager                                                    | Bank of Hawaii                                                         | lynette.sakamoto@boh.com                                               | (808) 694-4248                                                         |
| Marc Partoriza                                                         | EAM Shared Systems                                                     | Bank of Hawaii                                                         | marc.partoriza@boh.com                                                 |                                                                        |
| Matthew Mizumoto                                                       | Developer Analyst                                                      | Bank of Hawaii                                                         | matthew.mizumoto@boh.com                                               | (808) 694-5913                                                         |
| Michael Lotter                                                         | Technician IT Infrastructure Operations                                | Bank of Hawaii                                                         | michael.lotter@boh.com                                                 | (808) 537-8440                                                         |
| Michael Taylor                                                         | Executive Vice President & Manager, Corporate Real Estate & Facilities | Bank of Hawaii                                                         | michael.taylor@boh.com                                                 | (808) 694-8925                                                         |
| Michael Wu                                                             | Senior Systems Analyst                                                 | Bank of Hawaii                                                         | michael.wu@boh.com                                                     | (808) 694-5256                                                         |
| Neal Akamine                                                           | Vice President, Information Systems                                    | Bank of Hawaii                                                         | neal.akamine@boh.com                                                   | (808) 694-4316                                                         |
| Nichole Shimamoto                                                      | Senior VP & Deputy Chief Compliance Officer                            | Bank of Hawaii                                                         | nichole.shimamoto@boh.com                                              | (808) 694-4057                                                         |
| Preston Robler                                                         | Vice President                                                         | Bank of Hawaii                                                         | preston.robler@boh.com                                                 | (808) 537-8580                                                         |
| Randy Jose                                                             | Assistant Vice President & IT Architect                                | Bank of Hawaii                                                         | randy.jose@boh.com                                                     | (808) 694-5673                                                         |
| Robert Baker                                                           | System Engineer                                                        | Bank of Hawaii                                                         | robert.baker@boh.com                                                   | (808) 694-5390                                                         |
| Robyn Wolfe                                                            | Vice President, Director Enterprise Quality Assurance Governance       | Bank of Hawaii                                                         | robyn.wolfe@boh.com                                                    | (808) 694-5120                                                         |
| Ross Yonamine                                                          | VICE President, Information Technology Audit                           | Bank of Hawaii                                                         | ross.yonamine@boh.com                                                  | (808) 643-3888                                                         |
| Shahed Rahim                                                           | Manager, Applications                                                  | Bank of Hawaii                                                         | shahed.rahim@boh.com                                                   | (808) 694-5925                                                         |
| Sheh Bertram                                                           | IT Director, Application Development                                   | Bank of Hawaii Corporation                                             | sheh.bertram@boh.com                                                   | (801) 844-7637                                                         |
| Stephen Pang                                                           | Senior Director, Global Information Technology Network                 | Bank of Hawaii                                                         | spang@boh.com                                                          | (808) 694-5301                                                         |
| Steve Araki                                                            | Manager, Infrastructure & Server                                       | Bank of Hawaii                                                         | steve.araki@boh.com                                                    | (808) 694-5775                                                         |
| Steve Tiet                                                             | Information Technology Executive                                       | Bank of Hawaii                                                         | steve.tiet@boh.com                                                     | (808) 694-4977                                                         |
| T.J. Breshears                                                         | Administrator IT Applications                                          | Bank of Hawaii                                                         | tj.breshears@boh.com                                                   | (808) 537-8580                                                         |
| Taryn Salmon                                                           | Executive Vice President                                               | Bank of Hawaii                                                         | taryn.salmon@boh.com                                                   | (808) 694-5430                                                         |
| Todd Lemson                                                            | Information Technology Executive                                       | Bank of Hawaii                                                         | todd.lemson@boh.com                                                    | (808) 643-3888                                                         |
| Tyler Hunt                                                             | Administrator of IT Applications                                       | Bank of Hawaii                                                         | tyler.hunt@boh.com                                                     | (808) 643-3888                                                         |
| Vico Chang                                                             | Manager, Information Technology                                        | Bank of Hawaii                                                         | vico.chang@boh.com                                                     | (808) 694-5655                                                         |
| Wes Kurakake                                                           | VP, Network Administration                                             | Bank of Hawaii Corporation                                             | wes.kurakake@boh.com                                                   | (808) 694-5211                                                         |
| Wesley Ramos                                                           | Domain Architect - Network                                             | Bank of Hawaii                                                         | wesley.ramos@boh.com                                                   | +1.808.973.4440                                                        |
| William Digiorgio                                                      |                                                                        | Bank of Hawaii                                                         | william.digiorgio@boh.com                                              | +1 888-643-3888                                                        |
| Winston Sun                                                            | Database Administrator                                                 | Bank of Hawaii                                                         | wsun@boh.com                                                           | (808) 684-5865                                                         |