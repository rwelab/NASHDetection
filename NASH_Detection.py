import pandas as pd

#Import df
df = pd.read_parquet('path_to_df.parquet')

##Examine different 'Assessment and Plan' sections
def identify_AP_sections(df):
    #The following commands expect 'note_text' as the column for the clinical notes
    df['AP0_section'] = df['note_text'].str.contains("ASSESSMENT", case=True,na=False)
    df['AP1_section'] = df['note_text'].str.contains("A & P", case=True,na=False)
    df['AP2_section'] = df['note_text'].str.contains("A / P", case=True,na=False)
    df['AP3_section'] = df['note_text'].str.contains("A AND P", case=True,na=False)
    df['AP4_section'] = df['note_text'].str.contains("Assessment and Plan", case=True,na=False)
    df['AP5_section'] = df['note_text'].str.contains("attending attestation", case=False,na=False)
    df['AP6_section'] = df['note_text'].str.contains("assessment and plan", case=False,na=False)
    df['AP7_section'] = df['note_text'].str.contains("assessment", case=False,na=False) #Look at most general regex as well
    df['AP8_section'] = df['note_text'].str.contains("assessment:", case=False,na=False) 
    df['AP9_section'] = df['note_text'].str.contains("Assessment and Recommendation", case=True,na=False) 
    df['AP10_section'] = df['note_text'].str.contains("Assessment/Plan", case=True,na=False) 
    return df

df = identify_AP_sections(df)

df['AP_section_count'] = df['AP0_section'].astype(int) + df['AP1_section'].astype(int) + df['AP2_section'].astype(int) + df['AP3_section'].astype(int) + df['AP4_section'].astype(int) + df['AP5_section'].astype(int)

print(df['AP_section_count'].value_counts())

for column in ['AP0_section', 'AP1_section', 'AP2_section', 'AP3_section', 'AP4_section', 'AP5_section', 'AP6_section', 'AP7_section', 'AP8_section', 'AP9_section', 'AP10_section']:
    print(column)
    print(df[column].value_counts(), '\n')


##After inspection of above, include notes with the below headings:
#AP0_section (ASSESSMENT, cased)
#AP4_section (Assessment and Plan, cased)
#AP8_section (assessment:, uncased)
#AP9_section (Assessment and Recommendation, cased)
#AP10_section (Assessment/Plan, cased)

df = df[(df['AP0_section'] == True)|(df['AP4_section'] == True)|(df['AP8_section'] == True)|(df['AP9_section'] == True)|(df['AP10_section'] == True)]

##Now extract the text after 'Assessment' etc headings, sequentially:
def include_notes_w_assessment_section_only(df):
    #The following commands expect 'note_text' as the column for the clinical notes
    
    #Include:
    #AP0_section (ASSESSMENT, cased)
    #AP4_section (Assessment and Plan, cased)
    #AP8_section (assessment:, uncased)
    #AP9_section (Assessment and Recommendation, cased)
    #AP10_section (Assessment/Plan, cased)

    #This is in order of prevalence
    AP0= df.loc[df['note_text'].str.contains("ASSESSMENT", case=True,na=False)]
    AP4= df.loc[df['note_text'].str.contains("Assessment and Plan", case=True,na=False)]
    AP8= df.loc[df['note_text'].str.contains("assessment:", case=False,na=False)] #keep this uncased
    AP9= df.loc[df['note_text'].str.contains("Assessment and Recommendation", case=True,na=False)]
    AP10= df.loc[df['note_text'].str.contains("Assessment/Plan", case=True,na=False)]
    
    AP0['AP_number'] = 0
    AP4['AP_number'] = 1
    AP8['AP_number'] = 2
    AP9['AP_number'] = 3
    AP10['AP_number'] = 4

    AP0['AP'] = AP0['note_text'].str.split('ASSESSMENT',2)
    AP4['AP'] = AP4['note_text'].str.split('Assessment and Plan',2)
    AP8['AP'] = AP8['note_text'].str.lower().str.split('assessment:',2) #Need to convert text to lowercase as str.split() doesn't have an uncased option
    AP9['AP'] = AP9['note_text'].str.split('Assessment and Recommendation',2)
    AP10['AP'] = AP10['note_text'].str.split('Assessment/Plan',2)

    dfs = pd.concat([AP0,AP4,AP8,AP9,AP10])
    dfs.drop_duplicates(subset='deid_note_key', inplace=True) #This keeps the text from the earliest form of segmentation (e.g ASSESSMENT then 'A & P' etc) in column 'AP'

    dfs['AP2']=dfs['AP'].str[1] #This str.split above splits the text into a list before and after the regex; hence AP2 looks only at the str after each regex
    
    return dfs

