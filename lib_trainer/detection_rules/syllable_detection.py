

"""

24.04.09 added by Seunghee Seo.

This file contains the functionality to identify syllable tokens

Note, some strings may be classified before this is called 
in the detection process of email and website.

"""


# from nltk.tokenize import SyllableTokenizer
# from nltk import word_tokenize


def check_d_vowel(vowel_str):
    ''' 
    Checking whether the vowel set is a double vowel
    
    Variables: 
        vowel_str : a vowel chunk having 2 of length.
    
    Returns:
        Boolean : return TRUE, when the vowel chunk is a double vowel

    '''

    if (vowel_str[0] == 'h') and (vowel_str[1] in ['k', 'o', 'l']):
        return True
    elif (vowel_str[0] == 'n') and (vowel_str[1] in ['j', 'p', 'l']):
        return True
    elif (vowel_str[0] == 'm') and (vowel_str[1] =='l'):
        return True
    else:
        ## the string unsatisfies a condition of the double vowel
        return False
        

def detect_korean(section):
    ''' 
    Detecting strings having the order of Korean, when converting the string following Keyboard layout.
    For examples, tkfkd -> 사랑

    Variables:
        section: The current section of the password to process

    Returns:
        There are three return values:

        parsing, found_strings

        parsing: A list of the sections to return
        E.g. input password is '123tkfkd'
        parsing should return:
        [('tkfkd','H')]

        found_strings: A list containing all the korean strings found for a section

    '''

    # Consonant set
    LENIS = ['q', 'w', 'e', 'r', 't', 'a', 's', 'd', 'f', 'g', 'z', 'x', 'c', 'v']
    FORTES = ['Q', 'W', 'E', 'R', 'T']
    CONS_CLUSTER = ['rt', 'sw', 'sg', 'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'qt']

    # Vowel set
    VOWEL = ['y', 'u', 'i', 'o', 'p', 'h', 'j', 'k', 'l', 'b', 'n', 'm', 'O', 'P']      
    D_VOWEL = ['hk', 'ho', 'hl', 'nj', 'np', 'nl', 'ml']    #Double vowel

    # Korean Syllable Rules
    CONSTR_ONSET_ONLY = ['Q', 'W', 'E']

    working_string = section[0]
    parsing = []

    ## A Onset Constraint (Onset should be lenis or fortes)
    if not working_string[0] in LENIS+FORTES:
        return section, None
    
    ## Checking an onset of the first syllable
    if not working_string[1] in VOWEL:
        return section, None
    
    ## Extracting the position of vowels
    vowel_pos = []
    for pos, value in enumerate(working_string):
        if value in VOWEL:
            vowel_pos.append(pos)

    ## Checking the Korean syllable rule
    ksr_flag = True
    idx = 0
    syllable_len =0

    while idx < len(vowel_pos):
        syllable_len+=1

        if idx+1 >= len(vowel_pos):
            # Checking a consonant of the last syllable 
            cons_len = len(working_string)-vowel_pos[idx]-1

            if cons_len == 0: # when consonant is empty
                break
            elif cons_len == 1: # when the length of consonant is 1
                if not working_string[vowel_pos[idx]+1] in CONSTR_ONSET_ONLY:
                    break
            elif cons_len == 2: # when the length of consonant is 2
                if working_string[vowel_pos[idx]+1:] in CONS_CLUSTER:
                    break
            ksr_flag = False
            break

        
        dist = vowel_pos[idx+1] - vowel_pos[idx] 
        a_pos = vowel_pos[idx]
        if dist == 1:
            if not check_d_vowel(working_string[a_pos:a_pos+2]):
                # alpha string is not hangeul string
                ksr_flag = False
                break
            idx+=1
        elif dist == 2:
            if not working_string[a_pos+1] in LENIS+FORTES:
                # alpha string is not hangeul string
                ksr_flag = False
                break
        elif dist == 3:
            if working_string[a_pos+1] in CONSTR_ONSET_ONLY:
                # alpha string is not hangeul string
                ksr_flag = False
                break
        elif dist == 4:
            if not working_string[a_pos+1:a_pos+3] in CONS_CLUSTER:
                # alpha string is not hangeul string
                ksr_flag = False
                break
        idx+=1

    ## Update the parsing info
    if ksr_flag:
        parsing.append((section[0], 'H' + str(syllable_len)))
        return parsing, section[0]

    return section, None


def detect_greek():

    pass

def detect_japanese():

    pass


def syllable_detection(section_list):
    """
    Finds Greek or Korean syllable strings in alpha strings

    For example tkfkd123% will extract 'tkfkd'

    Returns:
        Returns one lists, korean_list

        korean_list: A list of korean strings that were detected

    """
    
    ## Detecting korean ##
    #
    # Walk through each section and find korean(hangeul) string 
    #

    korean_list = []

    index = 0
    while index < len(section_list):
        if 'A' in section_list[index][1]:

            parsing, korean_string = detect_korean(section_list[index])

            if korean_string is not None:
                korean_list.append(korean_string)
            
                del section_list[index]
                section_list[index:index] = parsing

        index +=1

    return korean_list


    ## Detecting Greek ##
    # TBC