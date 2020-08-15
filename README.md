# manage-sts-authorized-info

todo 後で書く

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

## Contributing

See [Contributing](/.github/CONTRIBUTING.md) details.

## For Develop

### Create Local Setting

- Formatter

1. Install yarn and black.

```
$ brew install yarn black
```

2. Node moudle setup.

```
$ yarn install
```

- Security

1. install git-secrets.

```
brew install git-secrets
```

2. register aws credentials.

```
git secrets --register-aws
```

**Please don't use 'git secrets --install' command. .git/hooks/pre-commit is already used by husky**

### Test

```
$ cd ${PROJECT_ROOT}
$ python -B -m unittest discover
```
