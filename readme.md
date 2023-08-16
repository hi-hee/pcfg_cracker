PCFG = Probabilistic Context Free Grammar


PCFG = Pretty Cool Fuzzy Guesser

In short: A collection of tools to perform research into how humans generate passwords. These can be used to crack password hashes, but also create synthetic passwords (honeywords), or help develop better password strength algorithms

## Tool Versions
**Trainer:** 4.4

**Guesser:** 4.5

**PRINCE_LING:** 4.3

**Password_Scorer:** 4.4

## Documentation

Sphinx is used to dynamically create a Developer's Guide based on docstrings in the code. To build the Developer's Guide, refer to the instructions in /doc/INSTRUCTIONS.rst

A pre-built Developer's Guide PDF can also be found in /doc/build/latex/pcfgdevelopersguide.pdf. Note, I'm not going to rebuild this guide between major releases to make the git history cleaner. Aka committing PDFs gets real messy real quick. This means the pre-build guide it may be slightly out of date so if you are using it to help you write/modify code it's recommended to build the guide yourself instead of using the prebuilt one.

## Overview

This project uses machine learning to identify password creation habits of users. A PCFG model is generated by training on a list of disclosed plaintext/cracked passwords. In the context of this project, the model is referred to as a ruleset and contains many different parts of the passwords identified during training, along with their associated probabilities. This stemming can be useful for other cracking tools such as PRINCE, and/or parts of the ruleset can be directly incorporated into more traditional dictionary-based attacks. This project also includes a PCFG guess generator that makes use of this ruleset to generate password guesses in probability order. This is much more powerful than standard dictionary attacks, and in testing has proven to be able to crack passwords on average with significantly less guesses than other publicly available methods. The downside is that generating guesses in probability order is slow, meaning it is creating on average 50-100k guesses a second, where GPU based algorithms can create millions to billions (and up), of guesses a second against fast hashing algorithms. Therefore, the PCFG guesser is best used against large numbers of salted hashes, or other slow hashing algorithms, where the performance cost of the algorithm is made up for with the accuracy of the guesses.

