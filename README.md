# Attachment Downloader

Automate running code submitted through email

## Background
At my job, we use coding prompts as one phase of our interview process. Candidates will email in their solutions to the coding prompt. The purpose of this project is to automate the process of downloading those solutions, running them, and checking their output against an expected result.

## Important Considerations
Because this project basically amounts to running untrusted code, **USE THIS AT YOUR OWN RISK**. Included in the repo is a Vagrantfile that will create a VM to run in. I highly recommend using the VM to sandbox the untrusted code being run.
