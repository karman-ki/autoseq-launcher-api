import paramiko
import time

#ip_address = "130.229.58.140"
ip_address = "anchorage.meb.ki.se"
username = "prosp"
password = "16Vinter16"

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=ip_address,username=username, password=password)

print("Successful connection", ip_address)
ssh_client.invoke_shell()

'''
session.invoke_shell()
session.sendall('source /nfs/PROBIO/liqbio-dotfiles/.bash_profile \n')
session.sendall('autoseq liqbio-prepare --help \n')

while (session.recv_ready()):
    print(str(session.recv(1024)))

'''
command = {
        1:'source /nfs/PROBIO/liqbio-dotfiles/.bash_profile; autoseq liqbio-prepare --help'
}

for key,value in command.items():
    stdin,stdout,stderr=ssh_client.exec_command(value, get_pty=True)
    outlines=stdout.readlines()
    result=''.join(outlines)
    print (result)

ssh_client.close()
