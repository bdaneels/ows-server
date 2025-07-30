#
# to replace data in templated files
# we use jinja cli interface for that
# first get the current directory (where this file is)

current_dir := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
CRIT_LOGGING := CRITICAL
DEBUG_LOGGING := DEBUG
INFO_LOGGING := INFO
MODE_DEBUG := ""
MODE_OPER := > /dev/null 2>&1
DIRS=uploads scripts
UPLOAD_DIR := uploads
SCRIPT_DIR := scripts
DIRS := $(UPLOAD_DIR) $(SCRIPT_DIR)

home: $(dirs) ini deb
server: $(dirs) ini opr

.PHONY: Makefile

$(dirs):
	mkdir $@

ini:
	jinja  -D cwd "$(current_dir)" -o ows.ini ows.ini.j2

deb:
	jinja  -D mode "$(MODE_DEBUG)" -o start_srv.sh start_srv.sh.j2
	chmod +x start_srv.sh
opr:
	jinja  -D mode "$(MODE_OPER)" -o start_srv.sh start_srv.sh.j2
	chmod +x start_srv.sh
tests:
	cp test/merge_csvs.py scripts/
	cp test/*.csv uploads/
