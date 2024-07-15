from config import log
from kindle_fun import refreshReadwiseDatabase
import json
log ("rebuilding database ⏳...")
refreshReadwiseDatabase()
log ("done 👍")
	

result= {"items": [{
    "title": "Done!" ,
    "subtitle": "ready to search now",
    "arg": "",
    "icon": {

            "path": "icons/done.png"
        }
    }]}
print (json.dumps(result))

