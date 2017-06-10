import os
import subprocess
import plistlib
from string import Template
import re


class MobileProvision:
    ProvisionTypes = ['Distribution', 'Development', 'Adhoc']

    def __init__(self, filename):
        self.info = None
        self.uuid = None
        self.is_development_profile = False
        self.profile_type = 'Distribution'
        self.provisioned_devices = 0
        self.application_identifier = None
        self.certificate_names = []
        if os.path.exists(filename):
            self.filename = filename
        else:
            raise Exception("%s not exists" % filename)

    def parse(self):
        output = subprocess.check_output(
            ["/usr/bin/security", "cms", "-D", "-i", self.filename],
            stderr=subprocess.DEVNULL)
        self.info = plistlib.loads(output)

        self.uuid = self.info['UUID'].upper()
        self.is_development_profile = 'ProvisionedDevices' in self.info
        self.certificate_names = []
        if 'DeveloperCertificates' in self.info:
            for c in self.info['DeveloperCertificates']:
                # certificate部分的解析，是否可以参考下面的链接？
                # http://stackoverflow.com/a/6782192
                # certificate_name_search = re.search('(iPhone .*)\x31\x13\x30\x11',c.data)
                # 下面的正则表达式是一个经验公式，根据现有的 mobileprovision 文件内容推测出来的
                # 不保证完全准确，也不保证将来 mobileprovision 格式变化之后还能用
                # certificate_name_search = re.search('(iPhone .*)\x31\x13', str(c))
                certificate_name_search = re.search('(iPhone .*?\))', str(c))
                if certificate_name_search:
                    self.certificate_names.append(
                        certificate_name_search.group(1))

        if 'ProvisionedDevices' in self.info:
            if 'Entitlements' in self.info and \
                            'aps-environment' in self.info['Entitlements'] and \
                            self.info['Entitlements'][
                                'aps-environment'] == 'production':
                self.profile_type = 'Adhoc'
            else:
                self.profile_type = 'Development'
            self.provisioned_devices = len(self.info['ProvisionedDevices'])
        else:
            self.profile_type = 'Distribution'

        self.application_identifier = self.info['Entitlements'][
            'application-identifier']

        self.info['application_identifier'] = self.application_identifier
        self.info['profile_type'] = self.profile_type

    def __str__(self):
        if self.profile_type == 'Development' or self.profile_type == 'Adhoc':
            devices = "%4d devices, " % self.provisioned_devices
        else:
            devices = "no devices, "
        short_uuid = self.uuid.split('-')[0] + '-...'
        s = Template(
            "%s, ${CreationDate}, ${profile_type}, %s${application_identifier},\t${TeamName},\t${Name}" % (
                short_uuid, devices)).substitute(self.info)
        for name in self.certificate_names:
            s += '\n' + '\t' * 7 + name
        return s + '\n'

    def description(self, prefix=''):
        s = Template("""${prefix}TeamName:\t${TeamName}
${prefix}appid:\t\t${application_identifier}
${prefix}profile_type:\t${profile_type}
${prefix}Name:\t\t${Name}
${prefix}UUID:\t\t${UUID}
${prefix}CreationDate:\t${CreationDate}
${prefix}certificate:""").substitute(dict(self.info, prefix=prefix))
        for name in self.certificate_names:
            s += '\n' + prefix + '\t' * 2 + name
        return s + '\n'

    def get_identity(self):
        return self.certificate_names[0]

    def save_entitlements(self, filename):
        o = self.info['Entitlements']
        fp = open(filename, 'wb')
        plistlib.dump(o, fp)


if __name__ == '__main__':
    profile_name = 'profile/19C237C1-71D5-4DC8-B455-A224F15257EA.mobileprovision'
    profile_name = 'profile/00584E33-7D9D-436E-8A9D-AA27F165AA20.mobileprovision'
    profile_name = 'profile/EA779F12-7531-4BC9-9AD8-19243A84DE91.mobileprovision'
    profile = MobileProvision(profile_name)
    profile.parse()
    print(profile)
    print(profile.description())
