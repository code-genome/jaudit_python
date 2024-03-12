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


class ClassGrouping:
    #
    # Tries to determine version from a group of unpackaged class files
    # which seem to belonog to the same package
    #
    def classPkgVersion(self,cpkg, inputHandle):
        '''Tries to determine version from a group of unpackaged class files
           which seem to belonog to the same package.  groupClassFiles can
           be used for the grouping.  The input is a list of class filenames.
        '''

        analytics=[]
        for a in State.analyticSet:
            name = a.get_name()
            if name in State.enabledAnalytics:
                analytics.append(a())

        State.currentJar.append(analytics)

        jc = JavaClass()
        for d in cpkg:
            for f in cpkg[d]:
                jcf = jc.loadFile(f)
                if jcf is None:
                    continue

                analytics = State.currentJar[-1]

                for a in analytics:
                    a.addClassFile(jcf)
                
        for a in analytics:
            a.identify(inputHandle)

        State.currentJar.pop()

    #
    # Group unpackaged class files by package name
    #
    def groupClassFiles(self,classes):
        '''Group unpackaged class files by package name

        Attempts to group the provide list of class names based on
        the packages they belong to.  They are also separated based
        on file system directory as well.  The returned value
        is a double dictionary.  The top level dictionary is keyed
        by directory name.  The second level is the package name.  This
        points to a list of classes.  So result[dir][pkgname] -> [classes].
        '''


        pkginfo={}
        jc = JavaClass()
        for cn in classes:
            try:
                cf = jc.loadFile(cn)
                pkg = cf.getPackageName()
                if pkg is None:
                    pkg="<none>/"
                if pkg not in pkginfo:
                    pkginfo[pkg] = []
                pkginfo[pkg].append(cn)
            except:
                pass

        pkgs={}
        for pkg in pkginfo:
            p = pkg.split('/')
            pname=None
            depth=0
            for x in range(0,len(p)):
                s = '/'.join(p[0:x])
                if s not in pkginfo:
                    pname = s
                    depth = 0
                else:
                    break
            if pname not in pkgs:
                pkgs[pname] = []
            for x in pkginfo[pkg]:
                pkgs[pname].append(x)

        pkgdir={}
        for pkg in pkgs:
            for f in pkgs[pkg]:
                n = f.find(pkg)
                if n == -1:
                    dirname="/"
                else:
                    dirname=f[0:n]
                if dirname not in pkgdir:
                    pkgdir[dirname] = {}
                if pkg not in pkgdir[dirname]:
                    pkgdir[dirname][pkg] = []
                pkgdir[dirname][pkg].append(f)

        return pkgdir
