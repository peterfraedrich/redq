from redq import redq
import subprocess
import re
import time

pattern = re.compile(r'test\.py')


ramp = 50

for loop in range(ramp):
    print('concurrent:', loop)
    for proc in range(loop):
        subprocess.call('./test.py >> ramp.txt'.format(loop), shell=True)
    get_instances = subprocess.check_output(['ps', 'aux'])
    while True:
        if not pattern.findall(get_instances.decode('ascii')):
            break
        time.sleep(0.1)



