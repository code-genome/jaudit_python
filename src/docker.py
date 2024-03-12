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

class Docker:

    def getContainerList(self):
        cmd = ("docker", "ps", "--format", "{{.ID}}")
        return self.runpipe(cmd)

    def getImageList(self):
        cmd = ("docker", "images", "--format", "{{.ID}}")
        return self.runpipe(cmd)

    def getVolumeList(self):
        cmd = ("docker", "volume", "ls", "--format", "{{.Name}}|{{.Mountpoint}}")
        return self.runpipe(cmd)

    def runpipe(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines=[]
        if sys.version_info.major == 3:
            with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                for line in pin:
                    line = line.rstrip()
                    lines.append(line)
        else:
            for line in p.stdout:
                line = line.rstrip()
                lines.append(line)
        p.wait()
        return lines
                    
