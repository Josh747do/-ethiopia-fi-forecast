"""
Data loading utilities for Ethiopia Financial Inclusion Forecasting System.
Updated to handle Excel files.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
from typing import Tuple, Dict, Optional, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Load and manage financial inclusion data from Excel files."""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize DataLoader with data directory.
        
        Parameters:
        -----------
        data_dir : str
            Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Data file names (Excel files)
        self.data_files = {
            "unified_data": "ethiopia_fi_unified_data.xlsx",
            "reference_codes": "reference_codes.xlsx",
            "additional_data": "Additional Data Points Guide.xlsx"
        }
        
        logger.info(f"DataLoader initialized with data directory: {data_dir}")
        logger.info(f"Looking for Excel files: {list(self.data_files.values())}")
    
    def check_data_files(self) -> Dict[str, bool]:
        """
        Check which data files exist locally.
        
        Returns:
        --------
        Dict[str, bool]
            Dictionary mapping file names to existence status
        """
        file_status = {}
        
        for name, filename in self.data_files.items():
            file_path = self.raw_dir / filename
            csv_path = self.raw_dir / filename.replace('.xlsx', '.csv')
            
            exists = file_path.exists() or csv_path.exists()
            file_status[name] = exists
            
            if exists:
                logger.info(f"✅ Data file found for {name}")
            else:
                logger.warning(f"❌ Data file not found for {name}")
        
        return file_status
    
    def download_data(self, force_download: bool = False) -> Dict[str, Path]:
        """
        Check for local data files.
        
        Parameters:
        -----------
        force_download : bool
            Not used for local files, kept for compatibility
            
        Returns:
        --------
        Dict[str, Path]
            Dictionary mapping dataset names to file paths
        """
        file_paths = {}
        
        for name, filename in self.data_files.items():
            # Try Excel file first
            excel_path = self.raw_dir / filename
            csv_path = self.raw_dir / filename.replace('.xlsx', '.csv')
            
            if excel_path.exists():
                logger.info(f"Found Excel file: {excel_path}")
                file_paths[name] = excel_path
            elif csv_path.exists():
                logger.info(f"Found CSV file: {csv_path}")
                file_paths[name] = csv_path
            else:
                logger.error(f"No data file found for: {name}")
                logger.error(f"Expected at: {excel_path} or {csv_path}")
        
        # Log summary
        if file_paths:
            logger.info(f"✅ Found {len(file_paths)} data file(s)")
            for name, path in file_paths.items():
                logger.info(f"   {name}: {path.name}")
        else:
            logger.error("❌ No data files found!")
            logger.error(f"Please place Excel files in: {self.raw_dir}")
        
        return file_paths
    
    def load_unified_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load the unified dataset from Excel and split into main data and impact links.
        
        Returns:
        --------
        Tuple[pd.DataFrame, pd.DataFrame]
            (main_data, impact_links)
        """
        try:
            # Get file paths
            file_paths = self.download_data()
            unified_data_path = file_paths.get("unified_data")
            
            if not unified_data_path:
                raise FileNotFoundError(
                    f"Unified data file not found. Expected: {self.data_files['unified_data']} "
                    f"in {self.raw_dir}"
                )
            
            # Load the file
            logger.info(f"Loading unified data from {unified_data_path}")
            
            # Check file type and load accordingly
            file_extension = unified_data_path.suffix.lower()
            
            if file_extension == '.xlsx':
                # Read Excel file
                excel_file = pd.ExcelFile(unified_data_path)
                sheet_names = excel_file.sheet_names
                logger.info(f"📂 Excel sheets available: {sheet_names}")
                
                # Try to find the right sheet
                df = None
                sheet_used = None
                
                # Common possible sheet names
                possible_sheet_names = [
                    'data', 'Sheet1', 'unified_data', 
                    'ethiopia_fi', 'main', 'observations'
                ]
                
                for sheet_name in possible_sheet_names:
                    if sheet_name in sheet_names:
                        df = pd.read_excel(unified_data_path, sheet_name=sheet_name)
                        sheet_used = sheet_name
                        logger.info(f"📊 Loaded from sheet: '{sheet_name}'")
                        break
                
                # If no common sheet found, try sheets with data
                if df is None:
                    for sheet_name in sheet_names:
                        try:
                            temp_df = pd.read_excel(unified_data_path, sheet_name=sheet_name, nrows=10)
                            # Check if this looks like our data (has record_type or similar)
                            if 'record_type' in temp_df.columns or 'indicator' in temp_df.columns:
                                df = pd.read_excel(unified_data_path, sheet_name=sheet_name)
                                sheet_used = sheet_name
                                logger.info(f"📊 Loaded from sheet (detected): '{sheet_name}'")
                                break
                        except:
                            continue
                
                # Last resort: use first sheet
                if df is None and sheet_names:
                    df = pd.read_excel(unified_data_path, sheet_name=sheet_names[0])
                    sheet_used = sheet_names[0]
                    logger.info(f"📊 Loaded from first sheet: '{sheet_used}'")
                    
            elif file_extension == '.csv':
                # Read CSV file
                df = pd.read_csv(unified_data_path)
                logger.info("📊 Loaded from CSV file")
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if df is None or df.empty:
                raise ValueError("Loaded dataframe is empty")
            
            logger.info(f"✅ Raw data loaded. Shape: {df.shape}")
            logger.info(f"📋 Columns: {df.columns.tolist()}")
            
            # Clean column names (strip whitespace, lowercase)
            df.columns = df.columns.str.strip().str.lower()
            logger.info(f"🔧 Cleaned columns: {df.columns.tolist()}")
            
            # Check for required columns
            required_columns = ['record_type']
            available_columns = df.columns.tolist()
            
            missing_columns = [col for col in required_columns if col not in available_columns]
            
            if missing_columns:
                logger.warning(f"⚠️  Missing expected columns: {missing_columns}")
                logger.info(f"📋 Available columns: {available_columns}")
                
                # Try to find similar columns
                for missing_col in missing_columns:
                    similar_cols = [col for col in available_columns if missing_col in col]
                    if similar_cols:
                        logger.info(f"   Similar to '{missing_col}': {similar_cols}")
            
            # Split into main data and impact links if 'record_type' exists
            if 'record_type' in df.columns:
                # Clean record_type values
                df['record_type'] = df['record_type'].astype(str).str.strip().str.lower()
                
                # Split data
                impact_links_mask = df['record_type'] == 'impact_link'
                main_data = df[~impact_links_mask].copy()
                impact_links = df[impact_links_mask].copy()
                
                logger.info(f"✅ Split data:")
                logger.info(f"   Main data records: {len(main_data)}")
                logger.info(f"   Impact link records: {len(impact_links)}")
                
                # Reset indices
                main_data = main_data.reset_index(drop=True)
                impact_links = impact_links.reset_index(drop=True)
                
            else:
                # If no record_type, assume all is main data
                logger.warning("⚠️  No 'record_type' column found. Assuming all data is main data.")
                main_data = df.copy()
                impact_links = pd.DataFrame()
            
            # Display sample of each type
            if not main_data.empty:
                logger.info(f"\n📄 MAIN DATA SAMPLE (first 3 rows):")
                print(main_data.head(3).to_string())
            
            if not impact_links.empty:
                logger.info(f"\n🔗 IMPACT LINKS SAMPLE (first 3 rows):")
                print(impact_links.head(3).to_string())
            
            return main_data, impact_links
            
        except Exception as e:
            logger.error(f"❌ Error loading unified data: {e}")
            logger.error("Please check:")
            logger.error("1. File exists in data/raw/ folder")
            logger.error("2. File is not open in Excel")
            logger.error("3. File format is correct")
            raise
    
    def load_reference_codes(self) -> pd.DataFrame:
        """
        Load reference codes from Excel file.
        
        Returns:
        --------
        pd.DataFrame
            Reference codes dataframe
        """
        try:
            file_paths = self.download_data()
            ref_codes_path = file_paths.get("reference_codes")
            
            if not ref_codes_path:
                raise FileNotFoundError(
                    f"Reference codes file not found. Expected: {self.data_files['reference_codes']} "
                    f"in {self.raw_dir}"
                )
            
            logger.info(f"Loading reference codes from {ref_codes_path}")
            
            # Load file based on extension
            file_extension = ref_codes_path.suffix.lower()
            
            if file_extension == '.xlsx':
                # Try to read Excel
                excel_file = pd.ExcelFile(ref_codes_path)
                sheet_names = excel_file.sheet_names
                logger.info(f"Excel sheets: {sheet_names}")
                
                # Try common sheet names
                possible_sheet_names = ['reference_codes', 'codes', 'Sheet1', 'ref']
                ref_codes = None
                
                for sheet_name in possible_sheet_names:
                    if sheet_name in sheet_names:
                        ref_codes = pd.read_excel(ref_codes_path, sheet_name=sheet_name)
                        logger.info(f"Loaded from sheet: '{sheet_name}'")
                        break
                
                # Use first sheet if none matched
                if ref_codes is None and sheet_names:
                    ref_codes = pd.read_excel(ref_codes_path, sheet_name=sheet_names[0])
                    logger.info(f"Loaded from first sheet: '{sheet_names[0]}'")
                    
            elif file_extension == '.csv':
                ref_codes = pd.read_csv(ref_codes_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if ref_codes is None or ref_codes.empty:
                raise ValueError("Loaded reference codes dataframe is empty")
            
            logger.info(f"✅ Reference codes loaded. Shape: {ref_codes.shape}")
            logger.info(f"📋 Columns: {ref_codes.columns.tolist()}")
            
            # Clean column names
            ref_codes.columns = ref_codes.columns.str.strip().str.lower()
            
            # Display sample
            logger.info(f"\n📄 REFERENCE CODES SAMPLE (first 5 rows):")
            print(ref_codes.head().to_string())
            
            return ref_codes
            
        except Exception as e:
            logger.error(f"❌ Error loading reference codes: {e}")
            raise
    
    def load_additional_data_guide(self) -> Dict[str, pd.DataFrame]:
        """
        Load the Additional Data Points Guide Excel file.
        This file contains multiple sheets with guidance for data enrichment.
        
        Returns:
        --------
        Dict[str, pd.DataFrame]
            Dictionary mapping sheet names to dataframes
        """
        try:
            file_paths = self.download_data()
            guide_path = file_paths.get("additional_data")
            
            if not guide_path:
                raise FileNotFoundError(
                    f"Additional data guide not found. Expected: {self.data_files['additional_data']} "
                    f"in {self.raw_dir}"
                )
            
            logger.info(f"Loading additional data guide from {guide_path}")
            
            # Check file type
            file_extension = guide_path.suffix.lower()
            
            if file_extension == '.xlsx':
                # Read all sheets
                excel_file = pd.ExcelFile(guide_path)
                sheet_names = excel_file.sheet_names
                
                logger.info(f"📂 Guide sheets available: {sheet_names}")
                
                # Load all sheets into dictionary
                sheets_dict = {}
                for sheet_name in sheet_names:
                    sheets_dict[sheet_name] = pd.read_excel(guide_path, sheet_name=sheet_name)
                    logger.info(f"   Loaded sheet: '{sheet_name}' - Shape: {sheets_dict[sheet_name].shape}")
                
                return sheets_dict
                
            else:
                raise ValueError(f"Unsupported file format for guide: {file_extension}")
            
        except Exception as e:
            logger.error(f"❌ Error loading additional data guide: {e}")
            return {}
    
    def validate_data_structure(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate the structure and completeness of the data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataframe to validate
            
        Returns:
        --------
        Dict[str, any]
            Validation results
        """
        validation_results = {
            "total_records": len(df),
            "record_type_counts": {},
            "pillar_distribution": {},
            "missing_values": {},
            "date_range": None,
            "unique_indicators": 0
        }
        
        if df.empty:
            logger.warning("⚠️  Dataframe is empty, skipping validation")
            return validation_results
        
        # Record type counts
        if 'record_type' in df.columns:
            validation_results["record_type_counts"] = df['record_type'].value_counts().to_dict()
        
        # Pillar distribution
        if 'pillar' in df.columns:
            validation_results["pillar_distribution"] = df['pillar'].value_counts().to_dict()
        
        # Missing values
        validation_results["missing_values"] = df.isnull().sum().to_dict()
        
        # Unique indicators
        if 'indicator_code' in df.columns:
            validation_results["unique_indicators"] = df['indicator_code'].nunique()
        
        # Date range if date column exists
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        if date_columns:
            for date_col in date_columns:
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    valid_dates = df[date_col].dropna()
                    if not valid_dates.empty:
                        validation_results["date_range"] = {
                            "min": valid_dates.min().strftime('%Y-%m-%d'),
                            "max": valid_dates.max().strftime('%Y-%m-%d')
                        }
                        break
                except:
                    continue
        
        return validation_results
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Save processed data to processed directory.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataframe to save
        filename : str
            Name of the file (without directory)
            
        Returns:
        --------
        Path
            Path to saved file
        """
        file_path = self.processed_dir / filename
        
        # Ensure filename ends with .csv
        if not filename.endswith('.csv'):
            filename += '.csv'
            file_path = self.processed_dir / filename
        
        df.to_csv(file_path, index=False)
        logger.info(f"💾 Saved processed data to {file_path}")
        return file_path

# Helper function to display data summary
def display_data_summary(main_data: pd.DataFrame, impact_links: pd.DataFrame) -> None:
    """
    Display a comprehensive summary of the loaded data.
    
    Parameters:
    -----------
    main_data : pd.DataFrame
        Main data dataframe
    impact_links : pd.DataFrame
        Impact links dataframe
    """
    print("=" * 70)
    print("📊 DATA LOADING SUMMARY")
    print("=" * 70)
    
    # Main data summary
    print(f"\n📄 MAIN DATA:")
    print(f"   Total records: {len(main_data):,}")
    
    if not main_data.empty:
        print(f"   Columns: {len(main_data.columns)}")
        print(f"   Columns list: {main_data.columns.tolist()}")
        
        # Record type distribution
        if 'record_type' in main_data.columns:
            record_counts = main_data['record_type'].value_counts()
            print(f"\n   📈 RECORD TYPE DISTRIBUTION:")
            for record_type, count in record_counts.items():
                percentage = (count / len(main_data)) * 100
                print(f"      {record_type}: {count:,} ({percentage:.1f}%)")
        
        # Date range
        date_columns = [col for col in main_data.columns if 'date' in col.lower()]
        if date_columns:
            print(f"\n   📅 DATE COLUMNS FOUND: {date_columns}")
    
    # Impact links summary
    print(f"\n🔗 IMPACT LINKS:")
    print(f"   Total links: {len(impact_links):,}")
    
    if not impact_links.empty:
        print(f"   Columns: {len(impact_links.columns)}")
        
        # Impact direction distribution
        if 'impact_direction' in impact_links.columns:
            direction_counts = impact_links['impact_direction'].value_counts()
            print(f"\n   📈 IMPACT DIRECTION:")
            for direction, count in direction_counts.items():
                print(f"      {direction}: {count}")
    
    print("\n" + "=" * 70)

# Example usage
if __name__ == "__main__":
    print("🚀 Testing DataLoader with Excel files...")
    print("=" * 50)
    
    try:
        # Initialize DataLoader
        loader = DataLoader()
        
        # Check which files exist
        print("\n🔍 Checking for data files...")
        file_status = loader.check_data_files()
        
        for file_name, exists in file_status.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {file_name}: {exists}")
        
        # Load unified data
        print("\n📥 Loading unified data...")
        main_data, impact_links = loader.load_unified_data()
        
        # Display summary
        display_data_summary(main_data, impact_links)
        
        # Load reference codes
        print("\n📋 Loading reference codes...")
        ref_codes = loader.load_reference_codes()
        
        # Load additional data guide
        print("\n📚 Loading additional data guide...")
        guide_sheets = loader.load_additional_data_guide()
        if guide_sheets:
            print(f"   Loaded {len(guide_sheets)} sheet(s): {list(guide_sheets.keys())}")
        
        print("\n🎉 Data loading test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Ensure Excel files are in data/raw/ folder")
        print("2. Check file names match exactly:")
        print("   - ethiopia_fi_unified_data.xlsx")
        print("   - reference_codes.xlsx")
        print("   - Additional Data Points Guide.xlsx")
        print("3. Make sure files are not open in Excel")
        print("4. Check file permissions")