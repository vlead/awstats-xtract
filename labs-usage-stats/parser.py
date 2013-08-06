#!/usr/bin/python

# This is a python script to parse awstats monthly data 
# and generate labs usage at lab level and experiment
# level.
#
# Input: awstats data file (passed as an argument)
# Output: pipe separated data 
#
#

import re, sys

### Mapping for courses ###
cMapping = {}
cMapping["cse01"] = "Data Structures"
cMapping["cse02"] = "Computer Programming"
cMapping["cse04"] = "Problem Solving"
cMapping["cse05"] = "PoPL"
cMapping["cse07"] = "Databases"
cMapping["cse08"] = "Software Engineering"
cMapping["cse09"] = "Linux"
cMapping["cse10"] = "Computer Organization & Arch."
cMapping["cse11"] = "Computer Systems Organization"
cMapping["cse17"] = "Mobile Robotics"
cMapping["cse15"] = "Digital Logic Design"
cMapping["cse18"] = "Computer Graphics"
cMapping["cse19"] = "Image Processing"
cMapping["cse06"] = "Data Mining"
cMapping["cse14"] = "VLSI"
cMapping["cse20"] = "Pattern Recognition"
cMapping["cse12"] = "FPGA Embedded System"
cMapping["cse29"] = "Cryptography"
cMapping["cse22"] = "Artificial Neural Networks"
cMapping["cse13"] = "Advanced VLSI"
cMapping["cse28"] = "Advanced Network Technologies"
cMapping["cse30"] = "Analog CMOS VLSI Circuit"
cMapping["cse16"] = "Speech Signal Processing"
cMapping["cse24"] = "Natural Language Processing"
cMapping["ccnsb01"] = "Molecular Flourescence Spectroscopy"
cMapping["ccnsb02"] = "Colloid & Surface Chemistry"
cMapping["ccnsb03"] = "Molecular Absorption Spectroscopy"
cMapping["ccnsb04"] = "Quantum Chemistry"
cMapping["ccnsb05"] = "Circular Dichroism Spectroscopy"
cMapping["ccnsb06"] = "Physical Chemistry"
cMapping["ccnsb07"] = "Molecular Interactions"
cMapping["eerc01"] = "Basic Engg Mechanics & Strength ..."
cMapping["eerc02"] = "Soil Mechanics & Foundation Engg"
cMapping["eerc03"] = "Hydraulics & Fluid Mechanics"
cMapping["eerc04"] = "Basic Structural Analysis"
cMapping["eerc05"] = "Geotechnical Engg"
cMapping["emt"] = "Electromagnetic Theory"


