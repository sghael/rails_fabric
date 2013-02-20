Requirements
=============

You must have Python and Fabric on your machine.  Typically you can install fabric with:

    $ easy_install fabric

Once you have Fabric installed, you can run

    $ ./provision.sh

against a target IP address to provision that server.


Target Machine
=============
Ubuntu 12.04 LTS (minimal) - 64 bits


Manual Steps before running fabric
=============
Install ssh pub key into root users directory


Manual Steps after running fabric
=============

Set hostname
-------------

Depending on the name you want:

nameofapp_Production
or
nameofapp_Staging

    $ echo 'nameofapp_Production' >> /etc/hostname

And on the second line of '/etc/hosts' add:

    127.0.0.1  nameofapp_Production


REBOOT SERVER.

Add a root cron job to delete files from backup directory older than N days

    0  0 * * * find /root/mysqlbackups -mtime +5 -exec rm {} \;


INFO
=============

Use /etc/init.d/mysql for control or sudo service mysql start/stop/restart
