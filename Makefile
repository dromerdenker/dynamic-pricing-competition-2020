# Felix Ogg, July 12 - making things manageable to compete with small increments.
SHELL=/bin/bash

TEST_DIR = tst
LOCALSIM_LOGDIR = local_simruns
SIM_DIR = compete_simulations
TS = $(shell date "+%a%Y%m%d-%Hh%M")
VENV_PYTHON = venv/bin/python

simulate_local:
	source venv/bin/activate ;\
	cd $(SIM_DIR) ;\
	python3 basic_sim_algorithm.py duopoly & \
	python3 basic_sim_algorithm.py dynamic & \
	python3 basic_sim_algorithm.py oligopoly

# simulate 100 seasons x 100 periods and save the excel report
simroll: simulate_local
	#duopoly
	mv $(LOCALSIM_LOGDIR)/duopoly_results.xlsx $(LOCALSIM_LOGDIR)/duopoly_results_$(TS).xlsx
	open $(LOCALSIM_LOGDIR)/duopoly_results_$(TS).xlsx
	#dynamic
	mv $(LOCALSIM_LOGDIR)/dynamic_results.xlsx $(LOCALSIM_LOGDIR)/dynamic_results_$(TS).xlsx
	open $(LOCALSIM_LOGDIR)/dynamic_results_$(TS).xlsx
  #oligopoly
	mv $(LOCALSIM_LOGDIR)/oligpoly_results.xlsx $(LOCALSIM_LOGDIR)/oligopoly_results_$(TS).xlsx
	open $(LOCALSIM_LOGDIR)/oligopoly_results_$(TS).xlsx

freeze:
	source venv/bin/activate ;\
	pip3 freeze > requirements.txt

# upload the files to the competition FTP server
upload: tag
	$(SHELL) upload.sh | tee -a uploads.log

ftp-ls:
	#list what is on the competition FTP server
	$(SHELL) ftp-ls.sh | tee -a uploads.log

# setup a local venv
venv:
	rm -rf venv
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	@echo -------- TIPS: ----------
	@echo Start venv with:        source venv/bin/activate
	@echo Exit from venv with:    deactivate

unittest:
	source venv/bin/activate ;\
	pytest $(TEST_DIR)

testwatch:
	source venv/bin/activate ;\
	ptw $(TEST_DIR)

compete:
	#does my algo beat the demo competitor by the organizers?
	source venv/bin/activate ; cd $(SIM_DIR) ;\
	python3 sim_algorithm-competition.py duopoly_demo 481
	#does my algo beat my previous algos?
	source venv/bin/activate ; cd $(SIM_DIR) ;\
	python3 sim_algorithm-competition.py duopoly20200731 481
	#does my algo beat itself?
	source venv/bin/activate ; cd $(SIM_DIR) ;\
	python3 sim_algorithm-competition.py duopoly 481

jupyter:
	$(SHELL) docker_jupyter.sh

tag:
	git tag -a v.$(TS) -m 'submitted duopoly today.'
	git push origin --tags

terminals:
	# https://stackoverflow.com/questions/7171725/open-new-terminal-tab-from-command-line-mac-os-x
	# Terminal 1: unit-test watch
	echo "cd `pwd`; make testwatch" > /tmp/testwatch.sh;chmod a+x /tmp/testwatch.sh;open -a Terminal /tmp/testwatch.sh &\
	# Terminal 2: compete
	echo "cd `pwd`; make compete" > /tmp/compete_it.sh;chmod a+x /tmp/compete_it.sh;open -a Terminal /tmp/compete_it.sh &\	
	# Terminal 3: jupyter docker environment
	echo "cd `pwd`; make jupyter" > /tmp/jupyter_it.sh;chmod a+x /tmp/jupyter_it.sh;open -a Terminal /tmp/jupyter_it.sh
