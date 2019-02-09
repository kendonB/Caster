'''
Created on May 23, 2017

@author: shippy
'''

from dragonfly import Dictation, MappingRule, Choice, Repeat

from castervoice.lib import control
from castervoice.lib.actions import Key, Text
from castervoice.lib.ccr.standard import SymbolSpecs
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R
from castervoice.lib.dfplus.additions import IntegerRefST


class Rlang(MergeRule):
    auto = [".R", ".r"]
    pronunciation = "are"

    mapping = {
        SymbolSpecs.IF:
            R(Text("if ()") + Key("left"), rdescript="Rlang: If"),
        SymbolSpecs.ELSE:
            R(Text("else ") + Key("enter"), rdescript="Rlang: Else"),
        #
        # (no switch in Rlang)
        SymbolSpecs.BREAK:
            R(Text("break"), rdescript="Rlang: Break"),
        #
        SymbolSpecs.FOR_EACH_LOOP:
            R(Text("for ( in ):") + Key("left:6"), rdescript="Rlang: For Each Loop"),
        SymbolSpecs.FOR_LOOP:
            R(Text("for (i in 1:)") + Key("left"), rdescript="Rlang: For i Loop"),
        SymbolSpecs.WHILE_LOOP:
            R(Text("while ()") + Key("left"), rdescript="Rlang: While"),
        # (no do-while in Rlang)
        #
        SymbolSpecs.AND:
            R(Text(" & "), rdescript="Rlang: And"),
        SymbolSpecs.OR:
            R(Text(" | "), rdescript="Rlang: Or"),
        SymbolSpecs.NOT:
            R(Text("!"), rdescript="Rlang: Not"),
        #
        SymbolSpecs.SYSOUT:
            R(Text("print()") + Key("left"), rdescript="Rlang: Print"),
        #
        SymbolSpecs.IMPORT:
            R(Text("library()") + Key("left"), rdescript="Rlang: Import"),
        #
        # SymbolSpecs.FUNCTION:
        #     R(Text("function()") + Key("left"), rdescript="Rlang: Function"),
		SymbolSpecs.FUNCTION:               
		    R(Text("function()") + Key("leftbrace, rightbrace, left, enter, c-left, c-left, c-left, right"), rdescript="R: Function"),

        # SymbolSpecs.CLASS:          R(Text("setClass()") + Key("left"), rdescript="Rlang: Class"),
        #
        SymbolSpecs.COMMENT:
            R(Text("#"), rdescript="Rlang: Add Comment"),
        #
        SymbolSpecs.NULL:
            R(Text("NULL"), rdescript="Rlang: Null"),
        #
        SymbolSpecs.RETURN:
            R(Text("return()") + Key("left"), rdescript="Rlang: Return"),
        #
        SymbolSpecs.TRUE:
            R(Text("TRUE"), rdescript="Rlang: True"),
        SymbolSpecs.FALSE:
            R(Text("FALSE"), rdescript="Rlang: False"),

        # Rlang specific
        "ass":
            R(Text(" <- "), rdescript="Rlang: Assignment"),
        "contained in":
            R(Key('space, percent, i, n, percent, space'),
              rdescript="Rlang: In operator"),
        "slurp | chain":
            R(Key('space, percent, rangle, percent, space'), rdescript="Rlang: Pipe"),
        "tell (slurp | chain)":
            R(Key('end, space, percent, rangle, percent, enter'),
              rdescript="Rlang: Pipe at end"),
        "tell add":
            R(Key('end, space, plus, enter'), rdescript="Rlang: plus at end"),
        "NA":
            R(Text("NA"), rdescript="Rlang: Not Available"),
        "shell iffae | LFA":
            R(Text("elseif ()") + Key("left"), rdescript="Rlang: Else If"),
        "dot (our|are)":
            R(Text(".R"), rdescript="Rlang: .py"),
        "see as vee":
            R(Text("csv"), rdescript="Rlang: csv"),


 #       "tidy verse":
 #           R(Text("tidyverse"), rdescript="Rlang: tidyverse"),
        "fun <function>":
            R(Text("%(function)s()") + Key("left"), rdescript="Rlang: insert a function"),
        "graph <ggfun>":
            R(Text("%(ggfun)s()") + Key("left"),
              rdescript="Rlang: insert a ggplot function"),
        "pack <pacfun>":
            R(Text("%(pacfun)s()") + Key("left"), rdescript="Rlang: insert a pacman function"),
		
		"temp":
            R(Text("tmp"), rdescript="Rlang: tmp"),
		
# should be in rstudio		
		"run it <n>":                    
	        Key("home")+R(Key("s-down"), rdescript="R: Run command") * Repeat(extra="n") + Key("c-enter") + Key("right"), 
	    "run it":                    
	        Key("c-enter"),		
        "run it terminal":                    
	        Key("ca-enter"),
	    "run stay":
	        Key("a-enter"), 
	    "run this":
	        Key("c-right, cs-left, c-enter"),
        "run script":                    
	        Key("cs-s"),
        "run above":                    
	        Key("ca-b"),
        "run below":                    
	        Key("ca-e"),
			
		"look soul":
            R(Key("c-2"), rdescript="RStudio: Focus Console"),
        "look ed":
            R(Key("c-1"), rdescript="RStudio: Focus Main"),
		"look terminal":                    
	        R(Key("as-t"), rdescript="R: Focus terminal"),

        "help this":                        
		    R(Key("f1"), rdescript="R: Help for function at cursor"),
		"package deep":                           
		    R(Text("dplyr::"), rdescript="R: dplyr package prefix"),
		"package dev tools":                           
		    R(Text("devtools::"), rdescript="R: devtools package prefix"),
		"package data table":                           
		    R(Text("data.table::"), rdescript="R: data table package prefix"),
		"package per":                           
		    R(Text("purrr::"), rdescript="R: purrr package prefix"),
		"package tidy are":                           
		    R(Text("tidyr::"), rdescript="R: tidyr prefix"),
        "package lubricate":                          
		    R(Text("lubridate::"), rdescript="R: lubridate"),		
		"package string are":                          
		    R(Text("stringr::str_"), rdescript="R: stringr package prefix"),		
		"package tibble":                     
		    R(Text("tibble::"), rdescript="R: tibble package prefix"),		
        "package Magruder":                     
		    R(Text("magrittr::"), rdescript="R: magrittr package prefix"),		

	
    }

    extras = [
        Dictation("text"),
        Choice(
            "function", {
                "arrange": "arrange",
                "as character": "as.character",
                "as data frame": "as.data.frame",
                "as double": "as.double",
                "as factor": "as.factor",
                "as numeric": "as.numeric",
                "bind rows": "bind_rows",
				"browser": "browser", 
                "case when": "case_when",
                "count": "count",
                "drop NA": "drop_na",
                "filter": "filter",
                "full join": "full_join",
                "gather": "gather",
                "group by": "group_by",
                "head": "head",
                "inner join": "inner_join",
                "install": "install",
                "install github": "install_github",
                "install packages":"install.packages",
                "is dot na":"is.na",
                "left join": "left_join",
                "length": "length",
                "library": "library",
                "list": "list",
                "mean": "mean",
                "mutate": "mutate",
                "names": "names",
                "paste oh": "paste0",
                "read CSV": "read_csv",
                "rename": "rename",
                "select": "select",
                "string contains": "str_contains",
                "string detect": "str_detect",
                "string replace": "str_replace",
                "string replace all": "str_replace_all",
                "string subset": "str_subset",
                "starts with": "starts_with",
                "sum": "sum",
                "summarise": "summarise",
                "tail":"tail",
                "ungroup": "ungroup",
				"unique": "unique",
            }),
        Choice(
            "ggfun", {
                "aesthetics": "aes",
                "column [plot]": "geom_col",
                "density [plot]": "geom_density",
                "ex label":"xlab",
                "ex limit": "xlim",
                "facet grid": "facet_grid",
                "histogram [plot]": "geom_histogram",
                "labels": "labs",
                "line [plot]": "geom_line",
                "path [plot]": "geom_path",
                "plot": "ggplot",
                "point [plot]": "geom_point",
                "save": "ggsave",
                "smooth [plot]": "geom_smooth",
                "theme minimal": "theme_minimal",
                "why label":"ylab",
                "why limit": "ylim",
            }),
        Choice(
            "pacfun", {
                "install":"p_install",
                "install hub":"p_install_gh",
                "install version":"p_install_version",
                "install temp":"p_temp",
                "load":"p_load",
                "unload":"p_unload",
                "update":"p_update",
            }),
		IntegerRefST("n", 1, 10000),
    ]
    defaults = {}


control.nexus().merger.add_global_rule(Rlang())