### Mappings for experiments ###
mapping = {}
mapping["cse11"] = {}
mapping["cse11"]["/labs/cse11/Integers/"] = "exp1"
mapping["cse11"]["/labs/cse11/FloatingPointNumbers/"] = "exp2"
mapping["cse11"]["/labs/cse11/CacheOrganizations/"] = "exp3"
mapping["cse11"]["/labs/cse11/LocalityAnalysis/"] = "exp4"
mapping["cse11"]["/labs/cse11/TilingMatrix/"] = "exp5"
mapping["cse11"]["/labs/cse11/VirtualMemory/"] = "exp6"
mapping["cse11"]["/labs/cse11/MIPS1/"] = "exp7"
mapping["cse11"]["/labs/cse11/MIPS2/"] = "exp8"
mapping["cse11"]["/labs/cse11/ARM1/"] = "exp9"
mapping["cse11"]["/labs/cse11/ARM2/"] = "exp10"
mapping["cse11"]["/labs/cse11/SingleCycle/"] = "exp11"
mapping["cse17"] = {}
mapping["cse17"]["/labs/cse17/sensormodelling/"] = "exp1"
mapping["cse17"]["/labs/cse17/velocitymodelling/"] = "exp2"
mapping["cse17"]["/labs/cse17/mapping/"] = "exp3"
mapping["cse17"]["/labs/cse17/localization/"] = "exp4"
mapping["cse17"]["/labs/cse17/gridbasednavigation/"] = "exp5"
mapping["cse17"]["/labs/cse17/forwardkinematics/"] = "exp6"
mapping["cse17"]["/labs/cse17/scanmatching/"] = "exp7"
mapping["cse17"]["/labs/cse17/rrtbasedpathplanning/"] = "exp8"
mapping["cse17"]["/labs/cse17/exploration/"] = "exp9"
mapping["cse17"]["/labs/cse17/montecarlolocalization/"] = "exp10"
mapping["eerc03"] = {}
mapping["eerc03"]["/labs/eerc03/exp5/"] = "exp2"
mapping["eerc03"]["/labs/eerc03/exp6/"] = "exp3"
mapping["eerc03"]["/labs/eerc03/exp7/"] = "exp4"
mapping["eerc03"]["/labs/eerc03/exp8/"] = "exp5"
mapping["eerc03"]["/labs/eerc03/exp9/"] = "exp6"
mapping["eerc03"]["/labs/eerc03/exp10/"] = "exp7"
mapping["eerc03"]["/labs/eerc03/exp11/"] = "exp8"
mapping["eerc03"]["/labs/eerc03/exp12/"] = "exp9"
mapping["eerc03"]["/labs/eerc03/exp13/"] = "exp10"
mapping["ccnsb02"] = {}
mapping["ccnsb02"]["/labs/ccnsb02/exp14/"] = "exp4"
mapping["ccnsb02"]["/labs/ccnsb02/exp4/"] = "exp5"
mapping["ccnsb02"]["/labs/ccnsb02/exp5/"] = "exp6"
mapping["ccnsb02"]["/labs/ccnsb02/exp15/"] = "exp7"
mapping["ccnsb02"]["/labs/ccnsb02/exp7/"] = "exp8"
mapping["ccnsb02"]["/labs/ccnsb02/exp8/"] = "exp9"
mapping["ccnsb02"]["/labs/ccnsb02/exp13/"] = "exp10"
mapping["cse29"] = {}
mapping["cse29"]["/labs/cse29/exp5/"] = "exp4"
mapping["cse29"]["/labs/cse29/exp6/"] = "exp5"
mapping["cse29"]["/labs/cse29/exp7/"] = "exp6"
mapping["cse29"]["/labs/cse29/exp8/"] = "exp7"
mapping["cse29"]["/labs/cse29/exp9/"] = "exp8"
mapping["cse29"]["/labs/cse29/exp10/"] = "exp9"
mapping["cse29"]["/labs/cse29/exp11/"] = "exp10"
mapping["cse18"] = {}
mapping["cse18"]["/labs/cse18/exp5a/"] = "exp5"
mapping["cse18"]["/labs/cse18/exp5b/"] = "exp6"
mapping["cse18"]["/labs/cse18/exp6/"] = "exp7"
mapping["cse18"]["/labs/cse18/exp7/"] = "exp8"
mapping["cse18"]["/labs/cse18/exp8/"] = "exp9"
mapping["cse18"]["/labs/cse18/exp9/"] = "exp10"
mapping["cse18"]["/labs/cse18/exp10/"] = "exp11"



try: 
    f = open(sys.argv[1], 'r').readlines()
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)

def pathFilter(line):
	pieces = line.split()
	if pieces[0][0] == '/'  and pieces[0][-1] == '/' and pieces[0].count("/") == 3:
		return True
	if pieces[0][0] == '/'  and pieces[0][-1] == '/' and pieces[0].count("/") == 4 and re.match("exp\d+", pieces[0].split("/")[3]):
		return True
	if pieces[0][0] == '/'  and pieces[0][-1] == '/' and len(pieces[0].split("/")) > 2 and pieces[0].split("/")[2] in mapping:
		for exp in mapping[pieces[0].split("/")[2]]:
			if pieces[0] == exp:
				return True
	return False
i = 0
for line in f:
	if line.startswith('# URL - Pages - Bandwidth - Entry - Exit'):
		startingPoint = i
		break
	i+=1
for line in f[startingPoint:]:
	if line.startswith("BEGIN_SIDER"):
		startingPoint = i
	i+=1

labs = {}
newList = filter(pathFilter, f[startingPoint + 1:])
for line in newList:
	line = line.split()
	path = line[0].split("/")
	count = int(line[1])
	if path[2] not in labs:
		labs[path[2]] = {}
		labs[path[2]]["All Count"] = 0
	if len(path) > 4:
		if path[2] in mapping and "/labs/"+path[2]+"/"+path[3]+"/" in mapping[path[2]]:
			path[3] = mapping[path[2]]["/labs/"+path[2]+"/"+path[3]+"/"]
		if path[3] not in labs[path[2]]:
			labs[path[2]][path[3]] = count
		else:
			labs[path[2]][path[3]] += count	
	else:
		labs[path[2]]["All Count"] += count

experiments  = ["All Count"]
for i in range(1,16):
	experiments.append("exp" + str(i))
#print labs
print """| Lab name | All Visits | Exp 1 | Exp 2 | Exp 3 | Exp 4 | Exp 5 | Exp 6 | Exp 7 | Exp 8 | Exp 9 | Exp 10 | Exp 11 | Exp 12 | Exp 13 | Exp 14 | Exp 15 |
|----------+------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+--------+--------+--------+--------+--------+--------|"""
for lab in labs:
	if lab in cMapping:
		print	"| " + cMapping[lab] + "|",
	else:	
		print	"| " + lab + "|",
	for exp in experiments:
		if exp in labs[lab]:
			print labs[lab][exp],
		print "|",
	print ""
		
		

