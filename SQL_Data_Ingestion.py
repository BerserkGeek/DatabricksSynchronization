
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import json
import pandas as pd
import random
import time

class SQLDBService:

    def __init__(self) -> None:
        
        self.table_name = "ICMPSS.S_TLM_DAT"
        self.connection_url = URL.create(
        )
        self.dtype_map = {
            "nvarchar": "string",
            "numeric": "float64",
            "datetimeoffset": "datetime64[ns, UTC]",
            "date": "datetime64[ns]",
            "bigint": "int64"
        }
        self.engine = None

    def _get_engine(self):
        if self.engine is None:
            self.engine = create_engine(
                self.connection_url,
                pool_size=5,
                max_overflow=2,
            )
        return self.engine
    
    def _ingest_data(self, df: pd.DataFrame) -> bool:
        try:
            
            df.to_sql(
                self.table_name,
                con=self._get_engine(),
                if_exists="append",
                index=False,
            )
            return True
        except Exception as e:
            print(f"Data ingestion failed: {e}")
            return False
    
    def get_schema(self) -> dict:
        return {
            "TET_COD": "nvarchar",
            "STE_COD": "nvarchar",
            "SCE_SYS_COD": "nvarchar",
            "LGG_COD": "nvarchar",
            "OBJ_COD": "nvarchar",
            "CXT_NAM": "nvarchar",
            "VRB_NAM": "nvarchar",
            "QLY_OF_VAL": "numeric",
            "VRB_UOM_COD": "nvarchar",
            "VRB_NUM_VAL": "numeric",
            "VRB_ALP_VAL": "nvarchar",
            "TLM_DAT_TMS": "datetimeoffset",
            "VRB_COD": "nvarchar", 
            "CFG_SHT_TXT_ATR_1": "nvarchar",
            "CFG_SHT_TXT_ATR_2": "nvarchar",
            "CFG_LNG_TXT_ATR_1": "nvarchar",
            "CFG_LNG_TXT_ATR_2": "nvarchar",
            "CFG_DTE_ATR_1": "date",
            "CFG_DTE_ATR_2": "date",
            "ITG_ID": "bigint",
            "CRT_TMS": "datetimeoffset"
        }
    
    def get_random_value(self) -> float:
        return random.uniform(5.00, 100.00)
    
    def record_transformer(self, df: pd.DataFrame) -> pd.DataFrame:

        schema = self.get_schema()

        for col, sql_type in schema.items():

            if col not in df.columns:
                df[col] = None

            pandas_type = self.dtype_map.get(sql_type)
            if pandas_type:
                try:
                    # Skip conversion for datetime columns that are already correct
                    if pandas_type.startswith("datetime") and pd.api.types.is_datetime64_any_dtype(df[col]):
                        continue
                    df[col] = df[col].astype(pandas_type)
                except Exception as e:
                    print(f"Warning: Could not convert {col} to {pandas_type}: {e}")
        
        return df
            
    
    def data_processor(self, constant: dict, variable: list) -> pd.DataFrame:

        records: list = []

        utc_timestamp = pd.Timestamp.now(tz="UTC")
        utc_timestamp_updated = utc_timestamp + pd.Timedelta(minutes=2)

        for var in variable:

            record = {
                "TET_COD": "abb",
                "STE_COD": "STE001",
                "SCE_SYS_COD": "AIPM",
                "LGG_COD": "EN",
                "OBJ_COD": None,
                "CXT_NAM": None,
                "VRB_NAM": var,
                "QLY_OF_VAL": 1,
                "VRB_UOM_COD": None,
                "VRB_NUM_VAL": self.get_random_value(),
                "VRB_ALP_VAL": None,
                "TLM_DAT_TMS": utc_timestamp_updated,
                "VRB_COD": var,
                "CFG_SHT_TXT_ATR_1": None,
                "CFG_SHT_TXT_ATR_2": None,
                "CFG_LNG_TXT_ATR_1": None,
                "CFG_LNG_TXT_ATR_2": None,
                "CFG_DTE_ATR_1": None,
                "CFG_DTE_ATR_2": None,
                "ITG_ID": int(utc_timestamp_updated.timestamp() * 1000),
                "CRT_TMS": utc_timestamp
            }
            records.append(record)

        for key, value in constant.items():
            record = {
                "TET_COD": "abb",
                "STE_COD": "STE001",
                "SCE_SYS_COD": "AIPM",
                "LGG_COD": "EN",
                "OBJ_COD": None,
                "CXT_NAM": None,
                "VRB_NAM": key,
                "QLY_OF_VAL": 1,
                "VRB_UOM_COD": None,
                "VRB_NUM_VAL": value,
                "VRB_ALP_VAL": None,
                "TLM_DAT_TMS": utc_timestamp_updated,
                "VRB_COD": key,
                "CFG_SHT_TXT_ATR_1": None,
                "CFG_SHT_TXT_ATR_2": None,
                "CFG_LNG_TXT_ATR_1": None,
                "CFG_LNG_TXT_ATR_2": None,
                "CFG_DTE_ATR_1": None,
                "CFG_DTE_ATR_2": None,
                "ITG_ID": int(utc_timestamp_updated.timestamp() * 1000),
                "CRT_TMS": utc_timestamp
            }
            records.append(record)

        df = pd.DataFrame(records)

        return self.record_transformer(df)
    
    def _run_scheduler(self, json_file: str = "sql_data.json", interval: int = 60) -> None:
        
        print(f"Starting continuous ingestion from {json_file} (every {interval} seconds)...")
        print("Press Ctrl+C to stop.\n")
        
        run_count = 0
        
        try:
            while True:
                run_count += 1
                timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] Run #{run_count}")
                
                try:
                    # Reload JSON each iteration to pick up changes
                    with open(json_file, "r") as file:
                        sql_data = json.load(file)
                    
                    constant = sql_data.get("constant", {})
                    variable = sql_data.get("variable", [])
                    
                    if not constant and not variable:
                        print("  Warning: No data found in JSON (empty constant and variable)")
                        time.sleep(interval)
                        continue
                    
                    df = self.data_processor(constant, variable)
                    
                    if df.empty:
                        print("  Warning: No records generated")
                        time.sleep(interval)
                        continue
                    
                    ingestion_status = self._ingest_data(df)
                    
                    if ingestion_status:
                        print(f"  ✓ Ingested {len(df)} records successfully")
                    else:
                        print("  ✗ Ingestion failed")
                
                except FileNotFoundError:
                    print(f"  ✗ Error: {json_file} not found")
                except json.JSONDecodeError as e:
                    print(f"  ✗ Error: Invalid JSON format - {e}")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                
                print(f"  Next run in {interval} seconds...\n")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")
            print(f"Total runs completed: {run_count}")
            if self.engine:
                self.engine.dispose()
                print("Database connections closed.")

if __name__ == "__main__":
    service = SQLDBService()
    service._run_scheduler(json_file="sql_data.json", interval=55)


    