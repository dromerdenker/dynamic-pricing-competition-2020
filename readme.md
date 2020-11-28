Submission repository to play the  __Dynamic Pricing algorithms  competition__ - edition 2020.

https://www.dynamic-pricing-competition.com/


## Requirements

You need FTP on the command line installed. On my Mac OS (Catalina), I had to first install:

`brew install inetutils`

as explained here:
https://discussions.apple.com/thread/8093031

These `inetutils` are documented:
https://www.gnu.org/software/inetutils/manual/inetutils.html

Furtermore you need `make` , the typical pre-installed gnumake will do just fine. And finally you need `python3` with `pip`, from which the make will create a `virtualenv`.

## Playtime!
1. duplicate `secrets.vault_example` into `secrets.vault` and fill in your contest login/pass.
2. from the top level folder, run `make venv` to generate your virtual environment
3. `make simroll` to run all 3 demo algorithms, and opens up the reports.
4. `make freeze` you can skip for now, but later do try it.
5. `make upload` to upload to the FTP.  

# Competition code
Organizers provided example code for each of the three contests:
https://dynamic-pricing-competition.com/#scenarios

the code source is located inside `src`

the unit test code is in
`tst`
and you run it once with `make unittest`. However, it's much more convenient to `make testwatch` and just let the console re-test all unit tests on any file saved, automatically.

Test Driven Dev - here we come!

# Automation (Makefile)
To speed up mundane tasks the Makefile offers several targets.

`make simroll`

  - local run of the 3 algorithms to test they are free of errors.
  - each generates an Excel report (3x)
  - 'roll' it over = timestamp the Excel report, move into the archive  to prevent conflicts of multiple runs. These are NOT checked into GIT.

`make venv`
  - creates a virtual environment, from the `requirements.txt`
  - use to test before upload to contest, to check your requirements.txt is complete
  - you can now - from the command line - `source venv/bin/activate` to run it (UNIX).

`make freeze`

  - freeze the virtual env accumulated pip installs into `requirements.txt` (in the root folder)
  - note that `requirements.txt` is uploaded to the contest FTP

`make upload`
  - Upload the files to the competition server (FTP) into a "today" dated folder.
  - needs login/pass set in `secrets.vault`. Create yours using `secrets.vault_example` as a starting point.

Remote testing is described:
https://dynamic-pricing-competition.com/#testing
