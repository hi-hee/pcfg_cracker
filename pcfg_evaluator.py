"""
2024.05.10

Created by Seunghee Seo

"""

import argparse, os, sys

from lib_evaluation.montecarlo_evaluator import MonteCarloEvaluator
#from lib_guesser.grammar_io import load_grammar

def print_banner(program_info):
    """
    ASCII art for the pcfg evaluator banner
    
    no variables and returns
    
    """
    print()
    print('[ '+str(program_info['name'])+' ]')
    print("\nVersion: " + str(program_info['version']))
    print("Sample size: ", program_info['samples_num'])
    print("RuleSet : ", program_info['rule_name'])
    print()
    

def parse_command_line(program_info):
    """
    Responsible for parsing the command line.
    
    Inputs:

        program_info: A dictionary that contains the default values of
        command line options. Results overwrite the default values and the
        dictionary is returned after this function is done.

    Returns:
        True: If the command line was parsed successfully
        False: If an error occured parsing the command line

        (Program Exits): If the --help option is specified on the command line
    """
    
    # Establishing a program arguments
    parser = argparse.ArgumentParser(
        description= '''Evaluting Guessing Performance of models based Monte Carlo Estimation\n
        Created by Seunghee Seo in 2024.05.1\n'''
    )
    
    # The input file containing test passwords to evaluate 
    parser.add_argument(
        '--input',
        '-i',
        help = 'The filename of the input set to score. Newline seperated',
        metavar = 'INPUT_FILENAME',
        required = True
    )
    
    # The rule name to use when evaluating the performance.
    parser.add_argument(
        '--rule',
        '-r',
        help = 'The ruleset to use. Default is ' +
        program_info['rule_name'],
        metavar = 'RULESET_NAME',
        required = False,
        default = program_info['rule_name']
    )
    
    # The number of samples
    parser.add_argument(
        '--samples_num',
        '-n',
        help = 'The number of random samples to estimate the perfomance (Default = 10,000)',
        metavar = 'SMAPLE_NUM',
        required = False,
        default = program_info['samples_num']
    )
    
    # The output file to save results
    parser.add_argument(
        '--output',
        '-o',
        help = 'The output file to save results to. If not specified will output to Evalutaion_Result',
        metavar = 'OUTPUT_FILENAME',
        required = False,
        default = program_info['output_file']
    )
    
    parser.add_argument(
        '--label',
        '-l',
        help = 'The label name to identify the evalution',
        metavar = 'OUTPUT_FILENAME',
        required = False,
        default = program_info['label']
    )
        
    # Parse all the args and save them
    args=parser.parse_args()
    
    program_info['rule_name'] = args.rule
    program_info['input_file'] = args.input
    program_info['output_file']= args.output
    program_info['samples_num']= args.samples_num
    program_info['label']= args.label
    
    return True


def main():
    """
    Main function, starts everything off
    
    Inputs:
        None
        
    Returns:
        None
    """
    
    program_info = {

        # Program and Contact Info
        'name':'PCFG performance evaluator',
        'version': '4.4',
        'author':'Seunghee Seo',
        'contact':'sh.seo.713@gmail.com',

        # Standard Options
        'rule_name':'Default',
        'output_file':None,
        'samples_num':10000,
        'limit':0,
        'label':'',

        # OMEN Options
        #
        # Note, picking 9 as the default because the keyspace when training
        # on rockyou for level 9 is roughly 600 million which seems reasonable
        'max_omen_level':9

    }
    
    # Parsing the command line
    if not parse_command_line(program_info):
        # There was a problem with the command line so exit
        print("Exiting...",file=sys.stderr)
        return
    
    print_banner(program_info)
    
    ## Load Rules file from the standard storage location
    print("Loading Rule: " + str(program_info['rule_name']))
    
     # To set up a path of the rule 
    base_directory = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'Rules',
                        program_info['rule_name'])
    
     # To read rule and init the evaluator
    md_evaluator = MonteCarloEvaluator(
        program_info['rule_name'],
        base_directory,
        program_info['version'],
        program_info['label']
        )
    
    ## Setup evaluator.
        # 1) Random sampling
        # 2) calculating probabilities
        # 3) Position estimatation
    
    md_evaluator.setup()

    ## Evaluate the model performance with the inputs
    # 1) read input
    # 2) calculating probabilities
    # 3) find approximatin of probabilities
    # 4) confirm the position

    md_evaluator.evaluate_PCFG(program_info['input_file'])
   
    ## Write estimation about inputs to draw graph

if __name__ == "__main__":
    main()