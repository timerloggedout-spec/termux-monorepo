# 1. Heal synthegration_index.py – remove the broken @staticmethod
sed -i 's/    @staticmethod\n    def __init__/    def __init__/' ~/cli-synthegration/synthegration_index.py