df_APonly = include_notes_w_assessment_section_only(df)

##NASHDetection function:
def identify_NASH_notes(df):
    NASH_exclusion_criteria_regex_original_NASH = ['without NASH', 'not consistent with NASH', 'low suspicion for NASH', 'no evidence of NASH', 
                                'lack of NASH risk factors', 'no NASH', 'may be NASH', 'not mention NASH', 'no evidence of nonalcoholic steatohepatitis', 
                                     'no evidence of non-alcoholic steatohepatitis', 'no evidence of non alcoholic steatohepatitis']
    
    NASH_exclusion_criteria_regex_original_MASH = ['without MASH', 'not consistent with MASH', 'low suspicion for MASH', 'no evidence of MASH', 
                                'lack of MASH risk factors', 'no MASH', 'may be MASH', 'not mention MASH', 'no evidence of metabolic dysfunction-associated steatohepatitis', 
                                     'no evidence of metabolic dysfunction associated steatohepatitis']

    NASH_exclusion_criteria_regex_original = NASH_exclusion_criteria_regex_original_NASH + NASH_exclusion_criteria_regex_original_MASH
    
    #Added 'not mention NASH', 'no evidence of nonalcoholic steatohepatitis' to Balu's exclusion criteria
    negation_phrases_NASH = ["without NASH" , "NOT consistent with NASH" , "low suspicion for NASH", "no evidence of NASH" , "lack of NASH risk factors" , "no NASH" , "less likely for her to have recurrent NASH" , "did not have evidence of NASH" , "does have risk factors for NAFLD/NASH" , "without evidence of steatohepatitis" , "not meeting criteria for diagnosis of NASH" , "not classical for NASH" , "presence of NASH is unlikely" , "No clear NASH" , "not have active NASH" , "no evidence of active steatohepatitis" , "did not have significant fibrosis or evidence of inflammatory \*\*\*\*\* concerning for NASH" , "no evidence of steatohepatitis"]
    negation_phrases_MASH = ["without MASH" , "NOT consistent with MASH" , "low suspicion for MASH", "no evidence of MASH" , "lack of MASH risk factors" , "no MASH" , "less likely for her to have recurrent MASH" , "did not have evidence of MASH" , "does have risk factors for MAFLD/MASH" , "without evidence of steatohepatitis" , "not meeting criteria for diagnosis of MASH" , "not classical for MASH" , "presence of MASH is unlikely" , "No clear MASH" , "not have active MASH" , "no evidence of active steatohepatitis" , "did not have significant fibrosis or evidence of inflammatory \*\*\*\*\* concerning for MASH" , "no evidence of steatohepatitis"]
    negation_phrases = negation_phrases_NASH + negation_phrases_MASH
    
    non_positive_phrases_NASH = ["shares many pathogenic features in common with NASH" , "determine if he has NASH" , "monitor for nonalcoholic steatohepatitis", "monitor for non-alcoholic steatohepatitis", "monitor for non alcoholic steatohepatitis" , "evaluate for possible NASH" , "Phase III study will be started soon in patients with NASH" , "We did not spend much time discussing \*\*\*\*\* vs. NASH and will discuss this more at our next visit if the diagnosis is clear." , "would consider pursuing liver biopsy to assess for AIH vs NASH" , "risk for progression to NASH" , "consideration for liver biopsy to assess for etiology of elevated liver enzymes such as seronegative AIH, NASH" , "assess for NASH" , "prevent development of concurrent NASH" , "concerning for underlying inflammation and NASH" , "high risk for progression to NASH" , "initially thought to relate to alcohol or combination of \*\*\*\*\* and NASH" , "Patient had NASH fibrosis score checked" , "liver tests would be atypical for NAFLD/NASH alone"  , "vs NASH" , "assess for nonalcoholic steatohepatitis \(NASH\)" , "assess for non alcoholic steatohepatitis \(NASH\)" , "assess for non-alcoholic steatohepatitis \(NASH\)" , "association between NASH and PCOS" , "has been associated with development of fatty liver and steatohepatitis" , "evaluate for AIH +/- NASH" , "at risk for concurrent NAFLD and NASH" , "risk factors for NASH" , "also seen with NASH" , "NASH risk factors" , "assessment of NASH" , "risk for non-alcoholic steatohepatitis" , "risk for nonalcoholic steatohepatitis" , "risk for non alcoholic steatohepatitis" , "risk factors for the development of NASH" , "may relate to NAFLD/NASH" , "assess for NASH" , "rule out NASH" , "potential for progression to NASH" , "Vitamin E is reserved for biopsy-proven NASH" , "risk for developing NAFLD/NASH" , "risk for NASH" , "clarify whether this presents NASH" , "evaluate for NASH" , "evaluate the presence of NASH" , "differential diagnosis for cirrhosis in this patient includes alcoholic cirrhosis, NASH"]
    non_positive_phrases_MASH = ["shares many pathogenic features in common with MASH" , "determine if he has MASH" , "monitor for metabolic dysfunction associated steatohepatitis" ,"monitor for metabolic dysfunction-associated steatohepatitis" , "evaluate for possible MASH" , "Phase III study will be started soon in patients with MASH" , "We did not spend much time discussing \*\*\*\*\* vs. MASH and will discuss this more at our next visit if the diagnosis is clear." , "would consider pursuing liver biopsy to assess for AIH vs MASH" , "risk for progression to MASH" , "consideration for liver biopsy to assess for etiology of elevated liver enzymes such as seronegative AIH, MASH" , "assess for MASH" , "prevent development of concurrent MASH" , "concerning for underlying inflammation and MASH" , "high risk for progression to MASH" , "initially thought to relate to alcohol or combination of \*\*\*\*\* and MASH" , "Patient had MASH fibrosis score checked" , "liver tests would be atypical for MAFLD/MASH alone"  , "vs MASH" , "assess for metabolic dysfunction associated steatohepatitis \(MASH\)" , "assess for metabolic dysfunction-associated steatohepatitis \(MASH\)" , "association between MASH and PCOS" , "has been associated with development of fatty liver and steatohepatitis" , "evaluate for AIH +/- MASH" , "at risk for concurrent MAFLD and MASH" , "risk factors for MASH" , "also seen with MASH" , "MASH risk factors" , "assessment of MASH" , "risk for metabolic dysfunction associated steatohepatitis" , "risk for metabolic dysfunction-associated steatohepatitis" , "risk factors for the development of MASH" , "may relate to MAFLD/MASH" , "assess for MASH" , "rule out MASH" , "potential for progression to MASH" , "Vitamin E is reserved for biopsy-proven MASH" , "risk for developing MAFLD/MASH" , "risk for MASH" , "clarify whether this presents MASH" , "evaluate for MASH" , "evaluate the presence of MASH" , "differential diagnosis for cirrhosis in this patient includes alcoholic cirrhosis, MASH"]
    non_positive_phrases = non_positive_phrases_NASH + non_positive_phrases_MASH
    
    #Curate non-positive phrases by inspecting value_counts of 
    explore_50_phrases_NASH = ['Liver biopsy is required to distinguish between so-called \"\*\*\*\*\*\" steatosis \(no inflammation\) and steatohepatitis \(NASH\)', 'to differentiate between benign steatosis vs. nonalcoholic steatohepatitis is to do a liver biopsy', '\-\- NASH\: A1c, Lipid panel', 'We did not spend much time discussing \*\*\*\*\* vs. NASH and will discuss this more at our next visit', 'without inflammation, steatohepatitis \(NASH\; fat \+ inflammation in a characteristic pattern\)', 'Vitamin E has been demonstrated to improve hepatic steatosis and inflammation in non-diabetic patients with NASH.', 'steatosis \(no inflammation\) and steatohepatitis \(NASH\)', 'Only patients with biopsy-proven NASH should be treated with vitamin E.', 'whereas NASH can progress to cirrhosis.', 'inflammation in non-diabetic patients with NASH.']
    explore_50_phrases_MASH = ['Liver biopsy is required to distinguish between so-called \"\*\*\*\*\*\" steatosis \(no inflammation\) and steatohepatitis \(MASH\)', 'to differentiate between benign steatosis vs. metabolic dysfunction-associated steatohepatitis is to do a liver biopsy', '\-\- MASH\: A1c, Lipid panel', 'We did not spend much time discussing \*\*\*\*\* vs. MASH and will discuss this more at our next visit', 'without inflammation, steatohepatitis \(MASH\; fat \+ inflammation in a characteristic pattern\)', 'Vitamin E has been demonstrated to improve hepatic steatosis and inflammation in non-diabetic patients with MASH.', 'steatosis \(no inflammation\) and steatohepatitis \(MASH\)', 'Only patients with biopsy-proven MASH should be treated with vitamin E.', 'whereas MASH can progress to cirrhosis.', 'inflammation in non-diabetic patients with MASH.']

    explore_50_phrases = explore_50_phrases_NASH + explore_50_phrases_MASH
    
    other_phrases_after_manual_review_NASH = ['low risk category for NASH', ' or NASH', ' or non-alcoholic steatohepatitis', ' or nonalcoholic steatohepatitis', ' or non alcoholic steatohepatitis', 'vs. NASH', 'vs NASH', 'vs. non-alcoholic steatohepatitis', 'vs non-alcoholic steatohepatitis', 'vs. non alcoholic steatohepatitis', 'vs non alcoholic steatohepatitis', 'vs. nonalcoholic steatohepatitis', 'vs nonalcoholic steatohepatitis', 'If found to have NAFLD we will discuss the role of liver biopsy which is currently required for the diagnosis of fat related inflammation and scarring known as non alcoholic steatohepatitis \(NASH\)', 'between \*\*\*\*\* and NASH', 'did not have clear NASH', 'The use of vitamin E should be reserved only for patients with biopsy-proven NASH', 'NAFLD is an umbrella term that encompasses both nonalcoholic fatty liver \(\*\*\*\*\*\) or non-alcoholic steatohepatitis \(NASH\).', 'no risk factors for nonalcoholic steatohepatitis', 'vitamin E is reserved for patients with biopsy proven NASH', 'the typical causes of abnormal liver function tests lasting for longer than 6 months: NAFLD/NASH']
    other_phrases_after_manual_review_MASH = ['low risk category for MASH', ' or MASH', ' or metabolic dysfunction associated steatohepatitis', ' or metabolic dysfunction-associated steatohepatitis', 'vs. MASH', 'vs MASH', 'vs. metabolic dysfunction associated steatohepatitis', 'vs metabolic dysfunction-associated steatohepatitis', 'If found to have MAFLD we will discuss the role of liver biopsy which is currently required for the diagnosis of fat related inflammation and scarring known as metabolic dysfunction-associated steatohepatitis \(MASH\)', 'between \*\*\*\*\* and MASH', 'did not have clear MASH', 'The use of vitamin E should be reserved only for patients with biopsy-proven MASH', 'MAFLD is an umbrella term that encompasses both metabolic dysfunction-associated fatty liver \(\*\*\*\*\*\) or metabolic dysfunction-associated steatohepatitis \(MASH\).', 'no risk factors for metabolic dysfunction-associated steatohepatitis', 'vitamin E is reserved for patients with biopsy proven MASH', 'the typical causes of abnormal liver function tests lasting for longer than 6 months: MAFLD/MASH']  
    other_phrases_after_manual_review = other_phrases_after_manual_review_NASH + other_phrases_after_manual_review_MASH
    
    #141123 update - add the above negation_phrases and non_positive_phrases to the exclusion criteria
    NASH_exclusion_criteria_regex_updated = NASH_exclusion_criteria_regex_original.copy()
    NASH_exclusion_criteria_regex_updated.extend(negation_phrases)
    NASH_exclusion_criteria_regex_updated.extend(non_positive_phrases)
    NASH_exclusion_criteria_regex_updated.extend(explore_50_phrases)
    NASH_exclusion_criteria_regex_updated.extend(other_phrases_after_manual_review)
    #Drop duplicates in list and get list length
    NASH_exclusion_criteria_regex_updated = list(set(NASH_exclusion_criteria_regex_updated))
    print(len(NASH_exclusion_criteria_regex_updated))
   
    # Define the two biopsy_proven_str phrases
    phrase1 = 'Liver biopsy is required to distinguish between'
    phrase2 = 'patients with biopsy-proven NASH'
    phrase2b = 'patients with biopsy-proven MASH'
    phrase3 = 'Only patients with biopsy-proven' #Sometimes, NASH in phase2 has been redacted - in these cases, we still want to remove NASH mentions from the earlier parts of the section, hence add in this phrase3 to do this
    # Create a regular expression pattern to extract text between the two phrases
    biopsy_proven_pattern = f'{phrase1}(.*?){phrase2}'
    biopsy_proven_pattern2 = f'{phrase1}(.*?){phrase3}'
    biopsy_proven_pattern3 = f'{phrase1}(.*?){phrase2b}'
    
    #Replace excluded strings with dummy string '##negatedtermremoved##' (so they are negated and not retrieved when applying the NASH_inclusion_criteria_regex below)
    df['AP2_negation_replaced'] = df['AP2'].str.replace(biopsy_proven_pattern, '##negatedtermremoved##', case = False)
    df['AP2_negation_replaced'] = df['AP2_negation_replaced'].str.replace(biopsy_proven_pattern2, '##negatedtermremoved##', case = False)
    df['AP2_negation_replaced'] = df['AP2_negation_replaced'].str.replace(biopsy_proven_pattern3, '##negatedtermremoved##', case = False)
    
    ##Replace the remaining mentions of NASH in the exclusion list with dummy string '##negatedtermremoved##' (so they are negated and not retrieved when applying the NASH_inclusion_criteria_regex below)
    print('Onto for-loop')
    for pattern in NASH_exclusion_criteria_regex_updated:
        df['AP2_negation_replaced'] = df['AP2_negation_replaced'].str.replace(pattern, '##negatedtermremoved##', case=False)
    
    #Include only notes with items in NASH_inclusion_criteria_regex in the AP2 section; set case=False to include any case
    NASH_inclusion_criteria_regex = ['nonalcoholic steatohepatitis', 'non-alcoholic steatohepatitis', 'non alcoholic steatohepatitis', 'NASH', 'MASH', 'metabolic dysfunction-associated steatohepatitis', 'metabolic dysfunction associated steatohepatitis']    
    df_positive = df[df['AP2_negation_replaced'].str.contains('|'.join(NASH_inclusion_criteria_regex), case=False)]
    df_negative = df[~df['AP2_negation_replaced'].str.contains('|'.join(NASH_inclusion_criteria_regex), case=False)]
    
    #Create output df where you have label for 1 (NASH diagnosis in note) vs 0 (no NASH diagnosis in note)
    df_positive['NASH_diagnosis_label'] = 1
    df_negative['NASH_diagnosis_label'] = 0
    #Concatenate back together
    df_output = pd.concat([df_positive, df_negative])
    
    print(df_positive.deid_note_key.nunique())
    print(df_negative.deid_note_key.nunique())
    print(df_output.deid_note_key.nunique())
    #
    print(df_positive.shape)
    print(df_negative.shape)
    print(df_output.shape)
    #
    
    return df_positive, df_negative, df_output

##Run above function and generate positive and negative datasets
df_APonly_NASHpositive, df_APonly_NASHnegative, df_APonly_labelled = identify_NASH_notes(df_APonly)
