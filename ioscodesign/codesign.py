import zipfile
import os
import shutil
import sys
import tempfile

import click
import sh

from .keychain import Keychain
from .mobileprovision import MobileProvision


def get_app_path(path):
    name = [x for x in os.listdir(os.path.join(path, 'Payload')) if
            x.endswith('.app')][0]
    return os.path.join(path, 'Payload', name)


def get_output_name(input_file, sign_type, output_path):
    basename = os.path.basename(input_file)
    name, extension = basename.rsplit('.', maxsplit=2)
    return os.path.join(output_path,
                        name + '-' + sign_type + '-Signed.' + extension)


@click.command()
@click.option('-p', '--provision-profile', type=click.Path(),
              required=True, help=u'Provisioning Profile')
@click.option('--p12', type=click.Tuple([click.Path(), str]), multiple=True,
              help=u'p12文件和密码')
@click.option('-o', '--output-path', type=click.Path(), help=u'输出目录')
@click.argument('input_file', type=click.Path(), required=True)
def main(provision_profile, p12, output_path, input_file):
    """
    签名步骤

    \b
    1. 新建keychain
    2. 将证书、私钥导入keychain
    3. 根据Provisioning Profile确定identity 并生成 entitlements.plist
    4. 解压安装包
    5. 重签名
    6. 压缩生成新的安装包
    """

    k = Keychain('build.keychain', 'mysecretpassword')
    if k.exists():
        k.delete()
    k.create()
    k.add_to_search_list()
    Keychain.list()
    k.unlock()
    for p12_filename, p12_password in p12:
        k.import_certificate(p12_filename, p12_password)
    k.sierra_operation()
    Keychain.find_identity(k)

    profile = MobileProvision(provision_profile)
    profile.parse()
    identity = profile.get_identity()
    _, entitlements = tempfile.mkstemp()
    profile.save_entitlements(entitlements)

    temp_path = tempfile.mkdtemp()
    zf = zipfile.ZipFile(input_file)
    zf.extractall(temp_path)

    app_path = get_app_path(temp_path)
    shutil.rmtree(os.path.join(app_path, '_CodeSignature'), ignore_errors=True)
    shutil.copy(provision_profile,
                os.path.join(app_path, 'embedded.mobileprovision'))

    codesign = sh.Command('/usr/bin/codesign')
    cmd = codesign.bake('--deep', '--force', '--verbose',
                        '--keychain', 'build.keychain',
                        '--sign', identity, '--entitlements', entitlements,
                        app_path)
    print(cmd)
    cmd(_out=sys.stdout.buffer, _err=sys.stderr.buffer)

    if output_path is None:
        output_path = os.path.dirname(input_file)
    output_file = get_output_name(input_file, profile.profile_type, output_path)
    print(output_file)
    shutil.make_archive(output_file, 'zip', temp_path)
    os.rename(output_file + '.zip', output_file)

    k.delete()
    os.unlink(entitlements)
    shutil.rmtree(temp_path)
