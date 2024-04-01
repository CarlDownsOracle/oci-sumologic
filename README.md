# OCI -> Sumologic

##  Overview

This sample implements a simple architecture for exporting OCI Logs to Sumologic.

---
# OCI

Here are the steps to set up OCI.

## OCI Compartment

_Name: ABC_

Create a compartment to contain the following:


- Virtual Cloud Network
- Application + Function
- Service Connector

## OCI Group

_Name: functions-developers_

Create a user group where we can assign developer related policies.   


## OCI Policies

See [common policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm).

### Developer Policies

Developer can create, deploy and manage Functions and Applications

See [reference](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm#)

    Allow group functions-developers to manage repos in tenancy
    Allow group functions-developers to manage serviceconnectors in tenancy
    Allow group functions-developers to manage logging-family in tenancy
    Allow group functions-developers to manage functions-family in tenancy
    Allow group functions-developers to use cloud-shell in tenancy
    Allow group functions-developers to use virtual-network-family in tenancy

    Allow service faas to read repos in tenancy where request.operation='ListContainerImageSignatures'


### Service Connector Policies

Service Connector can access Application + Function, Audit Logs

    Allow any-user to manage functions-family in compartment ABC where all {request.principal.type='serviceconnector'}
    Allow any-user to manage logging-family in compartment ABC where all {request.principal.type='serviceconnector'}


#  Function

[Quick Start guide on OCI Functions](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartguidestop.htm) before proceeding.

We will need to build and deploy a function.  The above guide takes you step by step.

These are the variables we need to set up in the Function Application.  

Here are the supported variables:

| Environment Variable        |    Default     | Purpose                                                                            |
|-----------------------------|:--------------:|:-----------------------------------------------------------------------------------|
| SUMOLOGIC_ENDPOINT          | not-configured | Sumologic API endpoint                                                             |
| SEND_TO_SUMOLOGIC          |      True      | Set to False if you need to debug things on OCI side without sending to Sumologic. |
| MAX_RECORDS_PER_POST               |      100       | Batch size for each POST.                                                          |
| LOGGING_LEVEL               |      INFO      | Controls function logging outputs.  Choices: INFO, WARN, CRITICAL, ERROR, DEBUG    |




# Troubleshooting

### FunctionTimeOut

If the Function times out, please change the
[function timeout setting](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscustomizing.htm).


---

## References

Please see these references for more details.


### OCI IaaS Data Sources

- [OCI Logging Service](https://docs.oracle.com/en-us/iaas/Content/Logging/Concepts/loggingoverview.htm)
- [OCI Audit Service](https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm)
- [OCI Monitoring Service](https://docs.oracle.com/en-us/iaas/Content/Monitoring/Concepts/monitoringoverview.htm)
- [OCI Events Service](https://docs.oracle.com/en-us/iaas/Content/Events/Concepts/eventsoverview.htm)
- [OCI CloudGuard](https://docs.oracle.com/en-us/iaas/cloud-guard/using/index.htm)

### OCI IaaS Enabling Technologies

- [OCI Service Connector Hub](https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm)
- [OCI Functions Service](https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm)
- [OCI Streaming Service](https://docs.oracle.com/en-us/iaas/Content/Streaming/Concepts/streamingoverview.htm)
- [OCI DevOps Pipelines](https://docs.oracle.com/en/solutions/build-cicd-pipelines-devops-function/index.html)


---
## License
Copyright (c) 2014, 2023 Oracle and/or its affiliates
The Universal Permissive License (UPL), Version 1.0
