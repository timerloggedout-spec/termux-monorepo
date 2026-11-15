"""Continuous-factor DOE generation and fixed-model design audits."""
from pathlib import Path
import itertools, json, re
import numpy as np
import pandas as pd
from jsonschema import validate
ROOT = Path(__file__).resolve().parents[1]

def load_config(path):
    c=json.loads(Path(path).read_text()); validate_config(c); return c

def validate_config(c):
    validate(c,json.loads((ROOT/'schemas/design-config.schema.json').read_text()))
    names=[f['name'] for f in c['factors']]
    reserved={'run_id','std_order','replicate','point_type'}
    if len(set(names))!=len(names) or any(n in reserved or n.startswith('x_') for n in names):
        raise ValueError('Factor names must be unique and not reserved')
    for f in c['factors']:
        if not np.isfinite([f['low'],f['high']]).all() or f['low']>=f['high']:
            raise ValueError('Factor ranges must be finite and increasing')
    if c['design']=='fractional-factorial':
        if not c.get('generators'): raise ValueError('Fractional design requires generators')
        generator_masks(c)
    elif c.get('generators'): raise ValueError('Generators only apply to fractional factorials')
    if c['design']=='face-centered-ccd' and len(names)<2: raise ValueError('CCD needs >=2 factors')
    if c['design']=='box-behnken' and len(names)<3: raise ValueError('Box-Behnken needs >=3 factors')

def generator_masks(c):
    names=[f['name'] for f in c['factors']]; gens=c['generators']
    if not set(gens)<=set(names): raise ValueError('Unknown generated factor')
    basic=[n for n in names if n not in gens]
    if not basic: raise ValueError('Need at least one basic factor')
    result=[]
    for target,expr in gens.items():
        sign=-1 if expr.startswith('-') else 1
        tokens=expr.lstrip('-').split('*')
        if not all(t in basic for t in tokens) or len(tokens)!=len(set(tokens)):
            raise ValueError('Generator products must use distinct basic-factor names only')
        mask=(1<<names.index(target))
        for t in tokens: mask^=1<<names.index(t)
        result.append((target,tokens,mask,sign))
    return basic,result

def defining_relation(c):
    if c['design']!='fractional-factorial': return None
    names=[f['name'] for f in c['factors']]; _,gens=generator_masks(c)
    words={0:1}
    for _,_,mask,sign in gens:
        words.update({m^mask:s*sign for m,s in list(words.items())})
    terms=[]; lengths=[]
    for mask,sign in sorted(words.items()):
        if mask:
            labels=[n for i,n in enumerate(names) if mask&(1<<i)]
            lengths.append(len(labels)); terms.append(('+' if sign==1 else '-')+'*'.join(labels))
    return {'identity':'I','signed_words':terms,'resolution':min(lengths)}

def coded_design(c):
    validate_config(c); k=len(c['factors']); names=[f['name'] for f in c['factors']]
    kind=c['design']; points=[]; labels=[]
    if kind in ('full-factorial','face-centered-ccd'):
        points=list(itertools.product([-1.,1.],repeat=k)); labels=['factorial']*len(points)
        if kind=='face-centered-ccd':
            for j in range(k):
                for s in (-1.,1.):
                    p=[0.]*k; p[j]=s; points.append(tuple(p)); labels.append('axial')
    elif kind=='fractional-factorial':
        basic,gens=generator_masks(c)
        for vals in itertools.product([-1.,1.],repeat=len(basic)):
            d=dict(zip(basic,vals))
            for target,tokens,_,sign in gens: d[target]=sign*np.prod([d[t] for t in tokens])
            points.append(tuple(d[n] for n in names)); labels.append('fractional')
    else:
        for i,j in itertools.combinations(range(k),2):
            for a,b in itertools.product([-1.,1.],repeat=2):
                p=[0.]*k; p[i]=a; p[j]=b; points.append(tuple(p)); labels.append('edge-pair')
    reps=c.get('replicates',1); centers=c.get('center_points',0)
    if len(points)*reps+centers>100000: raise ValueError('Run count exceeds 100000 limit')
    rows=[]
    for rep in range(1,reps+1):
        rows.extend([(*p,rep,label) for p,label in zip(points,labels)])
    rows.extend([(*(0.,)*k,0,'center') for _ in range(centers)])
    df=pd.DataFrame(rows,columns=['x_'+n for n in names]+['replicate','point_type'])
    df.insert(0,'std_order',np.arange(1,len(df)+1))
    for f in c['factors']:
        df[f['name']]=(f['low']+f['high'])/2+df['x_'+f['name']]*(f['high']-f['low'])/2
    df=df.iloc[np.random.default_rng(c['seed']).permutation(len(df))].reset_index(drop=True)
    df.insert(0,'run_id',np.arange(1,len(df)+1)); return df

