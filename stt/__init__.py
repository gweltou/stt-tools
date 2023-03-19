
sentence_post_process_subs = dict()
_substitution_file = "subs.txt"

with open(__file__.replace("__init__.py", _substitution_file), 'r') as f:
    for l in f.readlines():
        l = l.strip()
        if l and not l.startswith('#'):
            k, v = l.split('\t')
            sentence_post_process_subs[k] = v