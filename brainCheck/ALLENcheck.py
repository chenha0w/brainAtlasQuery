import pandas as pd
import json
from ._request import get_allen_expdf
import os

### define global constant:
file_path = os.path.join(os.path.dirname(__file__),"..","data","brain_structure.json")
with open(file_path,'r') as handle:
    ALLEN_MOUSE_BRAIN_STR = json.load(handle)


###----------helper function to get all the child region names---------###

def find_subtree(structure,area):
    if structure["acronym"]==area:
        return structure
    for child in structure.get("children",[]):
        result = find_subtree(child, area)
        if result:
            return result
    return None

def get_acronym(structure):
    acronyms = [structure["acronym"]]
    for child in structure.get("children",[]):
        acronyms.extend(get_acronym(child))
    return acronyms

def get_all_acronym(area):
    #area: a list of acronym
    regions=[]
    for region in area:
        regions.extend(get_acronym(find_subtree(ALLEN_MOUSE_BRAIN_STR,region)))
    return list(set(regions))

###------------check expression in regions in Allen mouse atlas-----------------###

def allen_mousebrain_check(exp_id,area):
    #exp_id:list of exp_id
    #area: list of list of acronyms, prioritize the list in the beginning. 
    #      Proceeding to the next list only when the area in the previous list were not found in any experiments.
    #      For the 1st list, also check all the subregion below it.
    isbreak=False
    allen=None
    for n,region in enumerate(area):
        if n==0:
            region=get_all_acronym(region)
        for ind in exp_id:
            expdf = pd.DataFrame(get_allen_expdf(ind))
            if expdf.empty:
                continue
            if not expdf[expdf.region.isin(region)].empty:
                isbreak=True
                if (expdf.loc[expdf.region.isin(region),'expression']>=1).any():
                    allen=True
                    break
                else:
                    allen=False
        if isbreak:
            break
    else:
        allen=None
    return {'allen_mousebrain':allen}