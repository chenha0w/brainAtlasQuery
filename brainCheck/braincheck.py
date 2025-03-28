from ._request import request_HPA, get_allen_expid
from lxml import etree
from .HPAcheck import HPA_consensus_check, HPA_humanbrain_check, HPA_mousebrain_check, HPA_pigbrain_check
from .ALLENcheck import allen_mousebrain_check
import pandas as pd

def test_1gene_allarea(gene,area_name):
    #----------------------------------------
    # request from HPA and allen
    #---------------------------------------
    # HPA
    response = request_HPA(gene)
    if response is None:           
        raise RuntimeError("Failed to request from HPA")
    else:
        root = etree.fromstring(response)
    # ALLEN
    exp_id=get_allen_expid(gene)
    if exp_id is None:
        raise RuntimeError("Failed to request from Allen")

    #----------------------------------------
    # check existence
    #----------------------------------------
    exam_gene={}
    for key,area in area_name.items():
        exam_dict={}
        if 'HPA' in area:
            exam_dict.update(HPA_consensus_check(root,area['HPA']))
            if 'human' in area['HPA']:
                exam_dict.update(HPA_humanbrain_check(root,area['HPA']['human']))
            if 'mouse' in area['HPA']:
                exam_dict.update(HPA_mousebrain_check(root,area['HPA']['mouse']))
            if 'pig' in area['HPA']:
                exam_dict.update(HPA_pigbrain_check(root,area['HPA']['pig']))
        if 'Allen' in area:
            if 'mouse' in area['Allen']:
                if not exp_id:
                    exam_dict.update({'allen_mousebrain':None})
                else:
                    exam_dict.update(allen_mousebrain_check(exp_id,area['Allen']['mouse']))
        exam_gene.update({key:exam_dict})
    return exam_gene

def braincheck(genes,area_name):
    # genes: list of gene
    test_gene={}
    for gene in genes:
        test_gene[gene]=test_1gene_allarea(gene,area_name)

    exam_df = pd.DataFrame(columns=['check','area'])
    for gene in test_gene:
        temp_df = pd.DataFrame(test_gene[gene]).reset_index().melt(id_vars=['index'], value_vars=list(area_name.keys())).rename(
            columns={'index':'check','variable':'area','value':gene})
        if exam_df.empty:
            exam_df = temp_df
        else:
            exam_df = exam_df.merge(temp_df,on=['check','area'],how='outer')
    return exam_df