## Synopsis
Enables one to quickly interact with the [Alibaba Cloud APIs](https://www.alibabacloud.com/support/developer-resources) via the [python SDK/aliyun-cli](https://github.com/aliyun/aliyun-cli).
It frees you from having to set up your own python environments and is perfect for one-shot small tasks, experiments or background jobs of all sorts.
OSSUtil comes as a bonus.

Note: python 2.7

## Usage

```
docker run -ti aliyunca/aliyuncli-python-toolbox:latest sh

# if you want the container to live after exiting, daemonize it with "-d"
docker run -dti aliyunca/aliyuncli-python-toolbox:latest sh
```

This will drop you into the interactive mode inside the container. You can now interact with the  python CLI:

```
# configure the CLI

$ aliyuncli configure 
Aliyun Access Key ID [None]: my_access_id
Aliyun Access Key Secret [None]: mypassword
Default Region Id [None]: 
Default output format [None]: 

# make calls to Alibaba Cloud!
$ aliyuncli ecs
usage: aliyuncli <command> <operation> [options and parameters]
[ecs] valid operations as follows:

ActivateRouterInterface                  | AddTags   
AllocateEipAddress                       | AllocatePublicIpAddress
ApplyAutoSnapshotPolicy                  | AssociateEipAddress
AssociateHaVip                           | AttachDisk
....

# get some help regarding the function
aliyuncli ecs DescribeImages help

# configure ossutil
ossutil config
```

## Passing credentials
The below environment variables are recognized by the image and can be used to bootstrap the container (either via `-e FOO=BAR` or as an `env` file):

```
ALI_ACCESS_KEY
ALI_ACCESS_SECRET
ALI_DEFAULT_REGION 
ALI_OUTPUT_FORMAT

# ossutil
ALI_OSSUTIL_LANG
ALI_OSSUTIL_ENDPOINT
```

Another way of bootstrapping it is to pass the volume into the container:

```
- v my_aliyuncli_user/.aliyuncli:/root/.aliyuncli
```

In this scenario you would run **configure** once which would write the required files  which you can then continue using across containers.

Please refer to the [**acs**](#extensions) directory for more information.

## Extensions

The `acs` directory contains a number of scripts that add extra functionality to the CLI as well as have snippets which are useful in day to day operations on Alibaba Cloud.
They tackle typical use cases and can also be used as  reference to chain various tasks related to infrastructure management.

```
acs/admin/ansible-support.sh         # adds ansible support; read below for more info
acs/network/vrouter_route_switch.py  # Switches route entries from HAVIP, Instance or RouterInterface and vice versa.
...
```

Most scripts have a help written to what they do and their inputs, e.g.:
```
acs/network/vrouter_route_switch.py -h
```

## Ansible

It is easy to add ansible support to the container:

```
# start container
docker run -dti \
    --name aliyuncli \
    -v my_ansible_dir:/ansible \
    aliyunca/python-toolbox:latest
    sh

# -d to have a "persistent" toolbox; something you can stop and start
# -v to bring your ansible project files into the container

docker exec -ti aliyuncli sh

# this is a simple ansible installation script
/tmp/ansible-support.sh

# go go go
$ ansible-playbook aliyun.yml
```