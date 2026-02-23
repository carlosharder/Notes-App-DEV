---
title: Gerry School
created: 2024-03-17T15:24:16
modified: 2024-03-17T15:24:18
---

Gerry School
Turbonomic training
Demonstração: módulos
••••••••••••••••••••NEEDS TO BE STREAMLINED•••••••••••••••••••••
PRELUDE:
* Gerry, I have found it usefull to preface the demo with a visual metaphor to clearly differenciate Turbonomic from tools that we know are outthere, in particular APMs.
* Picture yourself driving, it's dark, it's foggy and it's raiining.
* Pretty scary, but you have little machine above your dashboard that gives you insights. It tells you that there is a stopped vehicle on the right shorlder, that there is construction 1 mile ahead on the right, that there is oil on the road. That is what an APM does, it gives you valuable insights.
* Now, imagine a platform that takes realtime data from all the call, including that APM.....takes full or partial control o the veichle. And now imagine, letting go of the wheel and seing go left, go rifht, accelerate brake. That is automation and that is one way in which turbonomic is different.
* But turbonomic is different in another important way. There another family of solutions, that do a great job letting you know that part of your application stack has diviated from a healthy state, that sounds great, but think about it. They are giving you the warking after something is broken.
* Turbonomic is going to take a preventive approach.
* Turbonomic by having a complete understanding of the supply and demand resource needs of your application and full stack will generate actions, actions that will drive and sustaing the health of the complete application stack.
* To achieve this, Turbonomic is going to use API calls to gather realtime data from every layers. starting with the application, down to ___ to _____ all the way down to phisical host and stroate.
* this realtime data is
PART I - PREVENTITIVE APPROACH - APP CENTRIC
* What makes Turbonomic Different
* Turbonomic takes a preventive approach
* Supply and demand
* API Calls
* Real time data
* Every single layer of Stack
* Topology and insight are a fraction of the value
PART II - ACTIONS - HOLISTIC UNDERSTANDING
* Action that mantain and drive the health
* Focus on 3 actions
* Let's take a step back
* Turbonomic will never tell you to....
* It is not about taking actions in isolation, but with a complete understanding of interdependencies and Application demands
PART III - APP CENTRIC - INCREASE TRUST
* Business applications are the business
* look at the topology....
* let's focus on one application
* Turbonomic will give you metrics
* Turbo will give actions
* Turbo give details > Built trust / Look deeper
* Increase trust.....
PART IV - CONTROL PLATFORM - CLIENT CONTROL
* Turbo > control platform
* Control > understanding the implications of your actions before you take them
* Cluster > 75 VMs
* Topology
* *You can see # Host in the cluster
* Metrics: CPU, Mem, ReadyQ, Swapping
* Side by Side comparison
* What if....
* Plan > Run > questions?
* Side by side comparison
* Wow Doing all this manually.......
PART - AUTOMATION - BUILD TRUST
* Thousands of actions
* Customize the Automation
Let's take a step back
It took 1200 actions to get form here to her.
Turbonomic does not only allows you automate the implemtation of the actions
but it also allows you customize how this automation happens.
for that we go to setting. policy. new automation policy. For this demos lets focus on the automation of Virtual Machines.
* [ ] Name the automation Rule
* [ ] Select Scope
* [ ] Select What will be automated
	* [ ] Select Move
	* [ ] Change to Automatic
	* [ ] And if we hit "Save and Apply" Actions will start to happen, base on these rules
But as you saw there is more than "Move" actions
We can also do CPU and memory Zise-up actions.
and we can use the Non-Disruptive Mode option.
As you trust more and more the sistem, you will be able to do set up automation for actions that are disruptibe.
such as scale down.
In all of these actions the system will give the option to integrate with a ITSM system
and use scripts to coordinate before, during and after execution.
the platform even give you options about when this actions can take place
Typically, when our customers are just starting out with automation, they’re more comfortable automating non-disruptive actions, so let’s do that by clicking on Automation and Orchestration, click on Action type which in this case is “move” and if hot add is enabled we can also include Size up actions such as VCPU & Vmem resize up without causing a disruption.
Next we change action acceptance to automatic, then click submit.
After that, we click action constraints and click enforce non disruptive mode and the software will automatically identify the VM’s in this environment that have hot add enabled, to ensure there is no disruption in the environment.
Click save and apply and you’re all set.
Once you build trust in the automation and are ready to automate disruptive actions such as resizing down, it’s just as simple.
You would go through the same process, uncheck non disruptive mode and schedule the actions for a time when they wouldn’t interfere with day to day operations such as 2am on a Sunday.
And if you’re using an ITSM vendor such as ServiceNow, we can fully incorporate the actions within the software respecting their workflows and working within the boundaries and policies.
we are not asking, we don't recomend that client do full automation.
We want this to be a tool that fit into ongoing processes
and sistematy supports your iniitative reach full automation.
we can the client o have sistematic and gradual path of automatiation
PART 6 - THE CLOUD - SUSTAINABLE SAVINGS
* In the cloud we are solving the same problem that we were on-premise.
* We have also have the a view of the application stack, from the application, all the way down to zones are regions.
* And just like on premise, we'll give an over overview of the health of each layers, with red denoting overprovisioning risk, yellow underprovisioning risk and green an healthy state.
* And that same problem that we are solving is to assure the performance of all mission critical applications.
* Here I have 25 application in the cloud and some of them are not getting the resources that they need.
* The platform can show you actions to achieve the desired performance. Some involve the scaling of VMs and others the scaling of volumes.
* If I click on details and view the graph, I will see that 76% of the time the the Vcpu has bee running at 99% percent capacity. THIS IS PUTTING THE APPLICATION AT RISK.
* AND just like On-Prem, the platform not only gives you insight, but it gives you actions. Here the it is telling tht we need to move scale this VM from this instance to this instance.
* Notice that our emphasis continues to be on "How to assure application performance"
* We see Potential Savings as a bi-produce benefit.
* Why do we do this? What would happen if you implement an automation platform that is solely focus on Potential Savings, and initially it leads to savings greater than these. But eventualy, at some point. It leads to a failure of one of your chritical applications.
* The owner of that application in their own best interest, moving forward will over provision resource for that application. And the same hold true for all the other applications.
* But if you are using platform that never compromises on application performance, your teams will learn to trust the provisioning decisions and will give the program the space to achieve sustainbable Potential Savings.
* What would happen, if you use our platform and it never compromises the application performance? Your teams owning this applications will develop trust on the platform and lead to lasting change.
* There are many decision that with out any compromise in the Application, would have the ability to lower your monthly bill.
* On the left we have a list of all the actions to better aligght the existing demand of your applicaiton with the supply.
* You are able to schedule this decision for downtime to minimize any disruption.
* In the end, by assume application peformance this results are actually attainable.
* we need to look at the "performance" we need to go to view
overprovision risk.