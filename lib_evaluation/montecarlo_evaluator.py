"""
2024.05.10

Created by Seunghee Seo

Evaluation Module based on Monte Carlo

"""
'''
TO-DO

1. pdfg grammar load
2. random password gen
3. 

'''

import random, math, sys, time, os
import numpy as np
from datetime import datetime

#from lib_scorer.pcfg_password_scorer import PCFGPasswordScorer
from lib_guesser.pcfg_grammar import PcfgGrammar

class MonteCarloEvaluator(PcfgGrammar):
    
    def __init__(self, 
                rule_name,
                base_directory,
                version,
                label,
                log_scale = 2,
                samples_num = 10000) -> None:
        
        super().__init__(rule_name, base_directory, version)
        self.samples_num = samples_num
        self.label = label
        self.log_scale = log_scale # if the value is not 10, results will be converted to "log2 scale".
        
        self.samples_prob = []
        self.position = []
        
        
        '''
        super().grammar = { pt_type:[{'values':['x', 'x'], 'prob': 0.xx}] }
        eg. {'D3':[{'values':['117', '765', '338', '049'], 'prob':0.001557}, 
                      {'values': ['111'], 'prob': 0.01010}]}
        
        '''
    
    # Overrided by Seunghee Seo
    def random_walk(self):
        """
        Performs a random walk (truely not weighted) of the grammar and returns a pt_item

        Inputs:
            None

        Returns:
            pt_item: The parse tree that specifies the item found in the walk
                     {'based_prob' : 0.x, 'pt':[], 'prob': 0.x }
                     e.g. {'base_prob': 1.0, 'pt': [('K6', 0)], 'prob': 0.4590~}

        """
        # Initialize the pt_item
        pt_item = {
            'base_prob': 1.0,
            'pt': []
        }
        
        # Randomly choose base structure (except 'M')
        isM =True
        while isM:
            rd_base = random.choice(self.base)
            if 'M' not in rd_base['replacements']:
                isM = False
        
        # Update base_prob & pt with the randomly choosed base structure
        pt_item['base_prob'] = rd_base['prob']
        for replacement in rd_base['replacements']:
            pt_item['pt'].append((replacement,0))

        # Now go through each item and perform a random walk for it as well
        for pointer, item in enumerate(pt_item['pt']):
            
            pt_type = item[0]
            
            # Randomly selecting the index
            max_index = len(self.grammar[pt_type]) 
            
            if max_index == 1:
                rd_index = 0
            else:
                rd_index = random.randint(0, max_index-1)
            
            pt_item['pt'][pointer] =(pt_type, rd_index)
            
        # Calculate the probability
        pt_item['prob'] = self._find_prob(pt_item['pt'], pt_item['base_prob'])

        return pt_item
    
    # Overrided by Seunghee Seo
    def _honeyword_recursive_guess(self, cur_guess, pt, limit = None, cur_prob = 1):
        """
        Recursivly generates a single random guess from a parse tree
        from all of the possible guesses it could generate

        Will print out guesses to stdout

        Inputs:
            cur_guess: The current guess being generated

            pt: The parse tree, which is a list of tuples. Will recursivly work though the pt to
            fill out parts to cur_guess. (e.g. [(A3, 134), (C3, 0)])

            limit: It has not any meaning in this function.
            
            cur_prob: The current cumulative probability of the guess being generated 

        Returns:
            new_guess: An guess (the terminal output)
            new_prob : The cumulative probability of the guess
            
        """

        # Get the transistion category for the current rule, aka 'A' for alpha
        category = pt[0][0][0]

        # Get the type for the transistion, Aka A10 for 10 letter long alpha
        pt_type = pt[0][0]

        # Get he index into the transition, aka the 2nd most probable A10
        index = pt[0][1]
        
        # If it is a Markov guess
        if category == 'M':
            # Not currently supported for honeywords
            return 0

        # If it is a capitalization mask
        elif category == 'C':

            mask_len = len(self.grammar[pt_type][index]['values'][0])

            # Split off the part of the word we need to modify with the mask
            start_word = [cur_guess[:- mask_len]]
            end_word = cur_guess[- mask_len:]

            mask = random.choice(self.grammar[pt_type][index]['values'])
            
            # Apply the capitalization mask
            new_end = []
            idx = 0
            for item in mask:
                if item == 'L':
                    new_end.append(end_word[idx])
                else:
                    new_end.append(end_word[idx].upper())
                idx += 1

            # Recombine the capitalization mask with what came before
            new_guess = ''.join(start_word + new_end)
            
        # If it is any striaght replacement, (digits, letters, etc)
        else:
            item = random.choice(self.grammar[pt_type][index]['values'])
            new_guess = cur_guess + item

        # To calculate the cumulative probability
        new_prob = cur_prob * self.grammar[pt_type][index]['prob']
        
        # Figure out if the guess is ready to be returned or if there is more to do
        if len(pt) == 1:
            return new_guess, new_prob
        else:
            return self._honeyword_recursive_guess(new_guess, pt[1:], limit, new_prob)

    
    def _rd_sampling(self):
        """
        Randomly generating sample guesses to estimate the performance.
        The number of samples defaulted 10,000
        
        Inputs:

        Returns:
            samples: A list of the tuples having guess and probability.
                     The list is sorted in descending order.
                     The probabilities is converted to log2 or log10 scale.
            
        """
        
        samples = []
        # Initializing the seed of random function
        random.seed(datetime.now().microsecond)
        
        for i in range(0, self.samples_num):
            
            # pt_item = {'based_prob' : 0.x, 'pt':[], 'prob': 0.x }
            pt_item = self.random_walk()
    
            samples.append(pt_item['prob'])
            ## If you want to check guess, uncommnent below code
            # new_guess, new_prob = self._honeyword_recursive_guess('', pt_item['pt'])
        
        if self.log_scale != 10:
            # Convert the probabilities to log2 scale
            samples = [-math.log2(x) for x in samples]
            
        else :
            # Convert the probabilities to log10 scale
            samples = [-math.log10(x) for x in samples]
            
        return sorted(samples, reverse=True)
            
        
    def _pos_calculating(self, samples):
        """
        To calculate the position(rank) of each samples.

        Inputs:
            samples: A list of the probabilities.
                     The list is sorted in descending order.
                     The probabilities is converted to log2 or log10 scale.     
        Returns:

        """
        logprobs = np.fromiter((lp for lp in samples), float)
        
        if self.log_scale != 10:
            # Convert the probabilities to log scale
            logn = math.log2(self.samples_num)
        else :
            logn = math.log10(self.samples_num)
        
        # sigma_(1/(p(b)*n))
        self.position = (logprobs - logn).cumsum()
        
        return True
    
    
    def setup(self, samples_num = 10):
        """ Random Sampling and approximate position making to estimate a performance.

        Args:
            samples_num (int, optional): _description_. Defaults to 10,000.
            
        """
        self.samples_num = samples_num
        
        #print(super().initalize_base_structures())
        
        # 1) Random sampling and calculating probabilities
        self.samples_prob = self._rd_sampling()
        
        # 2)  Position estimatation
        if not self._pos_calculating(self.samples_prob):
            print(" _pos_calculating error.")
            sys.exit()
            
    
    def _find_input_prob(self, eval_word):
        return "aa"
        pass
        
    def _find_pos(self, eval_prob):
        return "bb"
        pass
    
    
    def evaluate_PCFG(self, evalset_path, out_path = 'Evaluation_Result/'):
        
        # making label forder
        out_path = out_path + self.label + '/'        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
         
        eval_time = datetime.now()
  
        stat_file = out_path + "evalutaion_config_" + eval_time.strftime("%y%m%d") +".txt"
        out_file = out_path + 'evaluation_result_'+ eval_time.strftime("%y%m%d-%H-%M") +".txt"
        
        start = datetime.now()
        with open(out_file, 'a+', encoding='utf-8') as f_res:
            with open(evalset_path, 'r', encoding='utf-8') as eval_sets:
                eval_num = 0
                
                for e in eval_sets:
                    e_prob = self._find_input_prob(e)
                    e_pos = self._find_pos(e_prob)
                    
                    f_res.writelines(str(e_prob)+","+str(e_pos)+'\n')
                    eval_num+=1
                    
        end = datetime.now()
        # Writing config log
        with open(stat_file, 'a+', encoding='utf-8') as log:
            log.writelines("""[Label-{6}]\nRule_set:{2}\nTest_set:{3}\nTest_set_size:{4}\nSampling_num:{5}\nStart_time:{0}\nExecution_time:{1}s\n\n"""
                           .format(
                               start.strftime("%Y-%m-%d %H:%M:%S"),
                               str((end-start).seconds),
                               self.rulename,
                               evalset_path,
                               str(eval_num),
                               str(self.samples_num),
                               self.label
                           ))
    
        
        
    
        
        