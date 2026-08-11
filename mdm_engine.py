# mdm_engine.py
import pandas as pd
from thefuzz import fuzz

class DataForgeEngine:
    def __init__(self, df: pd.DataFrame):
        self.raw_df = df
        self.cleaned_df = df.copy()
        self.quarantine_df = pd.DataFrame()
        self.audit_summary = {}

    def run_profiling(self) -> dict:
        """Evaluates completeness, row count, and missing value metrics."""
        total_rows = len(self.raw_df)
        null_counts = self.raw_df.isnull().sum().to_dict()
        exact_duplicates = self.raw_df.duplicated().sum()
        
        total_cells = total_rows * len(self.raw_df.columns)
        total_nulls = self.raw_df.isnull().sum().sum()
        completeness = round((1 - (total_nulls / total_cells)) * 100, 2) if total_cells > 0 else 0.0
        
        self.audit_summary['total_records'] = total_rows
        self.audit_summary['exact_duplicates'] = exact_duplicates
        self.audit_summary['completeness_score'] = completeness
        self.audit_summary['null_metrics'] = null_counts
        return self.audit_summary

    def enforce_data_rules(self) -> None:
        """Isolates non-compliant or incomplete records into a quarantine table."""
        # A record is non-compliant if it is missing Vendor_Name, Tax_ID, OR Contact_Email,
        # or if the email is flagged as invalid.
        has_missing_name = self.raw_df['Vendor_Name'].isnull()
        has_missing_tax = self.raw_df['Tax_ID'].isnull()
        has_missing_email = self.raw_df['Contact_Email'].isnull()
        has_invalid_email = self.raw_df['Contact_Email'] == "invalid_email_format"

        # Combine rules into a single quarantine condition
        quarantine_condition = has_missing_name | has_missing_tax | has_missing_email | has_invalid_email

        self.cleaned_df = self.raw_df[~quarantine_condition].copy()
        self.quarantine_df = self.raw_df[quarantine_condition].copy()
        self.audit_summary['quarantined_records'] = len(self.quarantine_df)

    def generate_golden_records(self, match_column: str, threshold: int = 80) -> pd.DataFrame:
        """Consolidates duplicate text variations into single Master Golden Records using fuzzy matching."""
        unique_entities = []
        visited_indices = set()
        df_to_match = self.cleaned_df.reset_index(drop=True)

        for i, row in df_to_match.iterrows():
            if i in visited_indices:
                continue
            
            current_val = str(row[match_column])
            cluster = [i]
            visited_indices.add(i)

            for j in range(i + 1, len(df_to_match)):
                if j in visited_indices:
                    continue
                target_val = str(df_to_match.loc[j, match_column])
                score = fuzz.token_sort_ratio(current_val, target_val)

                if score >= threshold:
                    cluster.append(j)
                    visited_indices.add(j)

            master_record = df_to_match.loc[cluster[0]].to_dict()
            master_record['Golden_Cluster_Size'] = len(cluster)
            master_record['Merged_Variations'] = ", ".join([str(df_to_match.loc[idx, match_column]) for idx in cluster])
            unique_entities.append(master_record)

        golden_df = pd.DataFrame(unique_entities)
        self.audit_summary['golden_records_count'] = len(golden_df)
        self.audit_summary['merged_duplicates'] = len(df_to_match) - len(golden_df)
        return golden_df