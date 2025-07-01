import yaml
import pandas as pd
import re

class StockSelector:
    def __init__(self, config_file='config/selection_rules.yaml'):
        """Inicjalizacja selektora z plikiem konfiguracyjnym"""
        self.config_file = config_file
        self.rules = self.load_rules()
    
    def load_rules(self):
        """Wczytuje reguły selekcji z pliku YAML"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config.get('selection_rules', {})
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono pliku {self.config_file}")
            return {}
        except yaml.YAMLError as e:
            print(f"Błąd w pliku YAML: {e}")
            return {}
    
    def apply_rule(self, df, rule_name, rule_config):
        """Stosuje pojedynczą regułę do DataFrame"""
        column = rule_config.get('column')
        operator = rule_config.get('operator')
        
        if column not in df.columns:
            print(f"Ostrzeżenie: Kolumna '{column}' nie istnieje w danych")
            return df
        
        if operator == 'in':
            values = rule_config.get('values', [])
            mask = df[column].isin(values)
        elif operator == '>=':
            value = rule_config.get('value')
            mask = df[column] >= value
        elif operator == 'complex':
            # Specjalna obsługa dla S&P Credit Rating
            if column == 'S&P Credit Rating':
                mask = self._apply_sp_rating_rule(df[column], rule_config)
            else:
                mask = pd.Series([True] * len(df))
        else:
            print(f"Nieznany operator: {operator}")
            mask = pd.Series([True] * len(df))
        
        return df[mask]
    
    def _apply_sp_rating_rule(self, column, rule_config):
        """Specjalna logika dla S&P Credit Rating"""
        allowed_patterns = rule_config.get('allowed_patterns', [])
        excluded_values = rule_config.get('excluded_values', [])
        
        mask = pd.Series([False] * len(column))
        
        for idx, value in enumerate(column):
            if pd.isna(value):
                continue
                
            value_str = str(value).strip()
            
            # Sprawdź czy wartość jest w wykluczonych
            if value_str in excluded_values:
                continue
            
            # Sprawdź wzorce A* i BBB+, BBB
            is_allowed = False
            for pattern in allowed_patterns:
                if pattern == "A*" and value_str.startswith('A'):
                    is_allowed = True
                    break
                elif pattern in ["BBB+", "BBB"] and value_str == pattern:
                    is_allowed = True
                    break
            
            mask.iloc[idx] = is_allowed
        
        return mask
    
    def select_stocks(self, df):
        """Stosuje wszystkie reguły selekcji do DataFrame"""
        print("Rozpoczynam selekcję spółek...")
        print(f"Początkowa liczba spółek: {len(df)}")
        
        filtered_df = df.copy()
        
        for rule_name, rule_config in self.rules.items():
            print(f"\nStosuję regułę: {rule_name}")
            print(f"  Kolumna: {rule_config.get('column')}")
            print(f"  Operator: {rule_config.get('operator')}")
            
            filtered_df = self.apply_rule(filtered_df, rule_name, rule_config)
            print(f"  Spółek po tej regule: {len(filtered_df)}")
        
        print(f"\nSelekcja zakończona. Końcowa liczba spółek: {len(filtered_df)}")
        return filtered_df
    
    def get_selection_summary(self, original_df, filtered_df):
        """Zwraca podsumowanie selekcji"""
        summary = {
            'original_count': len(original_df),
            'filtered_count': len(filtered_df),
            'removed_count': len(original_df) - len(filtered_df),
            'selection_rate': round(len(filtered_df) / len(original_df) * 100, 2)
        }
        return summary 