#
# to replace data in templated files
# we use jinja cli interface for that
# first get the current directory (where this file is)

current_dir := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
MODE_DEBUG := 
MODE_OPER := > /dev/null 2>&1
DIRS=uploads scripts/tst out
UPLOAD_DIR := uploads
SCRIPT_DIR := scripts
SERVICE = ows_server.service
SYSTEMD_DIR = /etc/systemd/system

ifeq ($(MAKECMDGOALS),home)
	DEBUG = True
else ifeq ($(MAKECMDGOALS),server)
	DEBUG = False
else
	DEBUG = False
endif

home: dirs deb ini
server: dirs opr ini

.PHONY: Makefile dirs tests install

dirs:
	mkdir -p $(DIRS)

ini:
	sed -e "s|{{ cwd }}|$(current_dir)|g" -e "s/{{ debug }}/$(DEBUG)/g" \
	ows.ini.j2 > ows.ini

deb:
	sed -e "s|{{ mode }}|$(MODE_DEBUG)|g" start_srv.sh.j2 > start_srv.sh
	chmod +x start_srv.sh

opr:
	sed -e "s|{{ mode }}|$(MODE_OPER)|g" start_srv.sh.j2 >start_srv.sh
	chmod +x start_srv.sh
tests:
	cp test/merge_csvs.py scripts/tst/
	cp test/merge_csvs_pandas.py scripts/tst/
	cp test/merge_csvs_pandas_args.py scripts/tst/
	cp test/*.csv uploads/

install:
	@echo "Installing $(SERVICE) to $(SYSTEMD_DIR)..."
	install -m 644 $(SERVICE) $(SYSTEMD_DIR)/
	@echo "Reloading systemd daemon..."
	systemctl daemon-reload
	@echo "Enabling and starting $(SERVICE)..."
	systemctl enable --now $(SERVICE)
