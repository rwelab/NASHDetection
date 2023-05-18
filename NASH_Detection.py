import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import medspacy



def regular_exp():
	#The following commands expect 'note_text' as the column for the clinical notes
	AP0= df.loc[df['note_text'].str.contains("ASSESSMENT", case=True,na=False)]
	AP1= df.loc[df['note_text'].str.contains("IMPRESSION", case=True,na=False)]
	AP2= df.loc[df['note_text'].str.contains("RECOMMENDATIONS", case=True,na=False)]
	AP3= df.loc[df['note_text'].str.contains("A & P", case=True,na=False)]
	AP4= df.loc[df['note_text'].str.contains("A / P", case=True,na=False)]
	AP5= df.loc[df['note_text'].str.contains("A AND P", case=True,na=False)]


	AP0['AP'] = AP0['note_text'].str.split('ASSESSMENT',2)
	AP1['AP'] = AP1['note_text'].str.split('IMPRESSION',2)
	AP2['AP'] = AP2['note_text'].str.split('RECOMMENDATIONS',2)
	AP3['AP'] = AP3['note_text'].str.split('A & P',2)
	AP4['AP'] = AP4['note_text'].str.split('A / P',2)
	AP5['AP'] = AP5['note_text'].str.split('A AND P',2)

	from functools import reduce
	data_list = [AP0,AP1,AP2,AP3,AP4,AP5]
	dfs = pd.concat(data_list)
	dfs.drop_duplicates(subset='deid_note_key', inplace=True)
	APS=dfs
	APS['AP2']=APS['AP'].str[1]


def medspacy_sectioning():
	nlp = medspacy.load()
	nlp.pipe_names
	#['medspacy_pyrush', 'medspacy_target_matcher', 'medspacy_context']
	sectionizer = nlp.add_pipe("medspacy_sectionizer")
	nlp.pipe_names
		#['medspacy_pyrush','medspacy_target_matcher','medspacy_context','medspacy_sectionizer']
	# Add some target rules for extracting entities
	from medspacy.target_matcher import TargetRule

	rules = [
    TargetRule("ASSESSMENT", "SECTION"),
    TargetRule("IMPRESSION", "SECTION"),
    TargetRule("RECOMMENDATIONS", "SECTION"),
    TargetRule("A & P", "SECTION"),
	TargetRule("A AND P", "SECTION"),
    TargetRule("A / P", "SECTION")]
	nlp.get_pipe("medspacy_target_matcher").add(rules) 
	text=APS.note_text.iloc[3]
	doc = nlp(text)
	doc._.section_categories
		[None,'history_of_present_illness','allergies','allergies','social_history','patient_education','family_history','physical_exam','assessment and plan''labs_and_studies']
	doc._.section_titles
	ls=["ASSESSMENT","IMPRESSION","RECOMMENDATIONS","A & P","A AND P","A/P"]
	sections = doc._.section_spans
	for i in sections:
		if sections[i].isin(ls)
			APS['AP']=sections[i]
 
	APS = APS[APS['AP2'].notna()]
	APS = APS.loc[:,~APS.columns.duplicated()].copy()

df=pd.read_csv('File_Path')
regular_exp()
medspacy_sectioning()
ls='Physician','Resident','Scribe','Medical Student'
APS=APS.loc[APS['auth_prov_type'].isin(ls)]
#NASH
APS=APS.loc[~APS['AP2'].str.contains("without NASH",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("NOT consistent with NASH",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("low suspicion for NASH",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("no evidence of NASH",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("lack of NASH risk factors",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("no NASH",case=False)]
APS=APS.loc[~APS['AP2'].str.contains("may be NASH",case=False)]
AP0 = APS.loc[APS['AP2'].str.contains("NASH", case='TRUE',na=False)]
AP1 = APS.loc[APS['AP2'].str.contains("Nonalcoholic steatohepatitis", case=False,na=False)]
AP2 = APS.loc[APS['AP2'].str.contains("Non-alcoholic steatohepatitis", case=False,na=False)]
AP3 = APS.loc[APS['AP2'].str.contains("non-alcoholic steatohepatitis", case=False,na=False)]
AP4 = APS.loc[APS['AP2'].str.contains("nonalcoholic steatohepatitis", case=False,na=False)]
data_list = [AP0,AP1,AP2,AP3,AP4]
NASH_notes = pd.concat(data_list)
NASH_notes.drop_duplicates(subset='deid_note_key', inplace=True)


