# Find every place where model_type is set or used in the API calls
grep -n 'model_type\|expert\|instant\|model.*=' ~/deepcli/deepcli/core.py | head -20