def model_matrix(df,c):
    names=[f['name'] for f in c['factors']]; x=df[['x_'+n for n in names]].to_numpy(float)
    cols=[np.ones(len(df))]; terms=['Intercept']
    for i,n in enumerate(names): cols.append(x[:,i]); terms.append(n)
    if c['model'] in ('two-factor','quadratic'):
        for i,j in itertools.combinations(range(len(names)),2):
            cols.append(x[:,i]*x[:,j]); terms.append(names[i]+':'+names[j])
    if c['model']=='quadratic':
        for i,n in enumerate(names): cols.append(x[:,i]**2); terms.append(n+'^2')
    return np.column_stack(cols),terms

def audit(df,c,check_schedule=True):
    validate_config(c); names=[f['name'] for f in c['factors']]; coded=['x_'+n for n in names]
    required=['run_id','std_order','replicate','point_type']+coded+names
    if not set(required)<=set(df.columns): raise ValueError('Missing required run-sheet columns')
    if len(df)==0: raise ValueError('Empty run sheet')
    if not np.isfinite(df[coded+names].to_numpy(float)).all(): raise ValueError('Nonfinite data')
    if list(df['run_id'])!=list(range(1,len(df)+1)): raise ValueError('run_id must be sequential in row order')
    if sorted(df['std_order'])!=list(range(1,len(df)+1)): raise ValueError('std_order must be a permutation')
    for f in c['factors']:
        z=df['x_'+f['name']].to_numpy(float)
        expected=(f['low']+f['high'])/2+z*(f['high']-f['low'])/2
        if np.any(np.abs(z)>1+1e-10): raise ValueError('Coded setting outside supported design bounds')
        if not np.allclose(df[f['name']],expected,rtol=1e-10,atol=1e-10): raise ValueError('Natural/coded mismatch')
    if check_schedule:
        expected=coded_design(c)
        def counts(d):
            return d.groupby(coded,dropna=False).size().sort_index()
        if not counts(df).equals(counts(expected)): raise ValueError('Treatment multiplicities do not match config')
        a=df.sort_values('std_order').reset_index(drop=True)
        b=expected.sort_values('std_order').reset_index(drop=True)
        if not a[['replicate','point_type']].equals(b[['replicate','point_type']]):
            raise ValueError('Point type or replicate metadata mismatch')
    X,terms=model_matrix(df,c); rank=int(np.linalg.matrix_rank(X)); n,p=X.shape
    u=int(len(np.unique(df[coded].to_numpy(float),axis=0)))
    norms=np.linalg.norm(X,axis=0); Z=X/np.where(norms==0,1,norms)
    condition=float(np.linalg.cond(Z)) if rank==p else None
    pairs=[]; dots=Z.T@Z
    for i,j in itertools.combinations(range(p),2):
        if abs(dots[i,j])>.95: pairs.append({'term1':terms[i],'term2':terms[j],'normalized_dot':float(dots[i,j]),'exact_proportional':bool(np.isclose(abs(dots[i,j]),1,atol=1e-10,rtol=0))})
    warnings=[]
    if rank<p: warnings.append('Requested model is rank deficient; coefficients are not all identifiable.')
    if n-rank<=0: warnings.append('No residual error degrees of freedom.')
    if n-u<=0: warnings.append('No independent-error replication is established by repeated settings; none are present.')
    if condition is not None and condition>1e8: warnings.append('Severely ill-conditioned scaled model matrix.')
    warnings.append('Pure-error interpretation requires genuinely independent experimental units.')
    return {'n_runs':n,'terms':terms,'rank':rank,'residual_df':n-rank,'pure_error_df':n-u,'lack_of_fit_df':u-rank,'condition_number_scaled':condition,'column_pairs':pairs,'defining_relation':defining_relation(c),'warnings':warnings,'release_ready':bool(rank==p and n-rank>0 and (condition is not None and condition<1e8))}
