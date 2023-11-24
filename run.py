import os
import argparse
import subprocess
import configparser
import time
import random
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

parser = argparse.ArgumentParser()
parser.add_argument('--gpu', type=int, default=0)
parser.add_argument('--check_file', type=str, default='check.txt')
parser.add_argument('--config_path', type=str, default='config.ini')
parser.add_argument('--port', type=int, default=20059)
parser.add_argument('--config_name', type=str, default=get_random_string(4))
args = parser.parse_args()

# 子进程脚本的名称
child_script = 'gpu_process.py'

env = os.environ.copy()
env['CUDA_VISIBLE_DEVICES'] = str(args.gpu)

# 初始化子进程
process = subprocess.Popen(['python', child_script], env=env)

# 指定要检查的文件路径
def get_file_path():
    file_path_to_check = args.check_file
    try:
        file_path_to_check = open(file_path_to_check, 'r').readlines()[0].strip()
    except:
        file_path_to_check = 'check.txt'
    return file_path_to_check

file_path_to_check = get_file_path()
print(file_path_to_check)

# NOTE: add function to launch sshd process. and function to read from a file to start frpc process.
config = configparser.ConfigParser()
config.read('/usr/local/bin/frp/frpc.ini')
new_config = configparser.ConfigParser()
new_config['common'] = config['common']
new_config[f'ssh-{args.config_name}'] = config['ssh']
new_config[f'ssh-{args.config_name}']['remote_port'] = str(args.port)
new_config.write(open('/usr/local/bin/frp/frpc.ini', 'w'))

subprocess.Popen(['cat', '/usr/local/bin/frp/frpc.ini'])
subprocess.Popen(['mkdir', '/run/sshd'])
subprocess.Popen(['mkdir', '-p', '/mnt/ceph_rbd/zbc'])
subprocess.Popen(['mkdir', '-p', '/mnt/ceph_rbd/zlt'])

subprocess.Popen(['useradd', '-m', '-d', '/mnt/ceph_rbd/zbc', 'zbc', '-s', '/bin/bash'])
zbc_p = subprocess.Popen(['passwd', 'zbc'], stdin=subprocess.PIPE)
stdout, stderr = zbc_p.communicate(input=b'asd4561515\nasd4561515\n')
print(f'zbc_p: {stdout}, {stderr}')

subprocess.Popen(['useradd', '-m', '-d', '/mnt/ceph_rbd/zlt', 'zlt', '-s', '/bin/bash'])
zlt_p = subprocess.Popen(['passwd', 'zlt'], stdin=subprocess.PIPE)
stdout, stderr = zlt_p.communicate(input=b'asd4561515\nasd4561515\n')
print(f'zlt_p: {stdout}, {stderr}')


sshd_process = subprocess.Popen(['/usr/sbin/sshd', '-D'])
frpc_process = subprocess.Popen(['/usr/local/bin/frp/frpc', '-c', '/usr/local/bin/frp/frpc.ini'])

# 主循环
while True:
    file_path_to_check = get_file_path()
    if os.path.exists(file_path_to_check):
        # 文件存在时，杀死子进程以释放 GPU
        process.kill()
        time.sleep(1)  # 等待进程完全关闭

        # 重新启动 GPU 占用子进程
        process = subprocess.Popen(['python', child_script], env=env)

    else:
        # 文件不存在时，确保子进程运行
        if process.poll() is not None:  # 如果子进程已经关闭
            process = subprocess.Popen(['python', child_script], env=env)
    
    if frpc_process.poll() is not None:
        frpc_process = subprocess.Popen(['/usr/local/bin/frp/frpc', '-c', '/usr/local/bin/frp/frpc.ini'])
    if sshd_process.poll() is not None:
        sshd_process = subprocess.Popen(['/usr/sbin/sshd', '-D'])

    time.sleep(1)  # 检查周期

