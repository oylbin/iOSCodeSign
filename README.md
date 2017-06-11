# iOSCodeSign

[关于iOS应用签名](https://github.com/oylbin/iOSCodeSign/wiki/about-ios-codesigning)

## setup

clone this repo and cd to repo directory

    virtualenv -p python3 env
    source env/bin/activate
    pip install --editable .
    env/bin/ioscodesign --help

## usage

```
Usage: ioscodesign [OPTIONS] INPUT_FILE

  签名步骤

  1. 创建一个专门用于签名的Keychain。
  2. 解锁Keychain。
  3. 将证书、私钥（p12文件）导入keychain。
  4. 根据Provisioning Profile确定identity 并生成 entitlements.plist。
  5. 执行security set-key-partition-list，具体原因参考 security / codesign in Sierra: Keychain ignores access control settings andts for permission
  6. 解压安装包。
  7. 重签名，指定identity和entitlements。
  8. 压缩生成新的安装包。

Options:
  -p, --provision-profile PATH  Provisioning Profile  [required]
  --p12 <PATH TEXT>...          p12文件和密码
  -o, --output-path PATH        输出目录
  --help                        Show this message and exit.
```

## example

	env/bin/ioscodesign -p Distribution.mobileprovision \
	                    --p12 Distribution.p12 this_is_a_password \
	                    app.ipa
