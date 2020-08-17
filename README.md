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

1. Saves you from having to add the provided iam role arn information to the config file for the AWS CLI.
1. You can see in the history what provided iam role arn's were added or removed from the config file for the AWS CLI.

## Installation

### How to install/reinstall.

```
$ cd ${PROJECT_ROOT}
$ python setup.py
```

### Install config.

See [seup-config.yml](/config/setup-config.yml) details.

you can customize these settings.  
todo 設定可能項目の記載

## Usage

todo 後で書く

## Support

### OS

Supports macOS and Linux(CentOS / Ubuntu).  
`WindowsOS not supported sorry!`

### SHELL

Supports bash and zsh.  


## Contributing

See [CONTRIBUTING.md](/.github/CONTRIBUTING.md) details.

## For Develop

### Create Local Setting

- **Formatter**

1. Install yarn and black.

```
$ brew install yarn black
```

2. Node moudle setup.

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

### Test

```
$ cd ${PROJECT_ROOT}
$ python -B -m unittest discover
```
