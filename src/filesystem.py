##
## This code is part of the Jaudit utilty.
##
## (C) Copyright IBM 2023.
##
## This code is licensed under the Apache License, Version 2.0. You may
## obtain a copy of this license in the LICENSE.txt file in the root directory
## of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
##
## Any modifications or derivative works of this code must retain this
## copyright notice, and modified files need to carry a notice indicating
## that they have been altered from the originals.
##


class FileSystem:

    def getFileSystems(self, filter=None, invert=False):
        res = []
        platform = os.sys.platform
        if platform[0:5] == 'win32':
            p = subprocess.Popen(["C:\\Windows\\System32\\wbem\\WMIC.exe","logicaldisk","get","deviceid,drivetype"], stdout=subprocess.PIPE)
            psout=[]
            if sys.version_info.major == 3:
                with TextIOWrapper(p.stdout) as pin:
                    for line in pin:
                        psout.append(line)
            else:
                for line in p.stdout:
                    psout.append(line)

            header = psout[0]

            columns={}

            start=0
            foundSpace=False
            for n in range(0,len(header)):
                if header[n] == ' ':
                    if not foundSpace:
                        name = header[start:n]
                    foundSpace = True
                elif foundSpace:
                    columns[name]=(start,n-1)
                    start = n
                    foundSpace=False

            for line in psout[1:]:
                fields={}
                for fname in columns:
                    (s,e) = columns[fname]
                    val = line[s:e]
                    val = val.rstrip()
                    fields[fname] = val
                t = fields['DriveType']
                mtpoint = fields['DeviceID']+'\\'
                type='unknown'
                if t == '1':
                    type = 'no-root-dir'
                elif t == '2':
                    type = 'removable-disk'
                elif t == '3':
                    type = 'fixed-local-disk'
                elif t == '4':
                    type = 'network-drive'
                elif t == '5':
                    type = 'cdrom'
                elif t == '6':
                    type = 'ramfs'
                keep = False
                
                if filter is None or type in filter:
                    keep = True
                if invert:
                    keep = not keep
                if keep:
                    res.append(mtpoint)
            p.wait()
            return res
            
        if os.path.exists("/etc/mtab") and os.path.getsize("/etc/mtab") != 0:
            with open('/etc/mtab') as file:
                for line in file:
                    line = line.rstrip()
                    dev, mtpoint, type = line.split(' ')[0:3]
                    keep = False
                    if filter is None or type in filter:
                        keep = True
                    if invert:
                        keep = not keep
                    if keep:
                        mtpoint = mtpoint.replace('\\040', ' ')
                        res.append(mtpoint)
        else:
            mount=None
            for b in ["/bin/mount", "/sbin/mount", "/usr/bin/mount", "/usr/sbin/mount"]:
                if os.path.exists(b):
                    mount=b
                    break
            if mount is None:
                return None
            p = subprocess.Popen([mount], stdout=subprocess.PIPE)
            lines = []
            if sys.version_info.major == 3:
                with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                    for line in pin:
                        lines.append(line)
            else:
                for line in p.stdout:
                    lines.append(line)
            isAIX=False
            if os.sys.platform[0:3] == "aix":
                isAIX = True
            for line in lines:
                line = line.rstrip()
                line = line.strip()
                while line.find('  ') != -1:
                    line = line.replace('  ',' ')
                f = line.split(" ")
                if isAIX:
                    if f[0][0] == '-':
                        continue
                    if f[0] == "node":
                        continue
                    mtpoint = f[1]
                    type = f[2]
                else:
                    mtpoint = f[2]
                    type = f[4]

                keep = False
                if filter is None or type in filter:
                    keep = True
                if invert:
                    keep = not keep
                if keep:
                    res.append(mtpoint)

                
            p.wait()
        return res


    def walkFileSystem(self, start, stop=None, match=None):
        for dir in start:
            for path, subdirs, files in os.walk(os.path.normpath(dir)):
                if stop is not None:
                    for n in subdirs:
                        if path[-1] == '/':
                            pn = path + n
                        else:
                            pn = path + '/' + n
                        if pn in stop:
                            subdirs.remove(n)

                for f in files:
                    keep = True
                    if match is not None:
                        if not match(f):
                            keep = False
                        if keep:
                            yield (path, f)

