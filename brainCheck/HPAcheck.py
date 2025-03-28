import pandas as pd

###---------obtain RNA expression data based on assaytype-------------###

def get_RNAexp_HPA(root,assaytype,attr='organ',filter_brain=False):
    entry = root.find('entry')
    if entry is None:
        return entry
    rna = entry.xpath(f".//rnaExpression[@assayType='{assaytype}']")
    if not rna:
        return None
    data_list=[]
    for data in rna[0].findall('data'):
        tissue = data.find('tissue')
        level = data.find("level[@type='normalizedRNAExpression']")
        if tissue is not None and level is not None:
            tissue_organ = tissue.get(attr,'Unknown')
            sub_region = tissue.text.strip() if tissue.text else 'Unknown'
            nTPM = level.get('expRNA','N/A')
            if filter_brain and "Brain" not in tissue_organ:
                continue
            data_list.append({'region':tissue_organ,'sub_region':sub_region,'nTPM':float(nTPM)})
    return data_list

###--------check existence at brain level and large brain structure level------------------###

def HPA_consensus_check(root,area):
    # test for brian enrichment
    entry = root.find('entry')
    if entry is None:
        return {'brain_enrich':None,'inBrain_HPA':None,'consensus_HPA':None}
        
    for tissue in entry.xpath(".//rnaExpression[@assayType='consensusTissue']/rnaSpecificity/tissue"):
        if tissue.get('organ').lower()=='brain':
            brain_enrich=True
            break
    else:
        brain_enrich=False

    # test whether it's in brain
    consensus = pd.DataFrame(get_RNAexp_HPA(root,'consensusTissue',filter_brain=True))
    if consensus.nTPM.max()>=5:
        inBrain=True
    else:
        inBrain=False

    # test region in brain
    for key in area:
        if not consensus[consensus.sub_region.str.contains(area[key][1],case=False)].empty:
            if (consensus.loc[consensus.sub_region.str.contains(area[key][1],case=False),'nTPM']>=5).any():
                inRegion=True
            else:
                inRegion=False
            break
    else:
        inRegion=None

    return {'brain_enrich':brain_enrich,'inBrain_HPA':inBrain,'consensus_HPA':inRegion}

###------check expression at sub_region level in brain based on given dataset---------###

def HPA_brain_check(exp_df,area):
    if exp_df.empty:
        return None

    # if the last element of area is a list with area names, for example ['HY', 'Hypothalamus', ['Lateral hypothalamic area']]
    if isinstance(area[-1],list) and  area[-1][0]!='':
        combined = '|'.join(area[-1])
        # if found, decide True or False; if not fount, check higher category
        if not exp_df[(exp_df.region==area[0]) & (exp_df.sub_region.str.contains(combined,case=False))].empty:
            if (exp_df.loc[(exp_df.region==area[0]) & (exp_df.sub_region.str.contains(combined,case=False)),'nTPM']>=5).any():
                HPA_brain=True
            else:
                HPA_brain=False
        else:
            if not exp_df[exp_df.region==area[0]].empty:
                if (exp_df.loc[exp_df.region==area[0],'nTPM']>=5).any():
                    HPA_brain=True
                else:
                    HPA_brain=False
            else:
                HPA_brain=None
                
    # The last element is all or [''], for example  ['HY', 'Hypothalamus', 'all']           
    elif area[-1]=='all' or area[-1][0]=='':
        if not exp_df[exp_df.region==area[0]].empty:
            if (exp_df.loc[exp_df.region==area[0],'nTPM']>=5).any():
                HPA_brain=True
            else:
                HPA_brain=False
        else:
            HPA_brain=None        
            
    else:
        raise TypeError("The format of input area for HPA is not correct. Please check the given samples")
        
    return HPA_brain

###------check expression at sub_region level for different species--------###

def HPA_humanbrain_check(root,area):
    # check for humanbrain subarea
    humanbrain = pd.DataFrame(get_RNAexp_HPA(root,'humanBrain'))
    return {'HPA_humanbrain':HPA_brain_check(humanbrain,area)}

def HPA_mousebrain_check(root,area):
    # check for mousebrain subarea
    mousebrain = pd.DataFrame(get_RNAexp_HPA(root,'mouseBrain',attr='region'))
    return {'HPA_mousebrain':HPA_brain_check(mousebrain,area)}

def HPA_pigbrain_check(root,area):
    # check for mousebrain subarea
    pigbrain = pd.DataFrame(get_RNAexp_HPA(root,'pigBrain',attr='region'))
    return {'HPA_pigbrain':HPA_brain_check(pigbrain,area)}