'''
Created on Sep 1, 2015

@author: synkarius
'''
from dragonfly import Key, Mimic, Text, Dictation, Repeat

from caster.lib import control
from caster.lib.ccr.standard import SymbolSpecs
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.short import R


class LaTeX(MergeRule):
    auto = [".tex",".Rnw"]
    pronunciation = "lay tech"
        
    mapping = {
        
        # TexStudio specific
		SymbolSpecs.COMMENT:                R(Key("c-t"), rdescript="R: Add Comment"),
        
        "tech":                             R(Key("as-f6"), rdescript="LaTeX: Compile LaTeX quickly"),
	    "full tech":                        R(Key("as-f7"), rdescript="LaTeX: Compile LaTeX full"),
        "are tech":                         R(Key("as-f4"), rdescript="LaTeX: Compile knitr quickly"),
	    "full are tech":                    R(Key("as-f5"), rdescript="LaTeX: Compile knitr full"),
	    "eek":                              R(Key("cs-n"), rdescript="LaTeX: Equation environment"),
		"eek align":                        R(Key("ca-l"), rdescript="LaTeX: Align environment"),
	    "numbers":                          R(Key("ca-e"), rdescript="LaTeX: Enumerate environment"),
        "items":                            R(Key("ca-i"), rdescript="LaTeX: Itemize environment"),
        "new item":                         R(Key("cs-i"), rdescript="LaTeX: New item"),
	    "emphasize it":                    	R(Key("cs-e"), rdescript="LaTeX: Emphasize text"),
        "bold it":                    	    R(Key("c-b"), rdescript="LaTeX: Bold text"),
        "leak":                             R(Key("dollar") + Key("dollar") + Key("left"), rdescript="LaTeX: In line equation"),
        "Frank":                    	    R(Key("cs-f"), rdescript="LaTeX: Fraction"),
        "new frame":                    	R(Key("ca-f"),	  rdescript="LaTeX: New beamer frame"),
	    "knitting chunk":                   R(Key("ca-k"), rdescript="LaTeX: New knitr chunk"),
	    "word count":                       R(Key("a-t, n/25, up, down, tab, enter"), rdescript="LaTeX: Word count"), 
        "lay tech table":                         R(Key("cas-t"), rdescript="LaTeX: table template "),

	 
        "new file":                         R(Key("c-n"), rdescript="TexStudio: New file"),     
    	"save as":                          R(Key("ca-s"), rdescript="TexStudio: Save as"),
	 	"open recent":                      R(Key("a-f, r"), rdescript="TexStudio: Open recent"),
		"wizard quick start":               R(Key("a-w, s"), rdescript="TexStudio: Quick start"),
        # latex specific
        
        "lay tech infinity":                R(Text("\\infty"), rdescript="LaTeX: Infinity"),
        "lay tech shake":                   R(Text("\\\\") + Key("enter"), rdescript="LaTeX: New line"),
        "lay tech ellipses":                R(Text("\\ldots") , rdescript="LaTeX: Ellipses"),
		"Greek Alpha":                    	R(Text("\\alpha"), rdescript="LaTeX: Alpha character"),
        "Greek epsilon":                    R(Text("\\varepsilon"), rdescript="LaTeX: Alpha character"),
        "Greek Beta":                    	R(Text("\\beta"), rdescript="LaTeX: Beta character"),
        "Greek gamma":                    	R(Text("\\gamma"), rdescript="LaTeX: Small gamma character"),
        "Greek sigma":                    	R(Text("\\sigma"), rdescript="LaTeX: Small sigma character"),
        "big Greek gamma":                  R(Text("\\Gamma"), rdescript="LaTeX: Big gamma character"),
        "Greek Delta":                    	R(Text("\\delta"), rdescript="LaTeX: Small Delta character"),
        "Greek row":                    	R(Text("\\rho"), rdescript="LaTeX: Small rho character"),
        "square root":                    	R(Text("\\sqrt{")+ Key("rbrace") +Key("left"), rdescript="LaTeX: Square root"),
        
        "big Greek Delta":                  R(Text("\\Delta"), rdescript="LaTeX: Big Delta character"),
        "sub ex":                    	    R(Text("_{") + Key("rbrace") +Key("left"), rdescript="LaTeX: underscore"),
        "text citation":                    R(Text("\\textcite{")+  Key("rbrace")+Key("left"), rdescript="LaTeX: In text citation"), 
	    "ren citation":                     R(Text("\\parencite{")+  Key("rbrace")+Key("left"), rdescript="LaTeX: Parenthesis citation"), 
	    "new section":                      R(Text("\\section{") + Key("rbrace") + Key("left"), rdescript="LaTeX: New section"),
        "new sub section":                  R(Text("\\subsection{") + Key("rbrace") + Key("left"), rdescript="LaTeX: New section"),
        "lay tech degrees":                 R(Text("$^{\\circ}$"), rdescript="LaTeX: New section"),
        "lay tech curly":                   R(Text("\\left\\{\\right\\}") + Key("left") * Repeat(8), rdescript="LaTeX: Curly brackets"),
        "lay tech prekris":                 R(Text("\\left(\\right)") + Key("left") * Repeat(7), rdescript="LaTeX: Parenthesis"),
        "lay tech brax":                    R(Text("\\lef") + Key("t/25") + Key("lbracket/25") + Key("escape") + Text("\\right]") + Key("left") * Repeat(7), rdescript="LaTeX: Brackets"),
        "math bold | koom bee em":                        R(Text("\\bm{") + Key("rbrace") + Key("left"), rdescript="LaTeX: Bold math"),
		
        "quad space":                       R(Text("\\quad"), rdescript=""),
        "double quad space":                R(Text("\\qquad"), rdescript=""),
        "koom em box":                           R(Text("\\mbox{") + Key("rbrace") + Key("left"), rdescript=""),
        
        "koom <textnv>":                    R(Key("backslash") + Text("%(textnv)s") + Key("lbrace, rbrace, left"), rdescript="LaTeX: LaTeX command"), 
        "koom sum":                    R(Key("backslash") + Text("sum_") + Key("lbrace, rbrace, left"), rdescript="LaTeX: Sum command"), 
        "koom ref":                    R(Key("backslash") + Text("ref") + Key("lbrace, rbrace, left"), rdescript="LaTeX: ref command"), 
        "koom (equation|eck) ref":                    R(Key("backslash") + Text("eqref") + Key("lbrace, rbrace, left"), rdescript="LaTeX: ref command"), 
		
		"<textnv>": Text("%(textnv)s"),
		
		"Clean auxiliary files":
		    R(Key("a-t, a, enter"), rdescript="LaTeX: clean auxiliary files"),

    }

    extras = [
        Dictation("textnv"),
    ]

    defaults ={
            "textnv": "", 
           }


control.nexus().merger.add_global_rule(LaTeX())