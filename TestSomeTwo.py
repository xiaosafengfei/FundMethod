import os
def ping_ip(ip):
    output = os.popen('ping -n 1 %s'%ip).readlines()
    for w in output:
        if w.find('TTL')>=0:
            print(ip)


if __name__ == '__main__':
    for num in range(1,255):
        ip = '10.0.246.' + str(num)
        ping_ip(ip)