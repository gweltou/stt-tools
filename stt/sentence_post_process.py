#!/usr/bin/env python3

from stt import sentence_post_process_subs

def post_proc(text):
    if not text:
        return ''
    
    # web adresses
    if "HTTP" in text or "WWW" in text:
        text = text.replace("pik", '.')
        text = text.replace(' ', '')
        return text.lower()
    
    for sub in sentence_post_process_subs:
        text = text.replace(sub, sentence_post_process_subs[sub])
    
    splitted = text.split(maxsplit=1)
    splitted[0] = splitted[0].capitalize()
    return ' '.join(splitted)
