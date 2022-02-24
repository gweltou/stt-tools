#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    File : wavesplit.py
    
    
    Create a split file (time segments) from an audio file
    Convert audio file to correct format (wav mono 16kHz) if needed
    UI to listen and align audio segments with sentences in text file
    
    
    Author:        Gweltaz Duval-Guennoc 
"""


import sys
import os
import re
#from math import floor, ceil
#from pydub import AudioSegment
#import librosa
#from libMySTT import *

from wavsplit import *

import tkinter as tk
from tkinter.font import Font


class Pad(tk.Frame):

	# constructor to add buttons and text to the window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.toolbar = tk.Frame(self, bg="#eee")
        self.toolbar.pack(side="top", fill="x")
        
        # this will add Highlight button in the window
        self.bold_btn = tk.Button(self.toolbar, text="Highlight", command=self.highlight_text)
        self.bold_btn.pack(side="left")

        # this will add Clear button in the window
        self.clear_btn = tk.Button(self.toolbar, text="Clear", command=self.clear)
        self.clear_btn.pack(side="left")

        pw = tk.PanedWindow(self)
        pw.pack(side="bottom", fill="both", expand=True)
        
        # adding the utterance panel
        self.canvas = tk.Canvas(pw, bg="#fee")
        pw.add(self.canvas)
        
        #https://blog.teclado.com/tkinter-scrollable-frames/
        self.scrollable_frame = tk.Frame(self.canvas)
        #self.scrollable_frame.pack(expand=True, fill='both')
        #pw.add(self.scrollable_frame)
        #self.scrollbar = tk.Scrollbar(pw, orient='vertical', command=self.canvas.yview)
        
        x = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags=("inner_frame",))
        #self.canvas.configure(yscrollcommand=self.scrollbar.set)    # Updates scrollbar position
        
        self.canvas.bind("<Enter>", self.enableScrollCanvas)
        self.canvas.bind("<Leave>", self.disableScrollCanvas)
        self.canvas.bind("<Configure>", self.resize_utterances_panel)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Adding raw text panel
        self.raw_text = tk.Text(pw, wrap='word')
        self.raw_text.insert("end", "Hello world !")
        pw.add(self.raw_text)
        
        #self.raw_text.pack(side="right", expand=True, fill="both")
        #self.scrollbar.pack(side='right', fill='both')
        #self.canvas.pack(side='left', fill='both')
		
        #configuring a tag called start
        #self.text.tag_configure("hl", background="black", foreground="red")

    
    def enableScrollCanvas(self, e):
        self.bind_all("<MouseWheel>", self.scrollCanvas)
        self.bind_all("<Button-4>", self.scrollCanvas)
        self.bind_all("<Button-5>", self.scrollCanvas)
    
    def disableScrollCanvas(self, e):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
    
    def scrollCanvas(self, e):
        if e.num == 4:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
        elif e.num == 5: # Scroll down
            self.canvas.yview_scroll(1, "units")


    def resize_utterances_panel(self, e):
        #self.scrollable_frame.config(width=e.width)
        self.canvas.itemconfigure("inner_frame", width=e.width)
        

	# method to highlight the selected text
    def highlight_text(self):
        # if no text is selected then tk.TclError exception occurs
        try:
            self.text.tag_add("hl", "sel.first", "sel.last")		
        except tk.TclError:
            pass

	# method to clear all contents from text widget.
    def clear(self):
        self.text.tag_remove("hl", "1.0", "end")
    
    
    def count_total_nb_lines(self, textWidget):
        # Get Text widget content and split it by unbroken lines
        textLines = textWidget.get("1.0", "end-1c").split("\n")
        # Get Text widget wrapping style
        wrap = textWidget.cget("wrap")
        if wrap == "none":
            return len(textLines)
        else:
            # Get Text widget font
            font = Font(root, font=textWidget.cget("font"))
            totalLines_count = 0
            maxLineWidth_px = textWidget.winfo_width() - 2*textWidget.cget("padx") - 1
            for line in textLines:
                totalLines_count += self.count_nb_wrapped_lines_in_string(line,
                                                    maxLineWidth_px, font, wrap)
            return totalLines_count

    def count_nb_wrapped_lines_in_string(self, string, maxLineWidth_px, font, wrap):
        wrappedLines_count = 1
        thereAreCharsLeftForWrapping = font.measure(string) >= maxLineWidth_px
        while thereAreCharsLeftForWrapping:
            wrappedLines_count += 1
            if wrap == "char":
                string = self.remove_wrapped_chars_from_string(string, 
                                                        maxLineWidth_px, font)
            else:
                string = self.remove_wrapped_words_from_string(string, 
                                                        maxLineWidth_px, font)
            thereAreCharsLeftForWrapping = font.measure(string) >= maxLineWidth_px
        return wrappedLines_count

    def remove_wrapped_chars_from_string(self, string, maxLineWidth_px, font):
        avgCharWidth_px = font.measure(string)/float(len(string))
        nCharsToWrap = int(0.9*maxLineWidth_px/float(avgCharWidth_px))
        wrapLine_isFull = font.measure(string[:nCharsToWrap]) >= maxLineWidth_px
        while not wrapLine_isFull:
            nCharsToWrap += 1
            wrapLine_isFull = font.measure(string[:nCharsToWrap]) >= maxLineWidth_px
        return string[nCharsToWrap-1:]

    def remove_wrapped_words_from_string(self, string, maxLineWidth_px, font):
        words = string.split(" ")
        nWordsToWrap = 0
        wrapLine_isFull = font.measure(" ".join(words[:nWordsToWrap])) >= maxLineWidth_px
        while not wrapLine_isFull:
            nWordsToWrap += 1
            wrapLine_isFull = font.measure(" ".join(words[:nWordsToWrap])) >= maxLineWidth_px
        if nWordsToWrap == 1:
            # If there is only 1 word to wrap, this word is longer than the Text
            # widget width. Therefore, wrapping switches to character mode
            return self.remove_wrapped_chars_from_string(string, maxLineWidth_px, font)
        else:
            return " ".join(words[nWordsToWrap-1:])
    
    
    
    def load_split_file(self, filename):
        text_filename = filename.replace('.split', '.txt')
        
        #self.raw_text.pack_forget()
        #self.canvas.pack_forget()
        #self.scrollbar.pack_forget()
        
        text, speakers = load_textfile(text_filename)
        y_offset = 0
        
        for i, line in enumerate(text):
            line, _ = get_cleaned_sentence(line)
            utt = UtteranceFrame(self.scrollable_frame)
            utt.set_text(line)
            utt.set_number(i, len(text))
            utt.pack(fill='x')
            
            #t.place(anchor='nw', x=0, y=y_offset)
            y_offset += 20
        
        self.raw_text.delete("1.0","end")
        with open(text_filename, 'r') as f:
            for line in f.readlines():
                self.raw_text.insert("end", line)
        
        #self.raw_text.pack(side="right", expand=True, fill="both")
        #self.scrollbar.pack(side='right', fill='y')
        #self.canvas.pack(side='left')



class UtteranceFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #n_lines = self.count_total_nb_lines(t)
        
        upperBar = tk.Frame(self, bg="#aaf")
        upperBar.pack(side="top", fill="x")
        
        self.label = tk.Label(upperBar, text="n/t")
        self.label.pack(side="left")
        
        play_btn = tk.Button(upperBar, text=">", width=1, height=1, command=self.play_segment)
        play_btn.pack(side="left")
        
        self.text = tk.Text(self, wrap='word')
        self.text.insert('end', "empty text")
        self.text.config(state='disabled', height=2) # Read only
        self.text.pack(side="bottom", fill='x')
    
    def set_text(self, text):
        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('end', text)
        self.text.config(state='disabled')
        #self.text.update()
    
    def set_number(self, n, total):
        self.label.config(text = f"{n+1}/{total}")
    
    def play_segment(self):
        pass


if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        split_filename = sys.argv[1]
    print(split_filename)
    
    # Create a GUI window
    root = tk.Tk()

    # place Pad object in the root window
    pad = Pad(root)
    pad.pack(expand=1, fill="both")
    pad.load_split_file(split_filename)

    # start the GUI
    root.mainloop()
