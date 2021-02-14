import os
import optparse
import sys
from samples.samples import *

cshname = "condorrun_tauwp.csh"
split = 50

def DoesSampleExist(samplename):
    if samplename+".txt" not in os.listdir("../../crab/macros/files/"):
        return False
    else:
        return True

def AreAllCondored(samplename):
    storelist = [line for line in open("../../crab/macros/files/"+samplename+".txt")]
    try:
        condoredlist = os.listdir(path+samplename)
    except:
        condoredlist = []

    if samplename+"_merged.root" in condoredlist:
        condoredlist.remove(samplename+"_merged.root")
    if samplename+".root" in condoredlist:
        condoredlist.remove(samplename+".root")

    lenstore = len(storelist)

    if 'Data' in samplename:
        #print "lenstore:", lenstore
        #print "lenstore/split:", lenstore/split, "\tlenstore%split:", lenstore%split
        remainder = lenstore%split
        lenstore = lenstore/split
        if remainder > 0:
            lenstore += 1
        #print lenstore, remainder

    '''
    sorted_condoredlist=[]
    if len(condoredlist) > 0:
        for k in range(len(storelist)):
            for n in condoredlist:
                if "_part"+str(k)+".root" in n:
                    sorted_condoredlist.append(n)
                    break
                else:
                    continue
    '''

    if len(condoredlist) < lenstore:
        print "condored: ", len(condoredlist), "\tlenstore: ", lenstore
        return False
    elif lenstore==0 and len(condoredlist)==0:
        print "Warning for", samplename, "False flag for crabbed files! need to recrab them"
        return True
    else:
        return True

usage = 'python SetAndLaunchCondorRun.py -y year -j wp_jet -m wp_mu -e wp_ele -f folder --max max_jobs -c -d dataset'
parser = optparse.OptionParser(usage)
parser.add_option('-y', dest='year', type=str, default = '2017', help='Please enter a year, default is 2017')
parser.add_option('-j', dest='jetwp', type=str, default = 'VT', help='Please enter a TauID WP for vsJet')
parser.add_option('-m', dest='muwp', type=str, default = 'L', help='Please enter a TauID WP for vsMu')
parser.add_option('-e', dest='elewp', type=str, default = 'VL', help='Please enter a TauID WP for vsEle')
parser.add_option('-f', dest='fold', type=str, default = 'v30', help='Please enter a folder')
parser.add_option('--max', dest='maxj', type=int, default = 0, help='Please enter a maximum for number of condor jobs')
parser.add_option('-c', dest='check', default = False, action='store_true', help='Default executes condorrun')
parser.add_option('-d', dest='dat', type=str, default = 'all', help='Default is all')

(opt, args) = parser.parse_args()

vsJet_dict = {"VVVL": '1',
              "VVL": '2',
              "VL": '4',
              "L": '8',
              "M": '16',
              "T": '32',
              "VT": '64',
              "VVT": '128',
}

vsMu_dict = {"VL": '1',
             "L": '2',
             "M": '4',
             "T": '8'
}

vsEle_dict = {"VVVL": '1',
              "VVL": '2',
              "VL": '4',
              "L": '8',
              "M": '16',
              "T": '32',
              "VT": '64',
              "VVT": '128',
}

#username = str(os.environ.get('USER'))
#inituser = str(os.environ.get('USER')[0])

#print username

if opt.fold == '':
    folder = "Eff_Jet" + opt.jetwp + "_Mu" + opt.muwp + "_Ele" + opt.elewp
else:
    folder = opt.fold

path = "VBS/" + folder + "/"
#path = "/eos/home-" + inituser + "/" + username + "/VBS/nosynch/" + folder + "/"
#print folder, path

if not os.path.exists(path):
    os.makedirs(path)

optstring = " -f " + folder + " --wp " + str(opt.jetwp + opt.muwp + opt.elewp)
if opt.maxj > 0:
    optstring = optstring + " --max " + str(opt.maxj)
optstring = optstring + "\n"

f = open(cshname, "w")

dirlist = [dirs for dirs in os.listdir(path) if os.path.isdir(path+dirs)]



