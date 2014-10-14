# Userusage documentation
         
# description

UserUsage will scan a disk or a partition for any given
user's space usage on that disk and email or list those
users. It is build in Python with some core Unix utilities
for speed. It makes use of the speed of "find -exec" while
utilizing Python for combining that data.

# Warning

Userusage comes with no guarantee, warranty,or suggestion 
that it even remotely does what it's supposed to.

# Commands

* -h/--help: Display the help message and exit
* -u/--usage: Display the usage message and exit

* -r/--recursive: Run UserUsage in recursive mode
* --home-dir: Scan every user's home directory
* -p/--partition: Specify the partition to check
* -t/--threshold: Set threshold for specified partition to run UserUsage
* -d/--directory: Set directory to run UserUsage in

* --list-size: List users who are over a specified size
* --list-top: List the top space using users, -1 lists all users
* --sort: Sort list alphabetically

* --mail-size: Mail users who are over a specified size
* --mail-top: Mail the top space using users, -1 mails all users
* --mail-root: mail root a full report

* -v/--verbose: Run in verbose mode
* -vv/--very-verbose: Very verbose, much print, wow
* --config: specify a path to read the config from
* -db/--debug: Same as very verbose but don't mail anyone

* --version: Get UserUsage version

# Exit codes

There are 4 exit codes in UserUsage.
	0 is a successful exit, or in some cases an ArgParse error
	1 is an expected error, which usually is given context
	2 is an unexpected error, I.E. a code error, not a user error
	3 is if somehow we get out of main()

# Examples

UserUsage is built to be run as a weekly or manually kind of deal
Due to this, there are some sets of commands that everyone should
keep in mind. Also note that these will run with default configs
without much trouble.

1. userusage -db
	The simplest of commands. List all and mail none + very
	verbose. Fairly straightforward and useful if you just
	want to check your users usage.

2. userusage -vv --list-top -1 -r -p / -d / 1>&2 /var/log/userusage.log
	typical weekly cronjob of userusage. Mail top 10 users, list all,
	mail top 10, pipe errors and output from very verbose into a log
	file and check the whole drive for users recursively. It only does
	this if the root partition is over 95%

3. userusage -vv 1>&2 /var/log/userusage.log
	The quick version of the cronjob deal. Mail 10 list 0 nonrecursive
	check of the home directory. Only runs if /home partition is above
	95%

4. userusage -h
	help meeeeeee

If you have a solid config in /etc you can just do something along the
lines of

1. userusage 1>&2 /var/log/userusage.log

and it will go perfectally fine.

# Extra comments

Userusage is licensed by Beerware r42
The code is open and fairly well commented, so it should be followed
pretty easily for anyone who knows Python.

If you have bugs and stuff, email me will.drach@live.com or DM me on
Twitter @Merglyn or Reddit /u/Merglyn


