# brainAtlasQuery

## :pushpin: Description
This tool query and parse the human, mouse, pig brain RNA expression data from the Human Protein Atlas (HPA), and the mouse brain data from the Allen Mouse Atlas. It uses the parsed data to determine whether a gene is expressed in certain brain region.

## :rocket: Installtaion 
1. clone my repo
```bash
git clone https://github.com/chenha0w/brainAtlasQuery.git
```
2. Add the repo directory to sys.path in the python scripts or notebook
```python
import sys
sys.path.append(path to cloned repo)
``` 
3. import and use
```python
from brainCheck.braincheck import braincheck
```

## :fire: Usage
```python
from brainCheck.braincheck import braincheck
exam_df = braincheck(genes, area_name)
```
`genes` is a list of gene symbols.  
`area_name` is a dictionary of all the brain areas you want to exam for gene expression. Since different atlas uses a slightly different naming for brain structures. You will need to find out the naming for the atlas you want to check.  
Below are some examples for some brain area:  
1. Lateral hypothalamus area (LHA)
```python
area_name['LHA'] = {'HPA':{'human':['HY','Hypothalamus',['Lateral hypothalamic area']],
                       'mouse':['HY','Hypothalamus','all'],
                       'pig':['HY','Hypothalamus','all']},
                 'Allen':[['LHA'],['LZ']]}
```

For HPA, you need to specify the species. You can omit some species or atlas if you don't want to check them. For example, if only want to check in human brain, then you can do
```python
area_name['LHA'] = {'HPA':{'human':['HY','Hypothalamus',['Lateral hypothalamic area']]}}
```
For HPA, You put the short ('HY') and name ('Hypothalamus') for the main brain region in the front and put the sub region names in the last as a list. If you don't care about sub regions, you can put 'all' at the end.  
For Allen, you put the area you want to exam in the first list. The later one has less priority. For example, `[['LHA'],['LZ']]` means the tool will check 'LHA' first. It only checks 'LZ' when the entry of 'LHA' is missing. If you want to be strict, you can only do `'Allen':[['LHA']]` instead.

2. Amygdala
```python
area_name['AMY']={'HPA':{'human':['AMY','Amygdala','all'],
                         'mouse':['AMY','Amygdala','all'],
                         'pig':['AMY','Amygdala','all']},
                  'Allen':[['COA','LA','BLA','BMA','PA','sAMY']]}
```

3. medial pre-frontal cortex
```python
area_name['MPF']={'HPA':{'human':['CTX','Cerebral cortex',['Anterior cingulate cortex, supragenual-dorsal',
                                                           'Anterior cingulate cortex, supragenual-ventral',
                                                          'Orbitofrontal gyrus, anterior']],
                         'mouse':['CTX','Cerebral cortex',['Frontal cortex']],
                         'pig':['CTX','Cerebral cortex',['Prefrontal cortex']]},
                  'Allen':[['FRP','ACA','PL','ILA','ORB'],['Isocortex']]} 
```

## :hourglass_flowing_sand: In Progress
1. deploy the package
2. built a class for area name, making it easier to initiate
3. add Allen human data atlas
