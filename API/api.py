#!/usr/bin/python

import web
import sys
import os
try:
    import json
except ImportError:
    import simplejson as json

import fp

# Very simple web facing API for FP dist

urls = (
    '/query', 'query',
    '/query?(.*)', 'query',
    '/ingest', 'ingest',
)


class ingest:

    def POST(self):
        data = web.data()
        #print(data)
        tracks = json.loads(data)
        codes, bigeval, track_ids = self.parse_json_dump(tracks)
        #print("Codes est: '%s'" % codes)
        fp.ingest(codes, do_commit=True)
        return json.dumps({"track_ids":track_ids, "status":"ok"})

    def parse_json_dump(self, json_data):
        codes = json_data

        bigeval = {}
        fullcodes = []
	track_ids = []
        for c in codes:
            if "code" not in c:
                continue
            code = c["code"]
            m = c["metadata"]
            if "track_id" in m:
                trid = m["track_id"].encode("utf-8")
            else:
                trid = fp.new_track_id()
	    track_ids.append(trid)
            length = m["duration"]
            version = m["version"]
            artist = m.get("artist", None)
            title = m.get("title", None)
            release = m.get("release", None)
            youtube = m.get("youtube", None)
            characters = m.get("characters", None)
            decoded = fp.decode_code_string(code)
        
            bigeval[trid] = m
        
            data = {"track_id": trid,
                "fp": decoded,
                "length": length,
                "codever": "%.2f" % version
            }
            if artist: data["artist"] = artist
            if release: data["release"] = release
            if title: data["track"] = title
            if youtube: data["youtube"] = youtube
            if characters: data["characters"] = characters
            fullcodes.append(data)

        return (fullcodes, bigeval, track_ids)

class query:
    def POST(self):
        return self.GET()

    def GET(self):
        data = web.data()
        json_data = json.loads(data)
        response = fp.best_match_for_query(json_data['code'])
        print(response)
        return json.dumps({"ok":True, "query":json_data['code'], "message":response.message(), "match":response.match(), "score":response.score, \
                        "qtime":response.qtime, "track_id":response.TRID, "total_time":response.total_time, "metadata": response.metadata})

application = web.application(urls, globals())#.wsgifunc()

if __name__ == "__main__":
    application.run()

#if __name__ == "__main__":
#    if len(sys.argv) < 2:
#        print >>sys.stderr, "Usage: %s [-b] [json dump] ..." % sys.argv[0]
#        print >>sys.stderr, "       -b: write a file to disk for bigeval"
#        sys.exit(1)
    
#    write_bigeval = False
#    pos = 1
#    if sys.argv[1] == "-b":
#        write_bigeval = True
#        pos = 2
#    
#    for (i, f) in enumerate(sys.argv[pos:]):
#        print "%d/%d %s" % (i+1, len(sys.argv)-pos, f)
#        codes, bigeval = parse_json_dump(f)
#        fp.ingest(codes, do_commit=False)
#        if write_bigeval:
#            bename = "bigeval.json"
#            if not os.path.exists(bename):
#                be = {}
#            else:
#                be = json.load(open(bename))
#            be.update(bigeval)
#            json.dump(be, open(bename, "w"))
#    fp.commit()
