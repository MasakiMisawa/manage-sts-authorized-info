# manage-sts-authorized-info

1. [What is?](#what-is?)
1. [Installation](#installation)
1. [Usage](#usage)
1. [Support](#support)
1. [Contributing](#contributing)
1. [For Develop](#for-develop)

## What is?

This tool makes it easier to manage the AWS Security Token Service when using the AWS CLI.  
It provides two merit.

1. Saves you from having to add the assumed role information to the config file for the AWS CLI.
1. You can see in the history what assumed role's were added or removed from the config file for the AWS CLI.

## Installation

### How to install/reinstall.

```
$ pip install PyYAML
$ cd ${PROJECT_ROOT}
$ python setup.py
```

### Install config.

See [seup-config.yaml](/config/setup-config.yaml) details.

you can customize these settings.

- CONFIG_FILE

  - FILE_PATH str  
    AWS CLI config file path.  
    register_sts_assumed_role function overwrites the contents of this file.

- REGISTER_PROFILE

  - PROFILE_NAME (default) str  
    Default value of the profile name to be registered in the config file.  
    this value can be overridden when the register_sts_assumed_role function is executed.
  - REGION (default) str  
    Default value of the register profile region name to be registered in the config file.  
    this value can be overridden when the register_sts_assumed_role function is executed.
  - OUTPUT (default) str  
    Default value of the register profile output format to be registered in the config file.  
    this value can be overridden when the register_sts_assumed_role function is executed.

- CHANGE_LOG
  - FILE_PATH str  
    Log file path to execute register_sts_assumed_role function.  
    the profile information registered or deleted by register_sts_assumed_role function is recorded.

## Usage

```
$ register_sts_assumed_role
```

![architecture](document/register_sts_assumed_role.gif)

## Support

### OS

Supports MacOS(OS X) and Linux(CentOS / Ubuntu).  
`WindowsOS not supported sorry!`

### SHELL

Supports bash and zsh.  
`Other shell not supported sorry!`

## Contributing

See [CONTRIBUTING.md](/.github/CONTRIBUTING.md) details.

## For Develop

### Create Local Setting

- **Formatter**

1. Install yarn and black.

```
$ brew install yarn black
```

2. Node module setup.

```
$ yarn install
```

- **Security**

1. install git-secrets.

```
brew install git-secrets
```

2. register aws credentials.

```
git secrets --register-aws
```

**Please don't use 'git secrets --install' command.**  
**.git/hooks/pre-commit is already used by husky.**

- **Test**

1. install parameterized.

```
pip install parameterized
```

### Test

```
$ cd ${PROJECT_ROOT}
$ python -B -m unittest discover
```
