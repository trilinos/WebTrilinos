import os
import os.path
import shutil
import sys
import StringIO
import ConfigParser

#Read output.txt generated by setup.html
outputCP = ConfigParser.ConfigParser()
if not os.path.isfile("output.txt"):
	print "Could not find output.txt. Please run the configuration setup and try again."
	sys.exit()
outputCP.read("output.txt")

#Read Makefile.export.Trilinos
includeFilePath = outputCP.get('header', 'BaseInstallDir') + '/include/Makefile.export.Trilinos'
if not os.path.isfile(includeFilePath):
	print "An error occured when trying to access a Trilinos installation in " + outputCP.get('header', 'BaseInstallDir') + "."
	print "Please check the installation directory in output.txt and try again."
	sys.exit()
includeFile = open(includeFilePath, 'r')

#Adding a fake header to the content of Makefile.export.Trilinos
#so that I can use ConfigParser to read it
includeStr = StringIO.StringIO()
includeStr.write('[header]\n')
includeStr.write(includeFile.read())
includeStr.seek(0, os.SEEK_SET)

includeCP = ConfigParser.ConfigParser()
includeCP.readfp(includeStr)

#Remove specified libraries
prelimRemovals = outputCP.get('header', 'LibRemovals').split()
removals = list()
invalidRemovals = list()
libstr = includeCP.get('header', 'Trilinos_LIBRARIES') + " " + includeCP.get('header', 'Trilinos_TPL_LIBRARIES') + " -lm"
for str in prelimRemovals:
	if not str == "":
		str += " "
		if not libstr.find(str) == -1:
			removals.append(str)
		else:
			invalidRemovals.append(str)
for str in removals:
	libstr.replace(str, "")
if len(invalidRemovals) > 0:
	print "The following libraries were not found in the installation of"
	print "Trilinos specified and were not removed. Please check your spelling."
	printstr = "\t"
	for str in invalidRemovals:
		printstr += str
	print printstr + "\n"

#Copy the existing config.php to a backup, if it exists
overwrittenPHP = False
if os.path.isfile("config.php"):
	shutil.copyfile("config.php", "config.php.bk")
	overwrittenPHP = True

config = open("config.php", "w")

#Write the new configuration to config.php
config.write("<?\n")
config.write("$WebTrilinosDirectory = \"" + outputCP.get('header', 'WebTrilinosDir') + "\";\n")
config.write("$HTMLImageDirectory = \""   + outputCP.get('header', 'HTMLImageDir') + "\";\n")
config.write("$TempDirectory = \""        + outputCP.get('header', 'TempDir') + "\";\n")

config.write("$INCLUDES = \""             + includeCP.get('header', 'Trilinos_INCLUDE_DIRS'))
if not includeCP.get('header', 'Trilinos_TPL_INCLUDE_DIRS') == "":
	config.write(" "                  + includeCP.get('header', 'Trilinos_TPL_INCLUDE_DIRS'))
config.write("\";\n")

config.write("$LDFLAGS = \""              + includeCP.get('header', 'Trilinos_LIBRARY_DIRS'))
if not includeCP.get('header', 'Trilinos_TPL_LIBRARY_DIRS') == "":
	config.write(" "                  + includeCP.get('header', 'Trilinos_TPL_LIBRARY_DIRS'))
config.write("\";\n")

config.write("$LIBS = \""                 + libstr + "\";\n")
config.write("$PYTHONPATH = \""           + outputCP.get('header', 'PythonDir') + "\";\n")
config.write("$CXX = \""                  + includeCP.get('header', 'Trilinos_CXX_COMPILER') + "\";\n")
config.write("$WebHost = \""              + outputCP.get('header', 'Web_Host') + "\";\n")
config.write("$HBMatrixDirectory = \""    + outputCP.get('header', 'WebTrilinosDir') + "/data/HB/\";\n")
config.write("$MMMatrixDirectory = \""    + outputCP.get('header', 'WebTrilinosDir') + "/data/MM/\";\n")
config.write("$XMLMatrixDirectory = \""   + outputCP.get('header', 'WebTrilinosDir') + "/data/XML/\";\n")
config.write("$ImageDirectory = \""       + outputCP.get('header', 'WebTrilinosDir') + "/tmp/\";\n")
config.write("$Password = \""             + outputCP.get('header', 'Pass') + "\";\n")
config.write("$MAX_PROCS = \""            + includeCP.get('header', 'Trilinos_MPI_EXEC_MAX_NUMPROCS') + "\";\n")
config.write("$MPIEXEC = \""              + includeCP.get('header', 'Trilinos_MPI_EXEC') + "\";\n")
config.write("$NUMPROCS_FLAG = \""        + includeCP.get('header', 'Trilinos_MPI_EXEC_NUMPROCS_FLAG') + "\";\n")
config.write("$CXX_COMPILER_FLAGS = \""   + includeCP.get('header', 'Trilinos_CXX_COMPILER_FLAGS') + "\";\n")
config.write("\n")
config.write("putenv('LD_LIBRARY_PATH=' . str_replace(\"-L\", \"\", str_replace(\" \", \":\", $LDFLAGS)));\n")
config.write("putenv('PYTHONPATH=' . $PYTHONPATH);\n")
config.write("?>")

print "Successfully generated config.php."
if overwrittenPHP:
	print "The previous config.php file has been saved as config.php.bk."
print ""

#Copy the existing config.py to backup, if it exists
overwrittenPY = False
if os.path.isfile("config.py"):
	shutil.copyfile("config.py", "config.py.bk")
	overwrittenPY = True

pyconfig = open("config.py", "w")

#Write the new configuration to config.py
pyconfig.write("MAX_MATRIX_ROWS = 256 * 256\n")
pyconfig.write("MAX_MATRIX_NONZEROS = 256 * 256 * 5\n")
pyconfig.write("MAX_ITERATIONS = 1550\n")
pyconfig.write("MAX_KSPACE = 60\n")
pyconfig.write("HB_REPOSITORY = \""  + outputCP.get('header', 'WebTrilinosDir') + "/data/HB\"\n")
pyconfig.write("MM_REPOSITORY = \""  + outputCP.get('header', 'WebTrilinosDir') + "/data/MM\"\n")
pyconfig.write("XML_REPOSITORY = \"" + outputCP.get('header', 'WebTrilinosDir') + "/data/XML\"\n")

print "Successfully generated config.py."
if overwrittenPY:
	print "The previous config.py file has been saved as config.py.bk."


#Close the files
includeFile.close()
config.close()
pyconfig.close()
