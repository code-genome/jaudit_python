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

class SysPackages:

    # RPM: rpm -qal --files-bypkg -> pkg filename
    # DPKG: dpkg -S 'glob'  ->  pkg: filename
    #
    @classmethod
    def get_file_names(cls, patterns):
        isDPKG=False
        isRPM=False
        isLPP=False
        cmd=None
        pkgtype=None
        if os.path.exists("/usr/bin/lslpp"):
            isLPP=True
            pkgtype='lpp'
            cmd=["/usr/bin/lslpp", "-f", "-c"]
        elif os.path.exists("/usr/bin/dpkg"):
            isDPKG=True
            pkgtype = 'deb'
            cmd=["/usr/bin/dpkg","-S","*"]
        elif os.path.exists("/usr/bin/rpm"):
            isRPM=True
            pkgtype='rpm'
            cmd=["/usr/bin/rpm", "-qal", "--files-bypkg"]
        else:
            return None, 0

        if sys.version_info.major == 3:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            
        lines=[]
        if sys.version_info.major == 3:
            with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                for line in pin:
                    lines.append(line.strip())
        else:
            for line in p.stdout:
                lines.append(line.strip())

        result = {}
        result[pkgtype] = {}

        counter = 0
        for rec in lines:
            if isDPKG:
                rec = rec.replace(':', ' ')
            while rec.find('  ') != -1:
                rec = rec.replace('  ',' ')
            if isLPP and rec[0] == '#':
                continue
            if isLPP:
                (pkg,file) = rec.split(':',2)[1:]
            else:
                (pkg,file) = rec.split(' ',1)
            for p in patterns:
                if re.search(p, file) is not None:
                    if pkg not in result[pkgtype]:
                        result[pkgtype][pkg] = []
                    result[pkgtype][pkg].append(file)
                    counter += 1
                    break

        return result, counter
