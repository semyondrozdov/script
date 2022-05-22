import os
import random
import string
import subprocess


def download_app():
    global ipv4, ipv6_prefix, ipv6_netmask, port, addresses_amount

    os.system("apt-get install -y gcc make build-essential nano wget tar gzip")

    os.system("wget --no-check-certificate https://github.com/z3APA3A/3proxy/archive/0.9.0.tar.gz")
    os.system("tar xzf 0.9.0.tar.gz")

    os.system("cd 3proxy-0.9.0/; make -f Makefile.Linux; cd bin/; cp 3proxy /usr/bin/")

    os.system("rm 0.9.0.tar.gz")
    os.system("rm -R 3proxy-0.9.0")

    os.system("mkdir /etc/3proxy/")


def generate_ipv6_file(path):
    global ipv4, ipv6_prefix, ipv6_netmask, port, addresses_amount

    with open(path, "w") as file:
        for i in range(addresses_amount):
            while True:
                if ipv6_netmask == 48:
                    current_address = ipv6_prefix + ":".join("{:x}".format(random.randint(0, 2**16 - 1)) for i in range(5))

                elif ipv6_netmask == 64:
                    current_address = ipv6_prefix + ":".join("{:x}".format(random.randint(0, 2 ** 16 - 1)) for i in range(4))

                elif ipv6_netmask == 80:
                    current_address = ipv6_prefix + ":".join("{:x}".format(random.randint(0, 2 ** 16 - 1)) for i in range(3))

                if current_address not in addresses_list:
                    addresses_list.append(current_address)
                    file.write(current_address + "\n")
                    break


def generate_config(path):
    global ipv4, ipv6_prefix, ipv6_netmask, port, addresses_amount

    os.system("adduser --system --no-create-home --disabled-login --group --force-badname 3proxy")

    gid = subprocess.getoutput("id 3proxy")[20:23]
    uid = subprocess.getoutput("id 3proxy")[4:7]
    password = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))
    print("PASSWORD", password)

    with open(path, "w") as file:
        file.write("setgid " + gid + "\n")
        file.write("setuid " + uid + "\n")
        file.write("daemon\n")
        file.write("nserver 8.8.8.8\n")
        file.write("nserver 8.8.4.4\n")
        file.write("nscache 65536\n")
        file.write("auth strong\n")
        file.write("users default:CL:" + password + "\n")
        for i in range(addresses_amount):
            file.write("proxy -6 -s0 -n -a -p{0} -i{1} -e{2}\n".format(port, ipv4, addresses_list[i]))
            port += 1


def create_init(path):
    with open("/root/.bash_profile", "w") as file:
        file.write("ulimit -n 160000\n")

    with open(path, "w") as file:
        file.write("#!/bin/sh\n")
        file.write("#\n")
        file.write("### BEGIN INIT INFO\n")
        file.write("# Provides: 3Proxy\n")
        file.write("# Required-Start: $remote_fs $syslog\n")
        file.write("# Required-Stop: $remote_fs $syslog\n")
        file.write("# Default-Start: 2 3 4 5\n")
        file.write("# Default-Stop: 0 1 6\n")
        file.write("# Short-Description: Initialize 3proxy server\n")
        file.write("# Description: starts 3proxy\n")
        file.write("### END INIT INFO\n")
        file.write('case "$1" in\n')
        file.write("    start)\n")
        file.write("        echo Starting 3Proxy\n")
        file.write("        ulimit -n 160000\n")
        file.write("        for i in `cat /etc/3proxy/ipv6.list`; do\n")
        file.write("            ip addr add $i/{0} dev {1}\n".format(ipv6_netmask, dev_name))
        file.write("        done\n")
        file.write("        /usr/bin/3proxy /etc/3proxy/3proxy.cfg\n")
        file.write("    ;;\n")
        file.write("    stop)\n")
        file.write("        echo Stopping 3Proxy\n")
        file.write("        /usr/bin/killall 3proxy\n")
        file.write("    ;;\n")
        file.write("    restart|reload)\n")
        file.write("        echo Reloading 3Proxy\n")
        file.write("        /usr/bin/killall -s USR1 3proxy\n")
        file.write("    ;;")
        file.write("    *)")
        file.write('    echo Usage: \\$0 "{start|stop|restart}"\n')
        file.write("    exit 1\n")
        file.write("esac\n")
        file.write("exit 0\n")

    os.system("chmod +x /etc/init.d/3proxyinit")
    os.system("update-rc.d 3proxyinit defaults")


if __name__ == "__main__":
    dev_name = input("DEV : ")
    ipv4 = input("IPv4 : ")
    ipv6_prefix = input("IPv6 PREFIX : ") + ":"
    ipv6_netmask = int(input("IPv6 NETMASK : "))
    port = int(input("FIRST PORT : "))
    addresses_amount = int(input("ADDRESSES AMOUNT : "))

    addresses_list = list()

    download_app()
    generate_ipv6_file("/etc/3proxy/ipv6.list")
    generate_config("/etc/3proxy/3proxy.cfg")
    create_init("/etc/init.d/3proxyinit")

    os.system("chown 3proxy:3proxy -R /etc/3proxy")
    os.system("chown 3proxy:3proxy /usr/bin/3proxy")
    os.system("chmod 444 /etc/3proxy/3proxy.cfg")


'''
for i in $(seq 3231 4731); do
    iptables -I INPUT -p tcp -m tcp --dport $i -j DROP
    iptables -I INPUT -s 46.39.51.115/32 -p tcp -m tcp --dport $i -j ACCEPT
    iptables -I INPUT -s 185.18.54.137/32 -p tcp -m tcp --dport $i -j ACCEPT
    iptables -I INPUT -s 185.159.81.189/32 -p tcp -m tcp --dport $i -j ACCEPT
done
'''
