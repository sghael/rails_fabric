from __future__ import with_statement
from fabric.api import *
from fabric.contrib import files

import os

import logging
FORMAT="%(name)s %(funcName)s:%(lineno)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

########################
# Run this against Ubuntu 12.04 LTS
#
# You MUST have your ssh keys in root's authorized_keys file.  Otherwise
# this fabric script won't work
########################


def do_as_user_in_path(user, path, commands):
    sudo('sudo -u %(user)s sh -l -c "cd %(path)s && %(commands)s" ' % {'user': user, 'path': path, 'commands': commands}, shell=True)


def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages), shell=False)


def update_server():
    sudo('apt-get update')
    sudo('apt-get upgrade -y')


def install_utils():
    apt_get('htop')
    apt_get('wget')
    apt_get('locate')
    apt_get('screen')
    apt_get('iotop')
    apt_get('curl')
    apt_get('bison')
    apt_get('openssl')
    apt_get('libtool')
    apt_get('libreadline6')
    apt_get('libreadline6-dev')
    apt_get('zlib1g')
    apt_get('zlib1g-dev')
    apt_get('libssl-dev')
    apt_get('libsqlite3-0')
    apt_get('libsqlite3-dev')
    apt_get('libxml2-dev')
    apt_get('libxslt1-dev')
    apt_get('libpcre3-dev')
    apt_get('libpcrecpp0')
    apt_get('libyaml-dev')
    apt_get('libxslt-dev')
    apt_get('libc6-dev')
    apt_get('sqlite3')
    apt_get('autoconf')
    apt_get('python-software-properties')
    apt_get('denyhosts')
    apt_get('redis-server')
    apt_get('libcurl4-openssl-dev')
    apt_get('openjdk-6-jre-headless')
    apt_get('ant')
    apt_get('openjdk-6-jdk')
    apt_get('checkinstall')
    apt_get('git-core')
    apt_get('g++')
    apt_get('build-essential')
    apt_get('automake')
    apt_get('ncurses-dev')
    apt_get('s3cmd')
    apt_get('pbzip2')


def bootstrap_ruby():
    apt_get('ruby')
    with cd('/tmp'):
        sudo('wget http://production.cf.rubygems.org/rubygems/rubygems-1.8.5.tgz')
        sudo('tar xvzf rubygems-1.8.5.tgz')
    with cd('/tmp/rubygems-1.8.5'):
        sudo('ruby setup.rb')


def create_users(list_of_users):
    for user in list_of_users:
        try:
            sudo('/usr/sbin/useradd -p `openssl passwd -crypt "TODO-FOOBAR"` %s -m -s /bin/bash' % user)
        except:
            print "error creating user %s.  Perhaps the user exist already?" % user


def add_user_to_sudo(list_of_users):
    for user in list_of_users:
        try:
            sudo('/usr/sbin/adduser %s sudo' % user)
        except:
            print "error adding user %s to sudo group." % user


def add_my_sshpubkey(list_of_users):
    f = open(os.getenv("HOME") + "/.ssh/id_rsa.pub", 'r+')
    ssh_pubkey = f.read()

    for user in list_of_users:
        f.close()
        sudo('mkdir -p /home/' + user + '/.ssh')
        sudo('chown ' + user + ':' + user + ' -R /home/' + user + '/.ssh')
        sudo('chmod 700 /home/' + user + '/.ssh')
        sudo('touch /home/' + user + '/.ssh/authorized_keys')
        sudo('echo "%s" >> /home/%s/.ssh/authorized_keys' % (ssh_pubkey, user))
        sudo('chown ' + user + ':' + user + ' -R /home/' + user + '/.ssh/authorized_keys')
        sudo('chmod 644 /home/' + user + '/.ssh/authorized_keys')


def modify_sudoers_file():
    run(" sed -i '$ d' /etc/sudoers ")
    run(" echo '%sudo ALL=NOPASSWD: ALL' >> /etc/sudoers ")


def set_locale():
    sudo('locale-gen en_US.UTF-8')
    sudo('/usr/sbin/update-locale LANG=en_US.UTF-8')


def install_percona():
    apt_get('libmysqlclient-dev')
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show percona-server-server*')
    if result.failed is False:
        warn('Percona-5.5 is already installed')
        return
    apt_get('debconf-utils')
    mysql_password = prompt('Please enter Percona "root" password:')
    sudo('echo "percona-server-server-5.5 percona-server-server/root_password password ' \
                  '%s" | sudo debconf-set-selections ' % mysql_password)
    sudo('echo "percona-server-server-5.5 percona-server-server/root_password_again password ' \
                  '%s" | sudo debconf-set-selections' % mysql_password)

    sudo('curl http://www.percona.com/downloads/RPM-GPG-KEY-percona > /tmp/RPM-GPG-KEY-percona && gpg --import /tmp/RPM-GPG-KEY-percona')
    sudo('gpg -a --export CD2EFD2A | sudo apt-key add -')

    sudo('echo "deb http://repo.percona.com/apt precise main" >> /etc/apt/sources.list')
    sudo('echo "deb-src http://repo.percona.com/apt precise main" >> /etc/apt/sources.list')
    sudo('apt-get update')
    apt_get('percona-server-server-5.5')
    apt_get('percona-server-client-5.5')
    apt_get('percona-xtrabackup')

    configFile = os.path.join(os.getcwd(), 'my.cnf')
    files.upload_template(configFile, '/etc/mysql/', use_sudo=True)
    mysql_restart()


def mysql_restart():
    """ Restart MySQL """
    sudo('service mysql restart')


def mysql_execute(sql, user='', password=''):
    """
    Executes passed sql command using mysql shell.
    """
    with settings(warn_only=True):
        return run("echo '%s' | mysql -u%s -p%s" % (sql, user, password))


def install_monit():
    apt_get('monit')


def install_nginx():
    apt_get('nginx')


def create_ssh_key():
    """
    run this using 'fab -H <user>@<ip_address> create_ssh_key'
    """
    try:
        run('/usr/bin/ssh-keygen -t rsa -b 2048 -N "" -f .ssh/id_rsa')
    except:
        print "error creating ssh key"


def add_keys_to_root():
    sudo('curl https://s3.amazonaws.com/TODO-YOURBUCKET/id_rsa.pub > /root/.ssh/authorized_keys')


###############################################


def setup_server():
    update_server()
    install_utils()
    create_users(['TODO', 'TODO', 'TODO-name_of_app'])
    add_user_to_sudo(['TODO', 'TODO', 'TODO-name_of_app'])
    add_my_sshpubkey(['TODO', 'TODO', 'TODO-name_of_app'])
    modify_sudoers_file()
    set_locale()

    # Installing of Percona 5.5 instead of MySQL 5.1
    install_percona()
    bootstrap_ruby()

    install_monit()
    install_nginx()

    add_keys_to_root()
