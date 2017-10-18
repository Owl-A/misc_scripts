"""
   Script to download course videos from nptel 
   corresponding to course code entered as the input
"""
import urllib, json, os

course = raw_input();  # 106102064 for data structures
resp = urllib.urlopen("http://nptel.ac.in/courses/"+ course +"/")
urllist = json.loads(resp.read().split("<script type=\"application/ld+json\">")[1].split("</script>")[0])["partOfEducationalTrack"]
os.system("mkdir nptel"+course)
for i in range(1,len(urllist)+1) :
	handle = urllib.FancyURLopener()
	if (i<10) :
		handle.retrieve("http://nptelvideos.nptel.ac.in/softlinks/106102064/lec0"+ str(i) + ".flv", "nptel"+course+"/"+str(i)+".flv")
	else :
		handle.retrieve("http://nptelvideos.nptel.ac.in/softlinks/106102064/lec"+ str(i) +".flv", "nptel"+course+"/"+str(i)+".flv")
