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

class JarName(JarIdentifier):

    myname="jar-name"
    
    def __init__(self):
        self.regex_map = Configuration.get_analytic_data('jar-name')['identifiers']
        self.reported_bad = set()

    @classmethod
    def priority(cls):
        return 5
        
    @classmethod
    def supported(cls):
        if Configuration.get_analytic_data(cls.myname):
            return True
        return False        

    @classmethod
    def initialize(cls):
        cls.config = Configuration.get_analytic_data('jar-name')
        if cls.config is None:
            return False
        cls.regex_map = cls.config['identifiers']
        return True
    
    def identify(self,inputHandle):
        names = set()
        names.add(inputHandle.getName())
        names.add(inputHandle.getDisplay())

        res = False

        for name in names:
            n = name.rfind("/")
            if n != -1:
                name = name[n+1:]
            name = name.lower()

            for rule in self.regex_map:
                regex = rule['regex']
                fmt = rule.get('format', '%1')

                try:
                    m = re.match(regex, name)
                except Exception:
                    if regex not in self.reported_bad:
                        errorOut("Malformed regular expression: {regex}\n")
                        self.reported_bad.add(regex)
                    continue
                if m is None:
                    continue

                pos = 0
                segments = [x for x in m.groups()]
                replacements = []
                for ndx,value in enumerate(segments,1):
                    var = '%' + str(ndx)
                    value = segments[ndx-1]
                    pos = 0
                    while True:
                        ndx = fmt.find(var, pos)
                        if ndx == -1:
                            break
                        replacements.append((value,ndx,ndx+len(var)))
                        pos = ndx + len(var)

                v = []
                pos = 0
                for value, start, end in replacements:
                    v.append(fmt[pos:start])
                    v.append(value)
                    pos = end
                v = "".join(v)

                nv = Version(v, self.myname)
                if State.addEvidence:
                    nv.addEvidence(self.myname, "Filename matched /"+regex+"/")
                inputHandle.addVersion(nv)
                res = True
                break
        
        return res

    @classmethod
    def get_name(cls):
        return cls.myname

    @classmethod
    def get_description(cls):
        return "Uses patterns to extract the version from the name of the jar file. This analytic is not robust against file renaming, and also can not detect when class files have been included directly in a larger project."
