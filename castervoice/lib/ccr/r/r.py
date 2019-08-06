'''
Created on May 23, 2017filelist

@author: shippy
'''
from castervoice.lib.imports import *

package_dict = {
    "dev tools": "devtools",
    "drake": "drake",
	"string are": "stringr",
	"(dee plier | deep)": "dplyr",
	"lubridate": "lubridate",
	"raster": "raster",
	"roxygen": "roxygen2",
    "tidy verse": "tidyverse",
    "S F": "sf",
    "stars": "stars",
    "raster": "raster",
    "fist": "fst",
    "cow plot": "cowplot",
    "direct labels": "directlabels",
    "X table": "xtable"
}

class Rlang(MergeRule):
    auto = [".R", ".r"]
    pronunciation = "are"

    mapping = {
        SymbolSpecs.IF:
            R(Text("if ()") + Key("left")),
        SymbolSpecs.ELSE:
            R(Text("else ") + Key("enter")),
        #
        # (no switch in Rlang)
        SymbolSpecs.BREAK:
            R(Text("break")),
        #
        SymbolSpecs.FOR_EACH_LOOP:
            R(Text("for ( in ):") + Key("left:6")),
        SymbolSpecs.FOR_LOOP:
            R(Text("for (i in 1:)") + Key("left")),
        SymbolSpecs.WHILE_LOOP:
            R(Text("while ()") + Key("left")),
        # (no do-while in Rlang)
        #
        SymbolSpecs.AND:
            R(Text(" & ")),
        SymbolSpecs.OR:
            R(Text(" | ")),
        SymbolSpecs.NOT:
            R(Text("!")),
        #
        SymbolSpecs.SYSOUT:
            R(Text("print()") + Key("left")),
        #
        SymbolSpecs.IMPORT + " <lib_seq>":
            R(Text("pacman::p_load()") + Key("left, enter") + Function(lambda lib_seq: Text(",\n".join(lib_seq)).execute())),
        "these packages <lib_seq>":
            R(Function(lambda lib_seq: Text(",\n".join(lib_seq)).execute())),
        #
        # SymbolSpecs.FUNCTION:
        #     R(Text("function()") + Key("left"), rdescript="Rlang: Function"),
		SymbolSpecs.FUNCTION:
		    R(Text("function()") + Key("leftbrace, rightbrace, left, enter, c-left, c-left, c-left, right")),

        # SymbolSpecs.CLASS:          R(Text("setClass()") + Key("left"), rdescript="Rlang: Class"),
        SymbolSpecs.COMMENT:
            R(Text("#")),
        #
        SymbolSpecs.NULL:
            R(Text("NULL")),
        #
        SymbolSpecs.RETURN:
            R(Text("return()") + Key("left")),
        #
        SymbolSpecs.TRUE:
            R(Text("TRUE")),
        SymbolSpecs.FALSE:
            R(Text("FALSE")),

        # Rlang specific
        "assign":
            R(Text(" <- ")),
        "in (op | operator)":
            R(Key('space, percent, i, n, percent, space')),
        "slurp | chain":
            R(Key('space, percent, rangle, percent, space')),
        "tell (slurp | chain)":
            R(Key('end, space, percent, rangle, percent, enter')),
        "tell add":
            R(Key('end, space, plus, enter')),
        "NA":
            R(Text("NA")),
        "shell iffae | LFA":
            R(Text("elseif ()") + Key("left")),
        "dot (our|are)":
            R(Text(".R")),
        "see as vee":
            R(Text("csv")),


        #"tidy verse":
        #    R(Text("tidyverse"), rdescript="Rlang: tidyverse"),
        "fun <function>":
            R(Text("%(function)s()") + Key("left")),
        "fun target with transform":
            R(Text("target(") + Key("enter") + Text(",") + Key("enter") + Text("transform = ") + Key("up") + Key("left")),
        "new fun <text>":
            R(Text("%(text)s()") + Key("left")),
        "package <package>":
            R(Text("%(package)s::")),
        "graph <ggfun>":
            R(Text("%(ggfun)s()") + Key("left")),
        "pack <pacfun>":
            R(Text("%(pacfun)s()") + Key("left")),

		"temp":
            R(Text("tmp"), rdescript="Rlang: tmp"),

# should be in rstudio but continuous command recognition doesn't seem to be working for apps contexts
        "[go] [to] line <nr500>":
            R(Key("as-g/10") + Text("%(nr500)s") + Key("enter"),
              rdescript="R: Go to Line #"),
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
        Repetition(
            Choice("package", package_dict),
            min = 1, max = 8, name = "lib_seq"
        ),
        Choice(
            "function", {
                "aesthetics | AES": "aes",
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
                "class": "class",
				"come some": "cumsum",
                "debug": "debug",
                "desk": "desc",
                "distinct": "distinct",
                "drake plan": "drake_plan",
				"drake config": "drake_config",
                "drop NA": "drop_na",
                "element blank": "element_blank",
                "element text": "element_text",
				"expand": "expand",
				"extract": "extract",
				"factor": "factor",
				"(F E L M | FLM)": "felm",
				"filter": "filter",
				"file in": "file_in",
				"file out": "file_out",
				"file path": "file.path",
				"fixed": "fixed",
				"flatten": "flatten",
				"floor date": "floor_date",
                "full join": "full_join",
                "funds": "funs",
                "gather": "gather",
                "gee om point": "geom_point",
                "gee om line": "geom_line",
                "gee om (hist | histogram)": "geom_histogram",
				"gee om S F": "geom_sf",
                "G G plot": "ggplot",
                "group by": "group_by",
                "G G plot": "ggplot",
                "head": "head",
                "hist": "hist",
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
                "map view": "mapview",
				"(mem | memory) used": "pryr::mem_used",
                "pee map": "pmap",
                "pee map logical": "pmap_lgl",
                "pee map character": "pee map_chr",
                "pee map double": "pee map_dbl",
                "plot": "plot",
                "mean": "mean",
                "mutate": "mutate",
                "mutate at": "mutate_at",
                "mutate if": "mutate_if",
                "mutate each": "mutate_each",
                "en": "n",
                "names": "names",
                "nest": "nest",
                "in row": "nrow",
                "in col": "ncol",
                "paste oh": "paste0",
				"print": "print",
                "predict": "predict",
                "predict F E L M": "predict.felm",
				"object size": "pryr::object_size",
				"pull": "pull",
                "raster": "raster",
                "read": "readd",
				"read CSV": "read_csv",
                "read fist": "read_fst",
                "read (excel | X L S X)": "read_xlsx",
                "read R D S": "read_rds",
                "read S F": "read_sf",
                "read stars": "read_stars",
                "rename": "rename",
                "roxygenize": "roxygenize",
                "safely": "safely",
                "sample en": "sample_n",
                "seck": "seq",
                "seck along": "seq_along",
                "select": "select",
                "set diff": "setdiff",
                "set names": "set_names",
                "set (W D | working directory)": "setwd",
				"get (W D | working directory)": "getwd",
                "R lang sim": "rlang::sym",
                "slice": "slice",
                "S T as S F": "st_as_sf",
                "S T as S F C": "st_as_sfc",
                "S T as stars": "st_as_stars",
                "S T S F": "st_sf",
                "S T S F C": "st_sfc",
                "S T C R S": "st_crs",
                "S T collection extract": "st_collection_extract",
                "S T centroid": "st_centroid",
                "S T union": "st_union",
                "S T subdivide": "st_subdivide",
                "S T simplify": "st_simplify",
                "S T cast": "st_cast",
                "S T join": "st_join",
                "S T simplify": "st_simplify",
                "S T transform": "st_transform",
                "S T B box": "st_bbox",
                "spread": "spread",
                "stop if not": "stopifnot",
                "string contains": "str_contains",
                "string detect": "str_detect",
                "string replace": "str_replace",
                "string replace all": "str_replace_all",
                "string subset": "str_subset",
                "starts with": "starts_with",
                "sum": "sum",
                "summarise": "summarise",
                "summary": "summary",
				"summarise all": "summarise_all",
				"summarise if": "summarise_if",
				"summarise each": "summarise_each",
				"source": "source",
                "tail":"tail",
                "target":"target",
                "theme":"theme",
				"theme cow plot":"theme_cowplot",
                "tibble":"tibble",
                "tribble":"tribble",
                "train":"train",
                "table":"table",
                "ungroup": "ungroup",
				"unique": "unique",
				"unnest": "unnest",
				"vars": "vars",
				"walk": "walk",
				"pee walk": "pwalk",
                "ex (label | lab)":"xlab",
                "ex (limit | lim)": "xlim",
                "why (label | lab)":"ylab",
                "why (limit | lim)": "ylim",
            }),
        Choice(
            "runwithfunction", {
				"debug": "debug",
				"class": "class",
				"load": "loadd",
                "in row": "nrow",
				"object size": "pryr::object_size",
				"names": "names",
				"map view": "mapview",
				"summary": "summary",
				"view": "View",
				"unique": "unique",
            }),
        Choice("package", package_dict),
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


control.global_rule(Rlang())
