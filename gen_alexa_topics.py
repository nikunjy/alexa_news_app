import json

GLOBAL_DATA = []


def _add_nyt_topics():
    with open("NYT_TOPICS") as f:
        data = f.readlines()
        for d in data:
            GLOBAL_DATA.append(d.strip())


def _get_topic_mapping():
    data = {}
    with open("topic_mapping") as f:
        data = json.load(f)
    for topic in data:
        for mapping in data.get(topic):
            GLOBAL_DATA.append(mapping)



_add_nyt_topics()
_get_topic_mapping()

write_file = open("LIST_OF_TOPICS", "w")
for data in GLOBAL_DATA:
    write_file.write("%s\n" % data)
write_file.flush()
write_file.close()
