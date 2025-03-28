import requests
import diskcache as dc
import time
from functools import wraps

### Define global constant:
#HPA URL:
URL_HPA1 = "https://www.proteinatlas.org/api/search_download.php"
URL_HPA2 = "https://www.proteinatlas.org/search/"
URL_ALLEN_MOUSE="http://api.brain-map.org/api/v2/data/SectionDataSet/query.json"


###------define decorator for cache request-----------###

def select_cache(cache_dir="../.cache", size_limit=1e9):
    cache = dc.Cache(cache_dir, size_limit=int(size_limit))

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, frozenset(kwargs.items()))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            if result is not None:
                cache[key] = result
            return result
        return wrapper

    return decorator

###----------request from HPA-------------------------###

@select_cache()
def request_HPA(gene):
    # request gene_id
    params1={"search":gene,"format":"json","columns":"eg","compress":"no"}    
    gene_id=None
    for n in range(5):
        if gene_id is not None:
            break
        response=requests.get(URL_HPA1,params=params1)
        if response.status_code==200:
            if response.json():
                gene_id = response.json()[0]['Ensembl']
            else:
                gene_id = gene
        else:
            time.sleep(2)
            
    # request data based on gene_id        
    content=None
    if gene_id:
        for n in range(5):
            if content is not None:
                break
            response=requests.get(URL_HPA2+gene_id,params={"format":"xml"})
            if response.status_code==200:
                content = response.content
            else:
                time.sleep(2)
    return content

###-----------------request from Allen------------------------------###

# Get experimental id based on gene name
@select_cache()
def get_allen_expid(gene):
    gene=gene.capitalize()    
    params={"criteria":f"products[id$eq1],genes[acronym$eq'{gene}']","include":"genes"}    
    exp_id=None
    for n in range(5):
        if exp_id is not None:
            break
        response = requests.get(URL_ALLEN_MOUSE, params=params)
        if response.status_code==200:
            exp_id=[]
            for exp in response.json()['msg']:
                if exp['failed']:
                    continue
                exp_id.append(exp['id'])
        else:
            time.sleep(2)
    return exp_id

# get data based on exp_id
@select_cache()
def get_allen_expdf(exp_id):    
    params={"id":str(exp_id),"include":"structure_unionizes(structure)"}
    data_list=None
    for n in range(5):
        if data_list is not None:
            break        
        response = requests.get(URL_ALLEN_MOUSE, params=params)
        if response.status_code==200:
            data_list=[]
            for x in response.json()['msg'][0]['structure_unionizes']:
                region=x['structure']['acronym']
                name = x['structure']['name']
                expval = x['expression_energy']
                data_list.append({'region':region,'name':name,'expression':expval})
        else:
            time.sleep(2)
    return data_list