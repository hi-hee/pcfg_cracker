
"""

24.04.30 added by Seunghee Seo.

"""


#######################################################
# Unit tests for syllable string detection  
# 
# 24.04.30 Korean syllable test
# 
#######################################################


import unittest
import unittest.mock


## Functions to tests
from ..detection_rules.syllable_detection import syllable_detection

## Testing list:
#  + Test Korean String
#  + Test None Korean String
#  + Test 0 distance between consonants (Double vowels)
#  + Test 1 distance between consonants
#  + Test 2 distance between consonants
#  + Test 3 distance between consonants (Consonant Cluster)
#  + Test mixed distances
#  + Test constraint of fortes onset only (FORTES)



class Test_Korean_Syllable_Check(unittest.TestCase):

    def test_korean_string(self):
        section_list = [('qkskskdndb', 'A10')] #바나나여유

        found_korean_string = syllable_detection(section_list)
        
        assert found_korean_string == ['qkskskdndb']
        assert section_list == [('qkskskdndb', 'H5')]
    

    def test_none_korean_string(self):
        section_list = [('partha', 'A6'), ('EthanRyan', 'A'), ('woshishei', 'A')]
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == []
        assert section_list == [('partha', 'A6'), ('EthanRyan', 'A'), ('woshishei', 'A')]


    def test_0_distance(self):
        #D_VOWEL = ['hk', 'ho', 'hl', 'nj', 'np', 'nl', 'ml']
        section_list = [('dhkdwk', 'A6'), ('rhoscns', 'A5'), ('snlwlq', 'A5'), #왕자, 괜춘, 뉘집
                        ('anjsel', 'A5'), ('dnpgktm', 'A5'), ('dnlfP', 'A5'), #뭔디, 웨하스, 위례
                        ('rmlduq', 'A5')] #긔엽
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['dhkdwk', 'rhoscns','snlwlq','anjsel','dnpgktm','dnlfP','rmlduq']
        assert section_list == [('dhkdwk', 'H2'), ('rhoscns', 'H2'), ('snlwlq', 'H2'),
                                ('anjsel', 'H2'), ('dnpgktm', 'H3'), ('dnlfP', 'H2'), 
                                ('rmlduq', 'H2')] 
        

    def test_1_distance(self):
        section_list = [('ehtl', 'A4')] #도시
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['ehtl']
        assert section_list == [('ehtl', 'H2')]


    def test_2_distance(self):
        section_list = [('tlsehtl', 'A7')] #신도시
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['tlsehtl']
        assert section_list == [('tlsehtl', 'H3')]


    def test_3_distance(self):
        #CONS_CLUSTER = ['rt', 'sw', 'sg', 'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'qt']
        section_list = [('tlfgdj', 'A6')] #싫어
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['tlfgdj']
        assert section_list == [('tlfgdj', 'H2')]


    def test_mixed_distances(self):
        section_list = [('tlfgdjdhod', 'A10')] #싫어왱
        
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['tlfgdjdhod']
        assert section_list == [('tlfgdjdhod', 'H3')]


    def test_constraint_of_fortes_onset_only(self):
        # CONSTR_ONSET_ONLY = ['Q', 'W', 'E'] ㅃㅉㄸ
        section_list = [('Wkwkdaus', 'A8'), ('qkQ', 'A3'), ('WkW', 'A3'), ('ekE', 'A3')]
        #바ㅃ 짜ㅉ 다ㄸ
        found_korean_string = syllable_detection(section_list)

        assert found_korean_string == ['Wkwkdaus'] #짜장면
        assert section_list == [('Wkwkdaus', 'H3'), ('qkQ', 'A3'), ('WkW', 'A3'), ('ekE', 'A3')]
    
