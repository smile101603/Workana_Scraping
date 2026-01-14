"""
Google Sheets exporter for Workana jobs
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import TransportError
from requests.exceptions import ConnectionError as RequestsConnectionError
from config.settings import GOOGLE_SHEETS_SPREADSHEET_ID, GOOGLE_SHEETS_CREDENTIALS_PATH


class SheetsExporter:
    """Export jobs to Google Sheets with daily sheets and conditional formatting"""
    
    # Define the scope for Google Sheets API
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    def __init__(self, spreadsheet_id: str = None, credentials_path: str = None, translator = None):
        """
        Initialize Google Sheets exporter
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            credentials_path: Path to Google service account credentials JSON file
            translator: Optional translator instance for translating job data
        """
        self.spreadsheet_id = spreadsheet_id or GOOGLE_SHEETS_SPREADSHEET_ID
        self.credentials_path = credentials_path or GOOGLE_SHEETS_CREDENTIALS_PATH
        self.translator = translator
        self.client = None
        self.spreadsheet = None
        
        if not self.spreadsheet_id:
            raise ValueError("Google Sheets spreadsheet ID is required")
        
        if not self.credentials_path:
            raise ValueError("Google service account credentials path is required")
        
        self._connect()
    
    def _connect(self):
        """Connect to Google Sheets API"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPE
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        except (TransportError, RequestsConnectionError) as e:
            error_msg = str(e)
            if "Failed to resolve" in error_msg or "getaddrinfo failed" in error_msg:
                raise ConnectionError(
                    "Cannot connect to Google Sheets API: Network connection failed. "
                    "Please check your internet connection and DNS settings."
                ) from e
            else:
                raise ConnectionError(
                    f"Cannot connect to Google Sheets API: {error_msg}"
                ) from e
        except Exception as e:
            raise Exception(f"Failed to connect to Google Sheets: {e}")
    
    def get_date_sheet_name(self, date: datetime = None) -> str:
        """
        Get sheet name for a date in format MM/DD
        
        Args:
            date: Date object (defaults to today)
        
        Returns:
            Sheet name like "12/09"
        """
        if date is None:
            date = datetime.now()
        return date.strftime("%m/%d")
    
    def ensure_today_sheet_exists(self, date: datetime = None) -> gspread.Worksheet:
        """
        Ensure today's sheet exists, create it if it doesn't
        
        Args:
            date: Date object (defaults to today)
        
        Returns:
            Worksheet object for today's sheet
        """
        sheet_name = self.get_date_sheet_name(date)
        return self.get_or_create_sheet(sheet_name)
    
    def get_or_create_sheet(self, sheet_name: str) -> gspread.Worksheet:
        """
        Get existing sheet or create new one
        
        Args:
            sheet_name: Name of the sheet
        
        Returns:
            Worksheet object
        """
        try:
            # Try to get existing sheet
            worksheet = self.spreadsheet.worksheet(sheet_name)
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # Create new sheet
            try:
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=20
                )
                # Set up headers
                self._setup_headers(worksheet)
                return worksheet
            except (TransportError, RequestsConnectionError) as e:
                error_msg = str(e)
                if "Failed to resolve" in error_msg or "getaddrinfo failed" in error_msg:
                    raise ConnectionError(
                        "Cannot access Google Sheets: Network connection failed. "
                        "Please check your internet connection and DNS settings."
                    ) from e
                raise
        except (TransportError, RequestsConnectionError) as e:
            error_msg = str(e)
            if "Failed to resolve" in error_msg or "getaddrinfo failed" in error_msg:
                raise ConnectionError(
                    "Cannot access Google Sheets: Network connection failed. "
                    "Please check your internet connection and DNS settings."
                ) from e
            raise
    
    def _setup_headers(self, worksheet: gspread.Worksheet):
        """Set up column headers in the worksheet at row 1 (only if they don't exist)"""
        headers = [
            "ID",
            "Title",
            "Description",
            "URL",
            "Posted Date",
            "Bids Count",
            "Budget",
            "Budget Min",
            "Budget Max",
            "Budget Type",
            "Skills",
            "Client Name",
            "Client Country",
            "Client Rating",
            "Payment Verified",
            "Last Reply",
            "Featured",
            "Max Project",
            "First Seen At",
            "Scraped At"
        ]
        
        # Check if row 1 already has the expected headers
        try:
            row1_values = worksheet.row_values(1)
            # Check if row 1 matches our headers (at least first few should match)
            if row1_values and len(row1_values) > 0:
                # Check if first few headers match
                if (len(row1_values) >= 3 and 
                    row1_values[0] == headers[0] and 
                    row1_values[1] == headers[1] and 
                    row1_values[2] == headers[2]):
                    # Headers already exist in row 1, skip setup
                    return
        except:
            # If we can't read row 1, proceed with setup
            pass
        
        # Insert headers at row 1 using update (this will overwrite row 1 if it exists)
        worksheet.update('A1', [headers])
        
        # Format header row (bold, freeze)
        worksheet.format('1:1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        # Freeze header row
        worksheet.freeze(rows=1)
    
    def _apply_formatting_to_row(self, worksheet: gspread.Worksheet, row: int, job: Dict):
        """
        Apply formatting to a single row based on job data
        
        Args:
            worksheet: Worksheet to format
            row: Row number (1-indexed)
            job: Job dictionary with budget information
        """
        try:
            budget_type = job.get('budget_type')
            budget_min = job.get('budget_min')
            
            # Convert budget_min to float if possible
            budget_min_float = None
            if budget_min is not None:
                try:
                    budget_min_float = float(budget_min)
                except (ValueError, TypeError):
                    pass
            
            # Determine color based on rules:
            # Green: >= 1000 or hourly
            # Yellow: 500-1000 (fixed only)
            # Light orange: 250-500 (fixed only)
            color = None
            color_name = None
            
            if budget_type == 'hourly' or (budget_min_float and budget_min_float >= 1000):
                # Green
                color = {'red': 0.85, 'green': 0.95, 'blue': 0.85}
                color_name = 'Green'
            elif budget_min_float and 500 <= budget_min_float < 1000 and budget_type == 'fixed':
                # Yellow
                color = {'red': 1.0, 'green': 0.95, 'blue': 0.8}
                color_name = 'Yellow'
            elif budget_min_float and 250 <= budget_min_float < 500 and budget_type == 'fixed':
                # Light orange
                color = {'red': 1.0, 'green': 0.8, 'blue': 0.6}
                color_name = 'Light Orange'
            
            # Apply formatting if color is determined
            if color:
                worksheet.format(f'{row}:{row}', {
                    'backgroundColor': color
                })
                print(f"  Row {row}: Applied {color_name} formatting (Budget: {budget_min}, Type: {budget_type})")
            else:
                print(f"  Row {row}: No formatting applied (Budget: {budget_min}, Type: {budget_type})")
        except Exception as e:
            print(f"Warning: Could not format row {row}: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_simple_formatting(self, worksheet: gspread.Worksheet, start_row: int, end_row: int, jobs: List[Dict] = None):
        """
        Apply formatting row by row based on price ranges
        
        Args:
            worksheet: Worksheet to format
            start_row: First row to format (1-indexed)
            end_row: Last row to format (1-indexed)
            jobs: Optional list of job dictionaries (preferred method)
        """
        if jobs and len(jobs) == (end_row - start_row + 1):
            # Use job data directly (more reliable)
            # Prepare batch update requests
            requests = []
            sheet_id = worksheet.id
            
            for i, job in enumerate(jobs):
                row = start_row + i
                budget_type = job.get('budget_type')
                budget_min = job.get('budget_min')
                
                # Convert budget_min to float if possible
                budget_min_float = None
                if budget_min is not None:
                    try:
                        budget_min_float = float(budget_min)
                    except (ValueError, TypeError):
                        pass
                
                # Determine color based on rules
                color = None
                color_name = None
                
                if budget_type == 'hourly' or (budget_min_float and budget_min_float >= 1000):
                    # Green
                    color = {'red': 0.85, 'green': 0.95, 'blue': 0.85}
                    color_name = 'Green'
                elif budget_min_float and 500 <= budget_min_float < 1000 and budget_type == 'fixed':
                    # Yellow
                    color = {'red': 1.0, 'green': 0.95, 'blue': 0.8}
                    color_name = 'Yellow'
                elif budget_min_float and 250 <= budget_min_float < 500 and budget_type == 'fixed':
                    # Light orange
                    color = {'red': 1.0, 'green': 0.8, 'blue': 0.6}
                    color_name = 'Light Orange'
                
                # Add formatting request if color is determined
                if color:
                    requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': sheet_id,
                                'startRowIndex': row - 1,  # 0-indexed
                                'endRowIndex': row,        # 0-indexed (exclusive)
                                'startColumnIndex': 0,
                                'endColumnIndex': 20  # Format entire row
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': color['red'],
                                        'green': color['green'],
                                        'blue': color['blue']
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat.backgroundColor'
                        }
                    })
                    print(f"  Row {row}: Will apply {color_name} (Budget: {budget_min}, Type: {budget_type})")
                else:
                    print(f"  Row {row}: No formatting (Budget: {budget_min}, Type: {budget_type})")
            
            # Apply all formatting in one batch update
            if requests:
                try:
                    self.spreadsheet.batch_update({'requests': requests})
                    print(f"✅ Applied formatting to {len(requests)} row(s) via batch update")
                except Exception as e:
                    print(f"⚠️  Batch formatting failed: {e}")
                    print("   Trying individual formatting...")
                    # Fallback to individual formatting
                    for i, job in enumerate(jobs):
                        row = start_row + i
                        self._apply_formatting_to_row(worksheet, row, job)
        else:
            # Fallback: read from sheet
            for row in range(start_row, end_row + 1):
                try:
                    # Get budget values from the row
                    # Column I (9) = Budget Type, Column H (8) = Budget Min
                    budget_type = worksheet.cell(row, 9).value  # Budget Type
                    budget_min = worksheet.cell(row, 8).value   # Budget Min
                    
                    try:
                        budget_min_float = float(budget_min) if budget_min and str(budget_min).strip() else None
                    except (ValueError, TypeError):
                        budget_min_float = None
                    
                    # Determine color based on rules:
                    # Green: >= 1000 or hourly
                    # Yellow: 500-1000 (fixed only)
                    # Light orange: 250-500 (fixed only)
                    color = None
                    
                    if budget_type == 'hourly' or (budget_min_float and budget_min_float >= 1000):
                        # Green
                        color = {'red': 0.85, 'green': 0.95, 'blue': 0.85}
                    elif budget_min_float and 500 <= budget_min_float < 1000 and budget_type == 'fixed':
                        # Yellow
                        color = {'red': 1.0, 'green': 0.95, 'blue': 0.8}
                    elif budget_min_float and 250 <= budget_min_float < 500 and budget_type == 'fixed':
                        # Light orange
                        color = {'red': 1.0, 'green': 0.8, 'blue': 0.6}
                    
                    # Apply formatting if color is determined
                    if color:
                        worksheet.format(f'{row}:{row}', {
                            'backgroundColor': color
                        })
                except Exception as e:
                    print(f"Warning: Could not format row {row}: {e}")
                    continue
    
    def job_to_row(self, job: Dict) -> List:
        """
        Convert job dictionary to row data
        
        Args:
            job: Job dictionary
        
        Returns:
            List of values for the row
        """
        # Handle skills (convert list to comma-separated string)
        skills = job.get('skills', [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = [skills]
        skills_str = ', '.join(skills) if isinstance(skills, list) else str(skills) if skills else ''
        
        return [
            job.get('id', ''),
            job.get('title', ''),
            job.get('description', ''),
            job.get('url', ''),
            job.get('posted_date_relative', ''),
            job.get('bids_count', ''),
            job.get('budget', ''),
            job.get('budget_min', ''),
            job.get('budget_max', ''),
            job.get('budget_type', ''),
            skills_str,
            job.get('client_name', ''),
            job.get('client_country', ''),
            job.get('client_rating', ''),
            'Yes' if job.get('client_payment_verified') else 'No',
            job.get('client_last_reply', ''),
            'Yes' if job.get('is_featured') else 'No',
            'Yes' if job.get('is_max_project') else 'No',
            job.get('first_seen_at', ''),
            job.get('scraped_at', '')
        ]
    
    def export_jobs(self, jobs: List[Dict], date: datetime = None) -> int:
        """
        Export jobs to Google Sheets in a daily sheet
        
        Args:
            jobs: List of job dictionaries
            date: Date for the sheet (defaults to today)
        
        Returns:
            Number of jobs exported
        """
        if not jobs:
            return 0
        
        sheet_name = self.get_date_sheet_name(date)
        worksheet = self.get_or_create_sheet(sheet_name)
        
        # Ensure headers exist in row 1 (setup if they don't)
        self._setup_headers(worksheet)
        
        print(f"  Processing {len(jobs)} job(s) for export...")
        
        # Translate jobs if translator is available
        translated_jobs = []
        if self.translator and self.translator.is_available():
            print(f"  Translating {len(jobs)} job(s) before export...")
            for i, job in enumerate(jobs, 1):
                try:
                    translated_job = self.translator.translate_job_data(job.copy())
                    translated_jobs.append(translated_job)
                    if len(jobs) > 10 and i % 10 == 0:
                        print(f"    Translated {i}/{len(jobs)} jobs...")
                except Exception as e:
                    print(f"    ⚠️  Translation failed for job {job.get('id', 'unknown')}: {e}")
                    # Use original job if translation fails
                    translated_jobs.append(job)
            jobs_to_export = translated_jobs
            print(f"  Translation complete. {len(translated_jobs)} job(s) ready for export.")
        else:
            jobs_to_export = jobs
            print(f"  Translation skipped (translator not available). Using original job data.")
        
        # Get current row count (to know where to start)
        # Filter out empty rows by checking if row has any non-empty values
        all_values = worksheet.get_all_values()
        existing_rows = len([row for row in all_values if any(cell.strip() for cell in row)])
        # Start at row 2 if only headers exist, otherwise continue from existing rows
        start_row = 2 if existing_rows <= 1 else existing_rows + 1
        
        print(f"  Current sheet has {existing_rows} non-empty row(s). Starting export at row {start_row}.")
        
        # Convert jobs to rows
        rows = [self.job_to_row(job) for job in jobs_to_export]
        
        # Append rows
        if rows:
            try:
                # Get row count before appending
                rows_before = len([row for row in worksheet.get_all_values() if any(cell.strip() for cell in row)])
                
                print(f"  Appending {len(rows)} row(s) to sheet...")
                worksheet.append_rows(rows)
                
                # Increased delay to ensure rows are written before verification
                import time
                time.sleep(1)
                
                # Verify rows were actually written
                rows_after = len([row for row in worksheet.get_all_values() if any(cell.strip() for cell in row)])
                actual_added = rows_after - rows_before
                
                if actual_added != len(rows):
                    print(f"  ⚠️  Warning: Expected {len(rows)} rows, but {actual_added} were added to sheet")
                else:
                    print(f"  ✅ Successfully added {actual_added} row(s) to sheet (rows {start_row}-{start_row + actual_added - 1})")
                
            except (TransportError, RequestsConnectionError) as e:
                error_msg = str(e)
                if "Failed to resolve" in error_msg or "getaddrinfo failed" in error_msg:
                    raise ConnectionError(
                        "Cannot export to Google Sheets: Network connection failed. "
                        "Please check your internet connection and DNS settings."
                    ) from e
                raise
            
            # Apply conditional formatting to newly added rows using job data
            # Use original jobs (not translated) for formatting logic (budget values)
            try:
                end_row = start_row + len(rows) - 1
                print(f"  Applying formatting to rows {start_row}-{end_row}...")
                self._apply_simple_formatting(worksheet, start_row, end_row, jobs)
                print(f"  ✅ Formatting applied successfully")
            except (TransportError, RequestsConnectionError) as e:
                # Formatting failed but data was written, so continue
                print(f"  ⚠️  Warning: Could not apply formatting due to network error: {e}")
            except Exception as e:
                # Other formatting errors
                print(f"  ⚠️  Warning: Could not apply formatting: {e}")
        
        return len(rows)
    
    def is_available(self) -> bool:
        """Check if Google Sheets exporter is available"""
        return self.client is not None and self.spreadsheet is not None

