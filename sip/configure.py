import os
import glob
import sipconfig
import shutil
import numpy

modules = [('core',		['common', 'hardware', 'control']),
	   ('simulator',	[os.path.join('camera','simulator')]),
	   ('espia',		[os.path.join('camera','common','espia')]),
	   ('frelon',		[os.path.join('camera','frelon')]),
	   ('maxipix',		[os.path.join('camera','maxipix')])]

espiaModules = ['espia', 'frelon', 'maxipix']

rootDir = '..'
def rootName(fn):
    return os.path.join(rootDir, fn)
    
def findIncludes(baseDir):
    inclDirs = []
    for root, dirs, files in os.walk(baseDir):
        for dirname in dirs:
            if dirname == 'include':
                inclDirs.append(os.path.join(root,dirname))
    return inclDirs

def findModuleIncludes(name):
    for modName, modDirs in modules:
        if modName == name:
            modInclDirs = []
            for subDir in modDirs:
                modInclDirs += findIncludes(rootName(subDir))
            return modInclDirs
    return None

def main():
    excludeMods = set()

    confFile = open(rootName('config.inc'))
    for line in confFile:
	if line.startswith('export') : break
        line = line.strip('\n ')
        if line.startswith('COMPILE_'):
            var, value = line.split('=')
            try:
                value = int(value)
            except ValueError:
                continue
            if not value:
                excludeMods.add(var.split('_')[-1].lower())

    for modName, modDirs in modules:
        if modName in excludeMods:
            continue
    
        if os.path.exists(modName):
            if not os.path.isdir(modName):
                raise 'Error: %s exists and is not a directory' % modName
        else:
            os.mkdir(modName)

        os.chdir('%s' % modName)

        global rootDir
        rootDir = os.path.join('..',rootDir)
    
        sipFileNameSrc = "lima%s.sip" % modName
        if modName != 'core':
            sipFileNameIn = "../limamodules.sip.in"
            cmd = 'sed "s/%%NAME/%s/g" %s > %s' % (modName, sipFileNameIn,
                                                   sipFileNameSrc)
            os.system(cmd)

        sipFileName = "lima%s_tmp.sip" % modName
        shutil.copyfile(sipFileNameSrc, sipFileName)

        initNumpy = 'lima_init_numpy.cpp'
        shutil.copyfile(os.path.join('..',initNumpy), initNumpy)


        dirProcesslib = rootName(os.path.join('third-party','Processlib'))
        sipProcesslib = os.path.join(dirProcesslib,'sip')
        extraIncludes = ['.', '../core', sipProcesslib, numpy.get_include()]

        extraIncludes += findIncludes(dirProcesslib)
    
        coreDirs = modules[0][1]
        extraIncludes += findModuleIncludes('core')
    
        if (modName in espiaModules) and ('espia' not in excludeMods):
            espia_base = '/segfs/bliss/source/driver/linux-2.6/espia'
            espia_incl = os.path.join(espia_base,'src')
            extraIncludes += [espia_incl]
   
        extraIncludes += findModuleIncludes(modName)

        sipFile = open(sipFileName,"a")
        sipFile.write('\n')

        sipFile.write('%%Import %s/processlib_tmp.sip\n' % sipProcesslib)
    
        if modName != 'core':
            sipFile.write('%Import ../core/limacore_tmp.sip\n')
        if (modName in espiaModules) and (modName != 'espia'):
            sipFile.write('%Import ../espia/limaespia_tmp.sip\n')
            extraIncludes += findModuleIncludes('espia')

        for sdir in modDirs:
            srcDir = rootName(sdir)
            for root,dirs,files in os.walk(srcDir) :
                dir2rmove = excludeMods.intersection(dirs)
                for dname in dir2rmove:
                    dirs.remove(dname)
        
                for filename in files:
                    base,ext = os.path.splitext(filename)
                    if ext != '.sip':
                        continue
                    incl = os.path.join(root,filename)
                    sipFile.write('%%Include %s\n' % incl)

        sipFile.close()

        # The name of the SIP build file generated by SIP and used by the build
        # system.
        build_file = "lima%s.sbf" % modName
        config = sipconfig.Configuration()

        # Run SIP to generate the code.
        # module's specification files using the -I flag.
        cmd = " ".join([config.sip_bin,"-g", "-e","-c", '.',
                        "-b", build_file,sipFileName])
        print cmd
        os.system(cmd)

        #little HACK for adding source
        bfile = open(build_file)
        whole_line = ''
        for line in bfile :
            if 'sources' in line :
                begin,end = line.split('=')
                line = '%s = lima_init_numpy.cpp %s' % (begin,end)
            whole_line += line
        bfile.close()
        bfile = open(build_file,'w')
        bfile.write(whole_line)
        bfile.close()

        # We are going to install the SIP specification file for this module
        # and its configuration module.
        installs = []

        installs.append([sipFileNameSrc, os.path.join(config.default_sip_dir,
                                                      "lima")])

        installs.append(["limaconfig.py", config.default_mod_dir])

        # Create the Makefile.  The QtModuleMakefile class provided by the
        # pyqtconfig module takes care of all the extra preprocessor, compiler
        # and linker flags needed by the Qt library.
        makefile = sipconfig.ModuleMakefile(configuration=config,
                                            build_file=build_file,
                                            installs=installs,
                                            export_all = True)
        makefile.extra_include_dirs = extraIncludes
        makefile.extra_libs = ['pthread','lima%s' % modName]
        makefile.extra_lib_dirs = [rootName('build')]
        makefile.extra_cxxflags = ['-pthread', '-g']
        makefile.extra_cxxflags.extend(['-I' + x for x in extraIncludes])
        
        # Add the library we are wrapping.  The name doesn't include any 
        # platform specific prefixes or extensions (e.g. the "lib" prefix on 
        # UNIX, or the ".dll" extension on Windows).
        # None (for me)
        
        # Generate the Makefile itself.
        makefile.generate()

        # Now we create the configuration module.  This is done by merging a
        # Python dictionary (whose values are normally determined dynamically)
        # with a (static) template.
        content = {
            # Publish where the SIP specifications for this module will be
            # installed.
            "lima_sip_dir":    config.default_sip_dir
            }

        # This creates the lima<mod>config.py module from the limaconfig.py.in
        # template and the dictionary.
        sipconfig.create_config_module("lima%sconfig.py" % modName,
                                       "../limaconfig.py.in", content)

        os.chdir('..')
        rootDir = rootDir[3:]


if __name__ == '__main__':
    main()