for prname, proc in class_dict.items():
    if "Fake" in prname:
        continue
    if "DataHT" in prname or 'DataMET' in prname:
        continue
    if opt.year not in prname:
        continue

    toLaunch = True

    if hasattr(proc, 'components'):
        for sample in proc.components:
            if "Fake" in sample.label:
                continue
            if opt.dat != 'all':
                if not (str(sample.label).startswith(opt.dat) or prname.startswith(opt.dat)):
                    continue
            if not DoesSampleExist(sample.label):
                continue
                #if sample.label in dirlist:
            if not AreAllCondored(sample.label):
                if opt.check:
                    print sample.label, "not completely condored"
                else:
                    if os.path.exists(path+sample.label):
                        print "Setting jobs for missing condored files..."
                        #os.system("rm -r "+ path + sample.label + "/*")
                    print "Writing " + sample.label + " in csh..."
                    f.write("python submit_condor.py -d " + sample.label+ " " + optstring)
            else:
                print sample.label, " completely condored"

    else:
        if opt.dat != 'all':
            if not prname.startswith(opt.dat):
                continue
        if not DoesSampleExist(prname):
            continue
        if not AreAllCondored(proc.label):
            if opt.check:
                print proc.label, "not completely condored"
            else:
                if os.path.exists(path+proc.label):
                    print "Setting jobs for missing condored files..."
                    #os.system("rm -f "+ path + proc.label + "/*")
                print "Writing " + proc.label + " in csh..."
                f.write("python submit_condor.py -d " + proc.label+ " " + optstring)
        else:
            print proc.label, " completely condored"
f.close()

if not opt.check:
    t = open("CutsAndValues_bu.py", "w")
    t.write("# In this file values for cuts and constant will be stored and then recalled from the whole analysis function\n")
    t.write("#Using nanoAOD version 102X\n")
    t.write("ONLYELE=1\n")
    t.write("ONLYMU=0\n\n")

    t.write("PT_CUT_MU=  35\n")
    t.write("ETA_CUT_MU= 2.4\n")
    t.write("ISO_CUT_MU= 0.15\n\n")

    t.write("PT_CUT_ELE=  35\n")
    t.write("ETA_CUT_ELE= 2.4\n")
    t.write("ISO_CUT_ELE= 0.08\n\n")

    t.write("REL_ISO_CUT_LEP_VETO_ELE=   0.1\n")
    t.write("PT_CUT_LEP_VETO_ELE=        15\n")
    t.write("ETA_CUT_LEP_VETO_ELE=       2.4\n")
    t.write("REL_ISO_CUT_LEP_VETO_MU=    0.25\n")
    t.write("PT_CUT_LEP_VETO_MU=         10\n")
    t.write("ETA_CUT_LEP_VETO_MU=        2.4\n\n")

    t.write("DR_OVERLAP_CONE_TAU=        0.5\n")
    t.write("DR_OVERLAP_CONE_OTHER=      0.4\n\n")

    t.write("PT_CUT_JET= 30\n")
    t.write("ETA_CUT_JET=5\n\n")

    t.write("DELTAETA_JJ_CUT=2.5\n\n")

    #t.write("#btag info: l 13 skimtree_utils.BTAG_ALGO='CSVv2'   #CSVv2, DeepCSV, DeepFLV\n")
    t.write("BTAG_PT_CUT =   30\n")
    t.write("BTAG_ETA_CUT=   5\n")
    t.write("BTAG_ALGO   =   'DeepFlv'\n")
    t.write("BTAG_WP     =   'M'\n")
    t.write("ID_TAU_RECO_DEEPTAU_VSJET=  " + vsJet_dict[opt.jetwp] + " #byDeepTau2017v2p1VSjet ID working points (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight\n")
    t.write("ID_TAU_RECO_DEEPTAU_VSELE=  " + vsEle_dict[opt.elewp] + "  #byDeepTau2017v2p1VSe ID working points (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight\n")
    t.write("ID_TAU_RECO_DEEPTAU_VSMU=   " + vsMu_dict[opt.muwp] + "  #byDeepTau2017v2p1VSmu ID working points (deepTau2017v2p1): bitmask 1 = VLoose, 2 = Loose, 4 = Medium, 8 = Tight\n")
    t.write("ID_TAU_RECO_MVA=            8 #IsolationMVArun2v1DBoldDMwLT ID working point (2017v1): bitmask 1 = VVLoose, 2 = VLoose, 4 = Loose, 8 = Medium, 16 = Tight, 32 = VTight, 64 = VVTight\n")
    t.write("ID_TAU_ANTIMU=              1 #Anti-muon discriminator V3: : bitmask 1 = Loose, 2 = Tight\n")
    t.write("ID_TAU_ANTIELE=             2 #Anti-electron MVA discriminator V6 (2015): bitmask 1 = VLoose, 2 = Loose, 4 = Medium, 8 = Tight, 16 = VTight\n")
    t.write("PT_CUT_TAU=30\n")
    t.write("ETA_CUT_TAU=2.4\n")
    t.write("M_JJ_CUT=   500\n")
    t.write("MET_CUT=    40\n")
    t.close()

    print "Launching jobs on condor..."
    os.system("source ./" + cshname)
    print "Done! Goodbye my friend :D"
