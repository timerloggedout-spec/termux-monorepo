from pathlib import Path
import sys,unittest,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from doe_core import *
class Designs(unittest.TestCase):
    def config(self,name): return load_config(ROOT/'examples'/f'{name}.json')
    def test_factorial(self):
        c=self.config('factorial'); a=audit(coded_design(c),c)
        self.assertEqual((a['n_runs'],a['rank'],a['pure_error_df']),(19,7,10)); self.assertTrue(a['release_ready'])
    def test_fraction(self):
        c=self.config('fractional'); a=audit(coded_design(c),c)
        self.assertEqual(a['defining_relation']['resolution'],4); self.assertEqual(a['rank'],5)
    def test_fraction_interactions_fail(self):
        c=self.config('fractional'); c['model']='two-factor'; a=audit(coded_design(c),c)
        self.assertFalse(a['release_ready']); self.assertLess(a['rank'],len(a['terms']))
    def test_quadratic_factorial_fails(self):
        c=self.config('factorial'); c['model']='quadratic'; self.assertFalse(audit(coded_design(c),c)['release_ready'])
    def test_ccd(self):
        c=self.config('ccd'); a=audit(coded_design(c),c)
        self.assertEqual((a['n_runs'],a['rank']),(19,10)); self.assertTrue(a['release_ready'])
    def test_box_behnken(self):
        c=self.config('box-behnken'); a=audit(coded_design(c),c)
        self.assertEqual((a['n_runs'],a['rank']),(17,10)); self.assertTrue(a['release_ready'])
    def test_reproducibility(self):
        c=self.config('ccd'); self.assertTrue(coded_design(c).equals(coded_design(c)))
        d=copy.deepcopy(c); d['seed']+=1; self.assertFalse(coded_design(c).equals(coded_design(d)))
    def test_natural_corruption(self):
        c=self.config('ccd'); df=coded_design(c); df.loc[0,'A']+=1
        with self.assertRaises(ValueError): audit(df,c)
    def test_wrong_counts(self):
        c=self.config('ccd'); df=coded_design(c).iloc[:-1].copy()
        with self.assertRaises(ValueError): audit(df,c)
    def test_bad_generator(self):
        c=self.config('fractional'); c['generators']={'D':'A*A'}
        with self.assertRaises(ValueError): validate_config(c)
    def test_invalid_ranges(self):
        c=self.config('ccd'); c['factors'][0]['high']=0
        with self.assertRaises(ValueError): validate_config(c)
    def test_audit_schema(self):
        c=self.config('ccd'); validate(audit(coded_design(c),c),json.loads((ROOT/'schemas/audit.schema.json').read_text()))
    def test_signed_fraction(self):
        c=self.config('fractional'); c['generators']['D']='-A*B*C'; df=coded_design(c)
        corners=df[df.point_type!='center']; self.assertTrue(np.all(np.prod(corners[['x_A','x_B','x_C','x_D']],axis=1)==-1))
        self.assertEqual(defining_relation(c)['signed_words'],['-A*B*C*D'])
    def test_saturated_design(self):
        c=self.config('factorial'); c['factors']=c['factors'][:2]; c['replicates']=1;c['center_points']=0
        a=audit(coded_design(c),c);self.assertEqual(a['residual_df'],0);self.assertFalse(a['release_ready'])
if __name__=='__main__': unittest.main()
