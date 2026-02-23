---
title: ---
created: 2024-05-16T10:05:11
modified: 2025-01-16T18:42:30
---

---
title: IBM Concert
creation_date: May 16, 2024
modification_date: January 16, 2025
---

[[DEV-tech]]


![5CF5FC26-6467-4FA0-96D1-EC7F516821B7](images/5CF5FC26-6467-4FA0-96D1-EC7F516821B7.png)



![BEF9F74F-CED3-4078-8D59-5102572C582A](images/BEF9F74F-CED3-4078-8D59-5102572C582A.png)
from Ashok Gunnia (internal) to Everyone:    9:34  AM
Great initiative to add to IT Automation. Wondering about the naming convention 'Concert'. Band orchestration thought?
from Kay Groski (internal) to Everyone:    9:35  AM
we used to have IBM Rational Concert, just a little confusing 
from Jonathan Fairhurst (internal) to Everyone:    9:35  AM
and before that Lotus Symphony...there is a theme it seems
from Włodzimierz Dymaczewski (internal) to Everyone:    9:36  AM
It was Rational Team Concert
from WILLIAM Lobig to Everyone:    9:36  AM
when you understand what it is it will not be confusing. it's not a developer tool. 
from Chris Rudiman (internal) to Everyone:    9:37  AM
Complementary to Cloud Pak for AIOps I assume?
from HANI BANDI (internal) to Everyone:    9:39  AM
Does App 360 look at network metrics as part of application performance?
from Ashok Gunnia (internal) to Everyone:    9:41  AM
I think it fetches everything via API and stores / analyses in a flow on top of ML for stored data. Catch all similar to AIOps but with GenAI. It seems like it.
from Chris Rudiman (internal) to Everyone:    9:41  AM
How does this relate (or not) to IBM Cloud Pak for AIOps (hybrid deployment with on-prem Netcool)?
from Ashok Gunnia (internal) to Everyone:    9:43  AM
I like the CVEs and cert use case. That is whast causes outages...
from Jonathan Fairhurst (internal) to Everyone:    9:43  AM
Doesn't Turbo have a common data model allowing you to connect to multiple data sources like Instana , Datadog etc? 
from Vivek Singh (internal) to Everyone:    9:43  AM
This is really cool , Specially related to CVE's . App 360 will it be available as SaaS ?
from Lars Michelem (internal) to Everyone:    9:44  AM
what is CVE?
from Ashok Gunnia (internal) to Everyone:    9:44  AM
CVE - [https://cve.mitre.org/](https://cve.mitre.org/)
from Jason Shamroski (internal) to Everyone:    9:44  AM
[https://cve.mitre.org/](https://cve.mitre.org/)
from Vivek Singh (internal) to Everyone:    9:44  AM
Common Vulnerabilities and Exposure
from HANI BANDI (internal) to Everyone:    9:44  AM
NIST requires discovey data and compare to config for compliance .. how are you doing that?
from Sharon Cocco (internal) to Everyone:    9:44  AM
CVE= Common vulnerabilities and exposures
from Sharon Cocco (internal) to Everyone:    9:44  AM
so think security vulnerabilities
from Matthew Barto (internal) to Everyone:    9:45  AM
This is like Turbo's Supply Chain, but looks less detailed
from DAVID SONG (internal) to Everyone:    9:46  AM
where does it receive CVE from? (e.g., Websphere automation)
from Vivek Singh (internal) to Everyone:    9:46  AM
First question comes to my mind is how it is different from EDR,XDRs. If we are talking about vulnerabilties 
from Barry Howard (internal) to Everyone:    9:46  AM
What is the order/schedule for this connecting to current IBM products like Turbo, Instana, Apptio, etc.
from HANI BANDI (internal) to Everyone:    9:46  AM
Is App 360 able to create a line of business view?
from Veer (internal) to Everyone:    9:46  AM
@David song .. May be from code scanners?
from WILLIAM Lobig to Everyone:    9:46  AM
basically the idea is this. NIST is the body taht scores CVEs with what's called a CVSS score. This determines the severity but it does not take into account any applicatoin or evironmental considerations like proximity to attach surface area, is customer data exposed or not, is the vunerability even used in the code path, how is it used? how important or critical I sthe appliaction it's used in?
from WILLIAM Lobig to Everyone:    9:46  AM
[https://nvd.nist.gov/vuln](https://nvd.nist.gov/vuln)
from WILLIAM Lobig to Everyone:    9:46  AM
we take all that into account and help developers and security focals focus on what's most important in their IT/env/app context
from WILLIAM Lobig to Everyone:    9:47  AM
CVEs are published by NIST. code scanners detect if you have them
from Veer (internal) to Everyone:    9:47  AM
ok
from WILLIAM Lobig to Everyone:    9:47  AM
we do all the other risk factors I mention to give you a more prioritized and optimized view
from Sridhar Iyengar (internal) to Everyone:    9:47  AM
who is that target buyer for this tool - CISO ? CIO and App Dev teams?
from Darren Cacy (internal) to Everyone:    9:47  AM
@Bill this would be so helpful. Right now muy customer just sees that there's a CVE for the library we are using and they call it out...without anyone knowing if our code actually uses that component.
from WILLIAM Lobig to Everyone:    9:47  AM
app dev, SRE, Devops, IT managers/directors
from WILLIAM Lobig to Everyone:    9:48  AM
CISO will care
from Ashok Gunnia (internal) to Everyone:    9:48  AM
In case you missed the announcement on Infosec from IBM - [https://www.msn.com/en-us/money/other/ibm-and-palo-alto-networks-are-joining-forces-on-ai-as-cybersecurity-threats-get-tougher/ar-BB1msCnU](https://www.msn.com/en-us/money/other/ibm-and-palo-alto-networks-are-joining-forces-on-ai-as-cybersecurity-threats-get-tougher/ar-BB1msCnU)
from WILLIAM Lobig to Everyone:    9:48  AM
but dev/product teams are the ones resonsibel for finding and fixing these things
from Ashok Gunnia (internal) to Everyone:    9:48  AM
I think Palo Alto would connect to concert as well.
from WILLIAM Lobig to Everyone:    9:49  AM
@darren exactly. a jar file may be marked vunerabile but it has 15 apis only 1 of which is vunerable and your app doesn't use that api so you are safe
from HANI BANDI (internal) to Everyone:    9:49  AM
@Bill how are we accounting for network metrics, network cve's, config divation policies for risk mgmt?
from Sridhar Iyengar (internal) to Everyone:    9:49  AM
CISO threat management teams would block apps with CVEs that are high risk
from WILLIAM Lobig to Everyone:    9:49  AM
but in traditional methods you need to fix it anyway and you are considered exposed
from Nicholas Power (internal) to Everyone:    9:49  AM
Does the WatsonX specialist get credit for this product?
from WILLIAM Lobig to Everyone:    9:49  AM
@hani not considred yet but this is good input @coffey fyi...
from Ashok Gunnia (internal) to Everyone:    9:49  AM
How is the integration with ServiceNow scoped? all of this usually spoken inside ServiceNow, IMO.
from Debasish Banerjee (internal) to Everyone:    9:49  AM
Will the Watsonx run in clinet environment or Concert of a client will connect to Watsonx running in cloud?
from Sridhar Iyengar (internal) to Everyone:    9:50  AM
the testing tools need to be aware of errors/alerts from SIEM products like QRadar or Palo Alto CORTEX 
from Anthony Singh (internal) to Everyone:    9:50  AM
Looking good so far, I think it's been asked above but would be great to see integration with other offerings in the IT Aut portfolio to paint the holistic picture
from BALASUBRAMANIAN SIVASUBRAMANIAN (internal) to Everyone:    9:50  AM
Can this run on customer owned facility or depends Cloud ?
from DAVID SONG (internal) to Everyone:    9:50  AM
The CVE portion of this tool looks like overlapping with WSA for websphere apps.  
from WILLIAM Lobig to Everyone:    9:50  AM
@sridhar, this is an area I can see synergy with instana being valuable in the future
from Madelyn Forrester (internal) to Everyone:    9:50  AM
How can you tell "where" these CVEs are - are they on some of the images? are the CVEs in the repos? 
from Barry Howard (internal) to Everyone:    9:50  AM
What product/data sources was this demo built from?
from HANI BANDI (internal) to Everyone:    9:50  AM
Please don't think APPS.. think LOB
from Sharon Cocco (internal) to Everyone:    9:50  AM
David- think broader than WebSphere ;-)
from Stefan Kwiatkowski (internal) to Everyone:    9:50  AM
cannot Turbo integrate with Aptio as well to show how costs can be reduced 
from Angela Molinari (internal) to Everyone:    9:50  AM
How IBM Concert will be integrated (in case) with current AIOps features?
from WILLIAM Lobig to Everyone:    9:50  AM
it can IP block/deny apps in runtime if it knows CVEs are in the stack it monitors
from MARIBETH KINNAVY (internal) to Everyone:    9:50  AM
Looks like something that should be added to CP4Apps as it is centered around apps and vulnerabities.  Now we will have 4 reps calling on same folks with differing goals/messages?
from HANI BANDI (internal) to Everyone:    9:51  AM
Are you planning SevOne integration?
from WILLIAM Lobig to Everyone:    9:51  AM
@stefan yes that is available today
from Eduardo Ortega (internal) to Everyone:    9:51  AM
what does it do on the automation lense?
from Sridhar Iyengar (internal) to Everyone:    9:51  AM
@bill - yes on Instana - Also Guardium
from WILLIAM Lobig to Everyone:    9:51  AM
and we will package it as cloudabilty premium launcing next week
from Nicholas Power (internal) to Everyone:    9:52  AM
will the watsonx specialist be comped on this product?
from WILLIAM Lobig to Everyone:    9:52  AM
I don't know. I don't think so. need labros to comment. automation brand sellers will sell it. 
from Sridhar Iyengar (internal) to Everyone:    9:52  AM
@bill and potential for integration with Red Hat advanced Cluster Security - part of OpenShift Platform Plus for vulnerabilities at the container level for microservies apps
from KAUSHIK MUKHERJEE (internal) to Everyone:    9:52  AM
Is all the data shown through the Concert UI accessible through API's?
from Piero Proietti (internal) to Everyone:    9:52  AM
I would think IBM Concert in the Security portfolio
from WILLIAM Lobig to Everyone:    9:52  AM
agree on OCP but to be frank I have seen little success co-selling there due to the incentive models across RH and IBM
from Ashok Gunnia (internal) to Everyone:    9:53  AM
Interesting to include with Cloudability Premium SaaS. Just wondering if the customer will get two separate SaaS product or one with integration in UI. Will it?
from Sridhar Iyengar (internal) to Everyone:    9:53  AM
some of he coselling issues fixed in CP4Apps 
from JENNIFER FITZGERALD (internal) to Everyone:    9:53  AM
Piero, just remember these are the first use cases -- we'll go beyond risk & compliance in the future 
from MARIBETH KINNAVY (internal) to Everyone:    9:53  AM
2nd use case here is also what we sell with Noname API Security (App Mod sller)
from WILLIAM Lobig to Everyone:    9:53  AM
it will be turbo features for SaaS in cloudability premium edition. single sign on for now and over time we make the UIs more integraetd. there is some integration today
from Imran Paniwala (internal) to Everyone:    9:53  AM
Will this be able to feed information back to Cloud Pak for AIOps so you can integrate the risk or compliance information along with other data for the application / business?
from Angela Molinari (internal) to Everyone:    9:54  AM
With IBM Concert we'll finally be able to provide to customer an overview pointing to Services provided by Lobs (that is currently non easy to address in AIOps)? Multi-domain stiching events etc? 
from Saurabh Jha (internal) to Everyone:    9:54  AM
Is the core technology here the ability to correlate data across it products such as instana turbo etc and use ai planning to provide insights and actions? Or is it just another umbrella wrapper across our existing products ? 
from Jeff Babler (internal) to Everyone:    9:54  AM
Curious to learn when this will be integrated with Quantum Safe (CBOM) Application Certificate Management...
from WILLIAM Lobig to Everyone:    9:54  AM
there is a lot of enablement on this. conteact @marisa bannigan if you missed it. I suspect hthere are replays
from Meenu Patil (internal) to Everyone:    9:54  AM
would customers get a trail version with cloudability premium SaaS for 2 weeks? 
from HANI BANDI (internal) to Everyone:    9:54  AM
Agreed OCP ACM and Hashi Vault
from HANI BANDI (internal) to Everyone:    9:54  AM
For key mgmt
from SINEAD GLYNN (internal) to Everyone:    9:54  AM
Will IBM be Client 0 for this solution?
from Ashok Gunnia (internal) to Everyone:    9:54  AM
@ Piero, Cert expiration alert and other risks in IT a scope for security portfolio? 
from Sridhar Iyengar (internal) to Everyone:    9:54  AM
Note NoName security about to be acquired by Akamai 
from Eduardo Ortega (internal) to Everyone:    9:54  AM
can you disclose some info about the Automation roadmap? what is the use cas for that?
from ROHAN ARORA (internal) to Everyone:    9:54  AM
Did we get a chance to dogfood this with our very own SREs?
from WILLIAM Lobig to Everyone:    9:55  AM
@saurabh it's the former 
from Sridhar Iyengar (internal) to Everyone:    9:55  AM
not sure what this does to our OEM relationship
from Paige Jewett (internal) to Everyone:    9:55  AM
more info on cloudy premium in an hour: [https://ec.yourlearning.ibm.com/w3/event/10436038](https://ec.yourlearning.ibm.com/w3/event/10436038)
from WILLIAM Lobig to Everyone:    9:55  AM
@sinead yes. Priya's SRE team and CIO
from SINEAD GLYNN (internal) to Everyone:    9:55  AM
AFAIK - it's looks like a GenAI layer on top of the standard ops tools to make day 2 ops better. i.e a step towards zero touch ops
from SINEAD GLYNN (internal) to Everyone:    9:55  AM
thanks Bill!
from HANI BANDI (internal) to Everyone:    9:56  AM
@bill who's the customer that you are targeting with this solution? 
from Ashok Gunnia (internal) to Everyone:    9:56  AM
@Paige Thx on the premium annoucement with GenAI.
from HANI BANDI (internal) to Everyone:    9:56  AM
Is this a Security, App mgmt, or compliance solution?
from Angela Molinari (internal) to Everyone:    9:57  AM
IBM concert seams concentrated to application... customer is still looking about integrated view (topology and so on) including app and network ... info about that? net will be out of scopo of IBM Concert? AIOps still alive for that? Integration, overlapping features .... how to use, how to propose to no 0 client that is spending time and effort in AIOps? thanks a lot
from TOM MERCER (internal) to Everyone:    9:57  AM
Are we able to target SSLs in General or just Application Certificates? Infrastructure Certs are equally important. 
from SINEAD GLYNN (internal) to Everyone:    9:57  AM
Hani - it look like a day 2 ops GenAI tool (but Product Management shoudl confirm)
from WILLIAM Lobig to Everyone:    9:57  AM
initially it's app, sre, devops, IT ops teams who need risk mitigation tech. over time this will be the fabric that unifies IBM's 3rd platform. The TEch automation platform
from BILL Headlee (internal) to Everyone:    9:57  AM
Since we are integrating to git to create tickets, will we have ServiceNow integration as well? Jira?
from WILLIAM Lobig to Everyone:    9:57  AM
Rob alluded to it in his monday growth message few weeks ago. 
from WILLIAM Lobig to Everyone:    9:57  AM
didn't allude to concert but the automation platform. this is a key part to that
from Madelyn Forrester (internal) to Everyone:    9:58  AM
Have we found a need that SRE teams are responsible for identifying CVEs? Wouldnt this normally fall to security or app team? 
from WILLIAM Lobig to Everyone:    9:58  AM
@bill yes SNOW and Jira. I saw those in the dev demo this week but greyed out. they will come
from Nicholas Power (internal) to Everyone:    9:58  AM
who can demo this as our tech sellers get ramped up
from TOM MERCER (internal) to Everyone:    9:58  AM
@Bill Headlee - On the Arch Interlock call today, Catherine Cook introduced Jira for Incident Gener. Its coming
from Islam Elbanna (internal) to Everyone:    9:59  AM
how this is related to ROJA, is it the same thing?
from Ashok Gunnia (internal) to Everyone:    9:59  AM
@Tom, i think App cwert is SSL. It is tied to an application here. It will scope all visibile certs. Also , there is a miss on the management tools for certs like venifi........................
from Sridhar Iyengar (internal) to Everyone:    9:59  AM
Who is client ZERO ? Has our CIOs office trying it
from Ben Ball (internal) to Everyone:    9:59  AM
Roja = Concert
from WILLIAM Lobig to Everyone:    9:59  AM
Roja was code name. Concert is product name. it's the same
from Islam Elbanna (internal) to Everyone:    10:00  AM
thanks william
from Ashok Gunnia (internal) to Everyone:    10:01  AM
Nope @Madelyn...It is 100% incident management / NOC / SRE/ Devops for fire fighting an outage...
from Chris Rudiman (internal) to Everyone:    10:01  AM
I assume it's installable on-prem?
from Eduardo Ortega (internal) to Everyone:    10:02  AM
are. we launching GA with all the lenses/use cases available? 
from Jeff Babler (internal) to Everyone:    10:02  AM
Will this become part of IBM Security Brand or stay as part of IT Automation's Cadre?  Seems more CyberSecurity centric to me... (e.g., CVE's)
from Ben Ball (internal) to Everyone:    10:02  AM
Risk and compliance lenses will be available at GA.  More to come after that.
from JENNIFER FITZGERALD (internal) to Everyone:    10:02  AM
at GA, we will have risk & compliance use cases... more to quickly come
from LAMPROS KISOURAS (internal) to Everyone:    10:02  AM
Its the next gen autmation unifyingg platform for SRE automation 
from Barry Howard (internal) to Everyone:    10:03  AM
For data, will this only connect directly to IBM products or directly to third party tools as well. e.g. Turbo pulls data from lots of sources, would this connect to just Turbo for those data sources or have direct capability too?
from Lars Michelem (internal) to Everyone:    10:03  AM
who are the 9 clients?
from Nicholas Power (internal) to Everyone:    10:03  AM
are we allowed to show a demo before GA?
from LAMPROS KISOURAS (internal) to Everyone:    10:03  AM
there many more use cases over and above CVE / Security that will be coming
from Ashok Gunnia (internal) to Everyone:    10:03  AM
I believe it is AIOps 2.0 with GenAI. so IT Automation portfolio from the 1st look.
from ROHAN ARORA (internal) to Everyone:    10:03  AM
Have the client's SRE teams been a part of a alpha/beta or just the design / use-case discussions?
from Eduardo Ortega (internal) to Everyone:    10:03  AM
do you allow any internal volunteers for product testing, similarly as we did with WatsonX?
from Darren Cacy (internal) to Everyone:    10:03  AM
@Ashok agreed but with extra goodies like compliance.
from HANI BANDI (internal) to Everyone:    10:04  AM
Are the target customers - Security, SRE, DevOps? 
from Aarti Cherian (internal) to Everyone:    10:04  AM
Please promote the Think flyer with clients/partners - it includes Concrt sessions, and also other IT Automation sessions (Instana, Turbo, etc.)
from Trevor Firgau (internal) to Everyone:    10:04  AM
Very exciting!
from ZDENĚK BORŮVKA (internal) to Everyone:    10:05  AM
Is this deck available to share?
from Ingo Boelke (internal) to Everyone:    10:05  AM
@Dhuha: Can you share the links to the ama session, q6a, etc
from Eduardo Ortega (internal) to Everyone:    10:05  AM
can you share the AMA-EMEA session link for tomorrow?
from Dhuha Qazi (internal) to Everyone:    10:05  AM
Concert AMA (EMEA) 
- [https://ec.yourlearning.ibm.com/w3/event/10440466](https://ec.yourlearning.ibm.com/w3/event/10440466)
Concert AMA (Americas)
- [https://ec.yourlearning.ibm.com/w3/event/10440488](https://ec.yourlearning.ibm.com/w3/event/10440488)
Please submit your AMA questions here: [https://ibm.box.com/s/ws31tf0anp53un3vb6iderd9m1j9kfcw](https://ibm.box.com/s/ws31tf0anp53un3vb6iderd9m1j9kfcw)
from HANI BANDI (internal) to Everyone:    10:05  AM
So this is a secuirty solution?
from Giovanni My (internal) to Everyone:    10:06  AM
this concert will be part of which portfolio? Automation, Security, Application....?
from Aarti Cherian (internal) to Everyone:    10:06  AM
Concert will be part of IT Automation portfolio
from Rajdeep (Raj) Roy (internal) to Everyone:    10:07  AM
what are the diff lenses planned for ?
from Veer (internal) to Everyone:    10:07  AM
Will be able to estimate application outages/slowness with this?
from Nick Mollberg (internal) to Everyone:    10:07  AM
Dynatrace has has this capability for 2+ years - I'm glad to see it, but do we have plans to accelerate the integration of this solution with Instana?
from JENNIFER FITZGERALD (internal) to Everyone:    10:07  AM
Nick, yes portfolio integration is top of mind and we are actively working it
from MARK HELTON (internal) to Everyone:    10:08  AM
Where is the FAQ? 
from Amir Sboui (internal) to Everyone:    10:08  AM
In OCP/Containers environments, how will Concert differentiate with RedHat ACS ?
from JENNIFER FITZGERALD (internal) to Everyone:    10:08  AM
the first use cases support app sec which is  so good opportunity to compliment today 
from Angela Molinari (internal) to Everyone:    10:09  AM
we are planning to integrate also with SevOne?
from Hok Sum Chan (internal) to Everyone:    10:09  AM
Will it include SevOne intergation?
from Ashok Gunnia (internal) to Everyone:    10:09  AM
Shouldn't miss this. Instana can display APP dependency. Will we contribute to those APM teams ? Application portfolio management?
from DAVID WRIGHT (internal) to Everyone:    10:09  AM
Is Netcool part of this or do we have anew engine?
from Stu Lipshires (internal) to Everyone:    10:09  AM
can AIOPS take this as input? 
from Nicholas Power (internal) to Everyone:    10:09  AM
what about other APMs
from JENNIFER FITZGERALD (internal) to Everyone:    10:09  AM
yes sevone/ network automation is also in consideration 
from Aly Naguib (internal) to Everyone:    10:10  AM
How does this fit with the manager of manager approach aiops does?
from HANI BANDI (internal) to Everyone:    10:10  AM
So it's a risk mgmt solution?
from YANG KWANG GOH (internal) to Everyone:    10:10  AM
IBM Concert will eventually replace AIOPs?
from HANI BANDI (internal) to Everyone:    10:11  AM
@Yang.. No 
from Eduardo Ortega (internal) to Everyone:    10:12  AM
How this clashes/complement with our Threat Intelligence Insigths feature of the security portfolio?
from Ashok Gunnia (internal) to Everyone:    10:12  AM
Roja as in flower Rose?
from SINEAD GLYNN (internal) to Everyone:    10:12  AM
Josh can you confirm this is a 'Day 2' ops tool
from DAVID SONG (internal) to Everyone:    10:12  AM
how is this different from the insights dashboard in AIOPs? 
from Angela Molinari (internal) to Everyone:    10:12  AM
can you simply list the use cases to which IBMConc intend to respond? 
from Stu Lipshires (internal) to Everyone:    10:13  AM
the answer to "How does this integrate with AIOPS" Is a key question to have an answer to for our AIOPS customers
from Hok Sum Chan (internal) to Everyone:    10:13  AM
Have IBM concert demo video share with us?
from HANI BANDI (internal) to Everyone:    10:13  AM
With all due respect.. Concert is not a replacement for AIOPS as they requirement for managing infrastrucure at scale is very different from the Concert positioning
from Imran Paniwala (internal) to Everyone:    10:13  AM
I agree, we need a clearer roadmap of how this would Integrate with Cloud Pak for AIOps? 
from JENNIFER FITZGERALD (internal) to Everyone:    10:13  AM
Hok- demo & assets will go live on 21st when its announced at Think
from MARK HELTON (internal) to Everyone:    10:13  AM
Is there a link to the flyer and faq?
from SINEAD GLYNN (internal) to Everyone:    10:13  AM
it will help the folks understand how it applies Ops (which is multi dicipline) 
from Ashok Gunnia (internal) to Everyone:    10:13  AM
Forgot major Q. Is this Openshift or other K8 K3 tech backend?
from JENNIFER FITZGERALD (internal) to Everyone:    10:14  AM
future roadmap will be shared as we get closer to GA and continue to iterate,refine
from Imran Paniwala (internal) to Everyone:    10:14  AM
The way I see this could eventually feed data into AIOps as AIOps is already getting data from various components. Can they merge yes but need a clearer roadmap.
from FRANCLIM BENTO (internal) to Everyone:    10:14  AM
assuming it's OCP based will it be yet another CPak?
from David Hewitt (internal) to Everyone:    10:14  AM
great to see the efforts both organic and inorganic... big kudos to the product team and good luck getting to GA
from Eduardo Ortega (internal) to Everyone:    10:14  AM
Customers might be expecting something on the automation lense, specially after the adquisition of Hashicorp, and the relevance of Turbonomic, Instana, Ansible, etc. Are we going to name and show the use cases for Automation (despite it might not be ready for GA yet)
from Trevor Firgau (internal) to Everyone:    10:15  AM
Seems like the model is the technical differentiator of concert. Am i understanding this correct? What's the strategy there? 
from Nick Mollberg (internal) to Everyone:    10:15  AM
Do we have a target date for when sales plays for Instana+Concert will be available?
from Dhuha Qazi (internal) to Everyone:    10:15  AM
Think IT Automation Flyer: https://ibm.seismic.com/Link/Content/DC7WW7R8PBFcTGfFcWVXVqVBdcWP.
from YANG KWANG GOH (internal) to Everyone:    10:18  AM
It is kind of sudden why switch to security centric type of use cases for IT Auto. 
from Ashok Gunnia (internal) to Everyone:    10:18  AM
Like patching of CVEs like in iVanti. How is the cert management integrated with Venifi [they manage it] - [https://venafi.com/tls-protect/](https://venafi.com/tls-protect/) . Also, it is currently managed via ServiceNow...
from Chuck Miller (internal) to Everyone:    10:18  AM
Is there any integration on the roadmap with Openpages?