## Requirements + Installation
- Python3 is the only hard requirement for these tools
- It is **highly recommended** that you install the chardet python3 library for training. While not required, it performs character encoding autodetection of the training passwords. To install it:
 - Download the source from [https://pypi.python.org/pypi/chardet](http://https://pypi.python.org/pypi/chardet "https://pypi.python.org/pypi/chardet")
 - Or install it using `pip3 install chardet`

## Quick Start Guide
### Training
The default ruleset included in this repo was created by training on a 1 million password subset of the RockYou dataset. Better performance can be achieved by training on the full 32 million password set for RockYou, but that was excluded to keep the download size small. You can use the default ruleset to start generating passwords without having to train on a new list, but it is recommended to train on a target set of passwords that may be closer to what you are trying to target. If you do create your own ruleset, here is a quick guide:
1. Identify a set of plaintext passwords to train on. 
 - This passwords set should include duplicate passwords. That way the trainer can identify common passwords like 123456 are common.
 - The passwords should be in plaintext with hashes and associated info like usernames removed from them. Don't try to use raw .pot files as your training set as the hashes will be considered part of the password by the training program.
  - The passwords should be encoded the same way you want to generate password guesses as. So, if you want to create UTF-8 password guesses, the training set should also be encoded as UTF-8. Long term, the ability to modify this when generating guesses is on the development plan, but that feature is currently not supported.
  - The training password list should be between 100k and 50 million. Testing is still being done on how the size of the training password list affects guess generation, and there has been good success even with password lists as small as 10k, but an ideal size is likely around 1 million, with diminishing returns after that.
  - For the purposes of this tutorial the input password list will be referred to as INPUT_PASSWORD_LIST
2. Choose a name for your generated ruleset. For the purposes of this tutorial it will be NEW_RULESET
3. Run the trainer on the input password list
 - `python3 trainer.py -t INPUT_PASSWORD_LIST -r NEW_RULESET`
 - Common optional flags:
   a. **coverage**: How much you trust the training set to match the target passwords. A higher coverage means to use less intelligent brute force generation using Markov modeling, (currently using the OMEN algorithm). If you set coverage to 1, no brute force will be performed. If you set coverage to 0, it will only generate guesses using Markov attacks. This value is a float, with the default being 0.6 which means it expects a 60% chance the target password's base words can be found in the training set. Example: `python3 trainer.py -t INPUT_PASSWORD_LIST -r NEW_RULESET -c 0.6`
   b. **--save_sensitive**: If this is specified, sensitive data such as e-mail addresses and full websites which are discovered during training will be saved in the ruleset. While the PCFG guess generator does not currently make use of this data, it is very valuable during a real password cracking attack. This by default is off to make this tool easier to use in an academic setting. Note, even when this is off, there will almost certainly still be PII data saved inside a ruleset, so protect generated rulesets appropriately. Example: `python3 trainer.py -t INPUT_PASSWORD_LIST -r NEW_RULESET --save_sensitive`
   c. **--comments**: Adds a comment to your ruleset config file. This is useful so you know why and how you generated your ruleset when looking back at it later. Include the comment you want to add in quotes.
   
### Guess Generation
This generates guesses to stdout using a previously training PCFG ruleset. These guesses can then be piped into any program that you want to make use of them. If no ruleset is specified, the default ruleset **DEFAULT** will be used. For the purposes of this guide it will assume the ruleset being used is **NEW_RULESET**. 

1. Note: the guess generation program is case sensitive when specifying the ruleset name.
-  A session name is not required, (it will by default create a session called **default_run**), but it is helpful to make restarting a paused/stopped session easier. These examples will use the session name **SESSION_NAME**. Note, there is no built in sanity check if you run multiple sessions with the same name at the same time, but it is recommend to avoid that.
2. To start a new guessing session run:
 - `python3 pcfg_guesser.py -r NEW_RULESET -s SESSION_NAME`
3. To restart a previous guessing session run (Note: You still need to specify the same ruleset when restoring a session):
 - `python3 pcfg_guesser.py -r NEW_RULESET -s SESSION_NAME --load`
 
### Password Strength Scoring
There are many cases where you may want to estimate the probability of a password being generated by a previously trained ruleset. For example, this could be part of a password strength metric, or used for other research purposes. A sample program has been included to perform this. 
- INPUT_LIST represents the list of passwords to score. These passwords should be plaintext, and separated by newlines, with one password per line.
1. To run a scoring session: `python3 password_scorer -r NEW_RULESET -i INPUT_LIST`
2. By default. it will output the results to stdout, with each password scored per line
 - The first value is the raw password
 - The second value will represent if the input value was scored a 'password', 'website', 'e-mail address', or 'other'. This determination of password or other is dependent on the limits you set for both OMEN guess limit, as well as probability associated with the PCFG.
 - The third value is the probability of the password according to the Ruleset. If it is assigned a value of 0.0, that means that the password will not be generated by the ruleset, though it may be generated by a Markov based attack
 - The fourth value is the OMEN level that will generate the password. A value of -1 means the password will not be generated by OMEN.

### Prince-Ling Wordlist Generator
**Name:** PRINCE Language Idexed N-Grams (Prince-Ling)

**Overview:** Constructs customized wordlists based on an already trained PCFG ruleset/grammar for use in PRINCE style combinator attacks. The idea behind this was since the PCFG trainer is already breaking up a training set up passwords into individual parsings, that information could be leveraged to make targeted wordlists for other attacks.

**Basic Mechanics:** Under the hood, the Prince-Ling tool is basically a mini-PCFG guess generator. It strips out the Markov guess generation, and replaces the base structures used in normal PCFG attacks with a significantly reduced base-structure tailored for generating PRINCE wordlists. This allows generating dictionary words in probability order with an eye to how useful those words are expected to be in a PRINCE attack. 

**Using Prince-Ling**
1. Train a PCFG ruleset using trainer.py. Note you need to create the ruleset using version 4.1 or later of the PCFG toolset, as earlier versions did not learn all the datastructures that Prince-Ling utilizes.
2. Run Prince-Ling  `python3 prince-ling.py -r RULESET_NAME -s SIZE_OF_WORDLIST_TO_CREATE -o OUTPUT_FILENAME`
 - **--rule**: Name of the PCFG ruleset to create the PRINCE wordlist from
 - **--size**: Number of words to create for the PRINCE wordlist. Note, if not specified, Prince-Ling will generate all possible words which can be quite large depending on if case_mangling is enabled. (Case mangling increases the keyspace enourmously)
  - **--output**: Output filename to write entrees to. Note, if not specified, Prince-Ling will output words to stdout, which may cause problems depending on what shell you are using when printing non-ASCII characters.
  - **--all_lower**: Only generate lowercase words for the PRINCE dictionary. This is useful when attacking case-insensitive hashes, or if you plan on applying targeted case mangling a different way.

### Example Cracking Passwords Using John the Ripper
`python3 pcfg_guesser -r NEW_RULESET -s SESSION_NAME | ./john --stdin --format=bcrypt PASSWORDS_TO_CRACK.txt`

### Contributing
If you notice any bugs, or if you have a feature you would like to see added, please open an issue on this github page. I also accept pull requests, though ideally please link a pull request to an issue so that I can more easily review it, ask questions, and better understand the changes you are making.

There's a lot of improvements that can be made to modeling password creation strategies using PCFGs. I'm very open to new ideas, changes, and suggestions. Just because the code currently does something a certain way doesn't mean that's the best option. For example, the fundamental base_structure of the current approach where masks are generated for alpha strings, digits, other, etc, was chosen because it was the "easiest" option to impliment. My team had a lot of debate that a better option might be to start with a base word, and then model more traditional mangling rules applied to it as transisions in the PCFG. So feel free to go wild with this code!
