import os
import sh
import sys


class Keychain:
    identities = []
    identities_str = 'need find_identity first'

    def __init__(self, name, password=''):

        home = os.path.expanduser("~")
        # home = os.getenv('HOME')

        filename = os.path.join(home, 'Library', 'Keychains', name)

        self.filename = filename
        self.name = name
        self.password = password

        # Keychain.list(self.name)
        self.securitycmd = sh.Command('/usr/bin/security')

    def exists(self):
        if os.path.exists(self.filename):
            return True
        if os.path.exists(self.filename + '-db'):
            return True
        return False

    def delete(self):
        self.securitycmd('delete-keychain', self.name,
                         _out=sys.stdout.buffer, _err=sys.stderr.buffer)

    def create(self):
        self.securitycmd('create-keychain', '-p', self.password, self.name,
                         _out=sys.stdout.buffer, _err=sys.stderr.buffer)

    def add_to_search_list(self):
        self.securitycmd('list-keychain', '-s', self.name, 'login.keychain',
                         _out=sys.stdout.buffer, _err=sys.stderr.buffer)

    @staticmethod
    def list():
        securitycmd = sh.Command('/usr/bin/security')
        securitycmd('list-keychain',
                    _out=sys.stdout.buffer, _err=sys.stderr.buffer)

    def unlock(self):
        self.securitycmd('unlock-keychain', '-p', self.password, self.name,
                         _out=sys.stdout, _err=sys.stderr)
        # self.securitycmd('set-keychain-settings', '-u', '-t', 6000, self.name,
        self.securitycmd('set-keychain-settings', '-l', self.name,
                         _out=sys.stdout, _err=sys.stderr)

    def sierra_operation(self):
        # https://stackoverflow.com/questions/39868578/security-codesign-in-sierra-keychain-ignores-access-control-settings-and-ui-p/40870033#40870033
        self.securitycmd('set-key-partition-list',
                         '-S', 'apple-tool:,apple:,codesign:',
                         '-s', '-k', self.password, self.name)

    def import_certificate(self, p12_filename, p12_password=None):
        if not os.path.exists(p12_filename):
            raise Exception("{} not exists".format(p12_filename))
        cmd = self.securitycmd.bake('import', p12_filename, '-k', self.name,
                                    '-T', '/usr/bin/codesign',
                                    '-T', '/usr/bin/security')
        # cmd = self.securitycmd.bake('import', p12_filename, '-k', self.name,
        #                             '-A')
        if p12_password is not None:
            cmd = cmd.bake('-P', p12_password)
        # print(cmd)
        cmd(_out=sys.stdout, _err=sys.stderr)

    def export(self, p12_filename, p12_password=''):
        self.securitycmd('export', '-k', self.name, '-t', 'identities',
                         '-f', 'pkcs12', "-P", p12_password, '-o', p12_filename)

    @staticmethod
    def find_identity(keychain=None, valid_only=True):
        #
        # output = subprocess.check_output(
        #     ["/usr/bin/security", "find-identity", "-p", "codesigning", "-v",
        #      self.name])
        # for identity_id, certificate_name in re.findall(
        #         "[ ]+[\d]+\) ([^ ]+) \"(.*)\"", output):
        #     self.identities.append({'identity_id': identity_id,
        #                             'certificate_name': certificate_name})
        # self.identities_str = output
        security = sh.Command('/usr/bin/security')
        cmd = security.bake('find-identity', "-p", "codesigning")
        if valid_only:
            cmd = cmd.bake('-v')
        if keychain is not None:
            if isinstance(keychain, Keychain):
                cmd = cmd.bake(keychain.name)
            else:
                cmd = cmd.bake(keychain)
        cmd(_out=sys.stdout, _err=sys.stderr)


if __name__ == '__main__':
    k = Keychain('build.keychain', 'password')
