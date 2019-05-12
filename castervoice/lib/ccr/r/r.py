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
        "assign":
            R(Text(" <- "), rdescript="Rlang: Assignment"),
        "R in":
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


        #"tidy verse":
        #    R(Text("tidyverse"), rdescript="Rlang: tidyverse"),
        "fun <function>":
            R(Text("%(function)s()") + Key("left"), rdescript="Rlang: insert a function"),
        "fun target with transform":
            R(Text("target(") + Key("enter") + Text(",") + Key("enter") + Text("transform = ") + Key("up") + Key("left"), rdescript="Rlang: insert a target function"),
        "new fun <text>":
            R(Text("%(text)s()") + Key("left"), rdescript="Rlang: insert a function"),
        "package <package>":
            R(Text("%(package)s::"), rdescript="Rlang: insert a package"),
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
			
		"focus console":
            R(Key("c-2"), rdescript="RStudio: Focus Console"),
        "focus main":
            R(Key("c-1"), rdescript="RStudio: Focus Main"),
        "help this":                        
		    R(Key("f1"), rdescript="R: Help for function at cursor"),
		
		"run with function <runwithfunction>":  
		    R(Key("c-c") + Key("c-2/10") + Key("c-a, backspace") + Text("%(runwithfunction)s") + Key("s-9") +
		        Key("c-v") + Key("enter/100") + Key("c-1"), rdescript="R: Run with function"),
	    "run with function <runwithfunction> terminal":  
		    R(Key("c-c") + Key("as-t/50") + Key("end") + Key("backspace:20") + Text("%(runwithfunction)s") + Key("s-9") +
		        Key("s-insert") + Key("s-0") + Key("enter/100") + Key("c-1"), rdescript="R: Run with function"),
		"jump sun [<nr500>] <text>":
    	    Key("s-pgup")*Repeat(extra="nr500") + R(Key("c-f") + Text("%(text)s") + Key("escape/5") + Key("left"), rdescript="RStudio: jump quickly up to text"),
		"jump doon [<nr500>] <text>":
    	    Key("s-pgdown")*Repeat(extra="nr500") + R(Key("c-f") + Text("%(text)s") + Key("escape/5") + Key("left"), rdescript="RStudio: jump quickly down to text"),
		"jump sauce [<nr500>] <text>":
    	    Key("s-up")*Repeat(extra="nr500") + R(Key("c-f") + Text("%(text)s") + Key("escape/5") + Key("left"), rdescript="RStudio: jump up to text"),
		"jump dunce [<nr500>] <text>":
    	    Key("s-down")*Repeat(extra="nr500") + R(Key("c-f") + Text("%(text)s") + Key("escape/5") + Key("left"), rdescript="RStudio: jump down to text"),
    }

    extras = [
        Dictation("text"),
        Choice(
            "function", {
                "arrange": "arrange",
                "as character": "as.character",
				"as date": "as_date",
                "as tibble": "as_tibble",
				"as double": "as.double",
				"as character": "as.character",
                "bind cols": "bind_cols",
                "bind plans": "bind_plans",
				"bind rows": "bind_rows",
				"browser": "browser", 
                "case when": "case_when",
                "combine": "combine",
                "complete": "complete",
                "count": "count",
                "cross": "cross",
                "crossing": "crossing",
				"debug": "debug",
                "desk": "desc",
                "distinct": "distinct",
                "drake plan": "drake_plan",
				"drake config": "drake_config",
                "drop NA": "drop_na",
                "expand": "expand",
				"extract": "extract",
				"filter": "filter",
				"file path": "file.path",
				"fixed": "fixed",
				"flatten": "flatten",
				"floor date": "floor_date",
                "full join": "full_join",
                "funds": "funs",
                "gather": "gather",
                "group by": "group_by",
                "head": "head",
                "if else": "if_else",
                "inner join": "inner_join",
                "install packages":"install.packages",
                "install github":"devtools::install_github",
                "is dot na":"is.na",
                "lag": "lag",
                "left join": "left_join",
                "length": "length",
                "load": "loadd",
                "library": "library",
                "list": "list",
                "list files": "list.files",
                "make": "make",
                "matches": "matches",
                "map": "map",
                "map logical": "map_lgl",
                "map character": "map_chr",
                "map double": "map_dbl",
				"(mem | memory) used": "pryr::mem_used",
                "pee map": "pmap",
                "pee map logical": "pmap_lgl",
                "pee map character": "pee map_chr",
                "pee map double": "pee map_dbl",
                "mean": "mean",
                "mutate": "mutate",
                "mutate at": "mutate_at",
                "mutate if": "mutate_if",
                "mutate each": "mutate_each",
                "en": "n",
                "names": "names",
                "nest": "nest",
                "paste oh": "paste0",
				"print": "print",
				"object size": "pryr::object_size",
				"pull": "pull",
                "raster": "raster",
                "read": "readd",
				"read S F": "read_sf",
                "read CSV": "read_csv",
                "read fist": "read_fst",
                "rename": "rename",
                "roxygenize": "roxygenize",
                "safely": "safely",
                "sample en": "sample_n",
                "select": "select",
                "set diff": "setdiff",
                "set names": "set_names",
                "set (W D | working directory)": "setwd",
				"get (W D | working directory)": "getwd",
                "slice": "slice",
                "S T as S F": "st_as_sf",
                "S T as S F C": "st_as_sfc",
                "S T S F": "st_sf",
                "S T S F C": "st_sfc",
                "S T C R S": "st_crs",
                "S T collection extract": "st_collection_extract",
                "S T centroid": "st_centroid",
                "S T union": "st_union",
                "S T subdivide": "st_subdivide",
                "S T cast": "st_cast",
                "S T join": "st_join",
                "S T B box": "st_bbox",
                "spread": "spread",
                "string contains": "str_contains",
                "string detect": "str_detect",
                "string replace": "str_replace",
                "string replace all": "str_replace_all",
                "string subset": "str_subset",
                "starts with": "starts_with",
                "sum": "sum",
                "R lang sim": "rlang::sym",
                "summarise": "summarise",
				"summarise all": "summarise_all",
				"summarise if": "summarise_if",
				"summarise each": "summarise_each",
				"source": "source",
                "tail":"tail",
                "target":"target",
                "tibble":"tibble",
                "tribble":"tribble",
                "train":"train",
                "ungroup": "ungroup",
				"unique": "unique",
				"unnest": "unnest",
				"vars": "vars",
				"walk": "walk",
				"pee walk": "pwalk",
            }),
        Choice(
            "runwithfunction", {
				"debug": "debug",
				"load": "loadd",
				"object size": "pryr::object_size",
				"names": "names",
            }),
        Choice(
            "package", {
                "dev tools": "devtools",
                "drake": "drake",
				"string are": "stringr",
				"(deep liar | deep)": "dplyr",
				"lubridate": "lubridate",
				"raster": "raster",
				"roxygen": "roxygen2",
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
		IntegerRefST("nr500", 1, 500),
        IntegerRefST("nr50", 1, 50),
    ]

    defaults = {
	  "nr500": 1,
      "nr50": 1,
	}


control.nexus().merger.add_global_rule(Rlang())
