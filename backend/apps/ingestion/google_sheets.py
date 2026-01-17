"""
Google Sheets Integration for Property Ingestion
Allows processing properties directly from Google Sheets
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service for interacting with Google Sheets API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'  # Cambiado de drive.file a drive completo
    ]
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets service.
        
        Args:
            credentials_path: Path to service account credentials JSON file
        """
        if credentials_path is None:
            credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        
        if not credentials_path or not os.path.exists(credentials_path):
            raise ValueError(
                "Google Sheets credentials not found. Set GOOGLE_SHEETS_CREDENTIALS_PATH "
                "environment variable or provide credentials_path parameter."
            )
        
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=self.SCOPES
        )
        
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheets_api = self.service.spreadsheets()
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def create_results_spreadsheet(self, title: Optional[str] = None) -> Dict[str, str]:
        """
        Create a new Google Sheet for batch processing results.
        
        Args:
            title: Optional custom title for the spreadsheet
            
        Returns:
            Dict with 'spreadsheet_id', 'spreadsheet_url', and 'title'
        """
        if title is None:
            title = f"Resultados Procesamiento - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # Define headers for results sheet
            headers = [
                'URL Original',
                'Título Propiedad',
                'Precio USD',
                'Habitaciones',
                'Baños',
                'Área (m²)',
                'Ubicación',
                'Tipo Propiedad',
                'Estado Procesamiento',
                'Fecha Procesamiento',
                'Notas',
                'Property ID'
            ]
            
            # Create spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': title
                },
                'sheets': [{
                    'properties': {
                        'title': 'Resultados',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': len(headers),
                            'frozenRowCount': 1
                        }
                    }
                }]
            }
            
            spreadsheet = self.sheets_api.create(body=spreadsheet_body).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']
            spreadsheet_url = spreadsheet['spreadsheetUrl']
            
            # Write headers
            self.sheets_api.values().update(
                spreadsheetId=spreadsheet_id,
                range='Resultados!A1:L1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # Format headers (bold, background color)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': len(headers)
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.2,
                                'green': 0.6,
                                'blue': 0.86
                            },
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                }
                            },
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            }]
            
            self.sheets_api.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Created results spreadsheet: {title} ({spreadsheet_id})")
            
            return {
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': spreadsheet_url,
                'title': title
            }
            
        except HttpError as e:
            logger.error(f"Error creating results spreadsheet: {e}")
            raise
    
    def append_result_row(
        self,
        spreadsheet_id: str,
        result_data: Dict[str, Any]
    ) -> bool:
        """
        Append a result row to the results spreadsheet.
        
        Args:
            spreadsheet_id: ID of the results spreadsheet
            result_data: Dictionary with property data and processing result
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract data from result
            property_data = result_data.get('property_data', {})
            
            # Convert Decimal to float for Google Sheets
            price = property_data.get('price')
            if price is not None:
                price = float(price)
            
            area = property_data.get('area')
            if area is not None:
                area = float(area)
            
            row_values = [
                result_data.get('url', ''),
                property_data.get('title', ''),
                price if price else '',
                property_data.get('bedrooms', ''),
                property_data.get('bathrooms', ''),
                area if area else '',
                property_data.get('location', ''),
                property_data.get('property_type', ''),
                result_data.get('status', 'Procesado'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                result_data.get('notes', ''),
                result_data.get('property_id', '')
            ]
            
            # Append row
            self.sheets_api.values().append(
                spreadsheetId=spreadsheet_id,
                range='Resultados!A:L',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_values]}
            ).execute()
            
            return True
            
        except HttpError as e:
            logger.error(f"Error appending result row: {e}")
            return False
    
    def get_or_create_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """
        Get or create a sheet (tab) in the spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet to get or create
            
        Returns:
            True if sheet exists or was created successfully
        """
        try:
            # Get spreadsheet metadata to check existing sheets
            spreadsheet = self.sheets_api.get(spreadsheetId=spreadsheet_id).execute()
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            
            if sheet_name in existing_sheets:
                logger.info(f"📋 Sheet '{sheet_name}' already exists")
                return True
            
            # Create new sheet
            logger.info(f"📝 Creating new sheet '{sheet_name}'...")
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 30
                            }
                        }
                    }
                }]
            }
            
            self.sheets_api.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            logger.info(f"✅ Created sheet '{sheet_name}'")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error getting/creating sheet: {e}")
            return False
    
    def clear_sheet(self, spreadsheet_id: str, sheet_name: str = 'Sheet1') -> bool:
        """
        Clear all data from a sheet (keeps the sheet structure).
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet to clear (default: 'Sheet1')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.sheets_api.values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:ZZ"
            ).execute()
            
            logger.info(f"✅ Cleared sheet '{sheet_name}' in {spreadsheet_id}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error clearing sheet: {e}")
            return False

    def append_rows(self, spreadsheet_id: str, range_name: str, rows: List[List[Any]], sheet_name: str = None) -> bool:
        """
        Append multiple rows to a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to append to (e.g., 'Sheet1!A:G')
            rows: List of row data (each row is a list of values)
            sheet_name: Optional sheet name to log (for better logging)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.sheets_api.values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
            
            sheet_info = f" to sheet '{sheet_name}'" if sheet_name else ""
            logger.info(f"✅ Appended {len(rows)} rows{sheet_info} ({spreadsheet_id})")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Error appending rows: {e}")
            return False
    
    def ensure_headers(self, spreadsheet_id: str) -> bool:
        """
        Ensure the sheet has proper headers. Create them if they don't exist or are incomplete.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            
        Returns:
            True if headers exist or were created successfully
        """
        try:
            result = self.sheets_api.values().get(
                spreadsheetId=spreadsheet_id,
                range='Sheet1!A1:K1'
            ).execute()
            
            values = result.get('values', [])
            
            # Define expected headers
            expected_headers = [
                'URL', 'Tipo', 'Status', 'Fecha', 'Notas',
                'Precio USD', 'Habitaciones', 'Baños', 'M² Construcción', 'Ubicación', 'Property ID'
            ]
            
            current_headers = values[0] if values and values[0] else []
            
            # Check if headers are complete (all 11 columns present)
            headers_complete = (
                len(current_headers) == 11 and
                all(current_headers[i] == expected_headers[i] for i in range(11))
            )
            
            if not headers_complete:
                if len(current_headers) == 0:
                    logger.info("📝 [GOOGLE SHEETS] No headers found - creating them...")
                else:
                    logger.info(f"📝 [GOOGLE SHEETS] Incomplete headers found ({len(current_headers)}/11) - updating to full set...")
                    logger.info(f"    Current: {current_headers}")
                
                self.sheets_api.values().update(
                    spreadsheetId=spreadsheet_id,
                    range='Sheet1!A1:K1',
                    valueInputOption='RAW',
                    body={'values': [expected_headers]}
                ).execute()
                
                logger.info("✅ [GOOGLE SHEETS] Headers created/updated successfully with all 11 columns")
                return True
            else:
                logger.info(f"✅ [GOOGLE SHEETS] All 11 headers already exist and are correct")
                return True
                
        except HttpError as error:
            logger.error(f"❌ [GOOGLE SHEETS] Error ensuring headers: {error}")
            return False
    
    def read_pending_rows(
        self, 
        spreadsheet_id: str, 
        range_name: str = 'Sheet1!A:K'
    ) -> List[Dict[str, Any]]:
        """
        Read all rows with 'Pendiente' status from the sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to read
            
        Returns:
            List of dictionaries with row data
        """
        try:
            result = self.sheets_api.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            logger.info(f"📊 [GOOGLE SHEETS] Total rows retrieved from API: {len(values)}")
            
            if not values:
                logger.info("❌ [GOOGLE SHEETS] No data found in sheet")
                return []
            
            # Detect if first row is a header or a URL
            first_row = values[0]
            is_header = False
            
            if first_row and len(first_row) > 0:
                first_cell = str(first_row[0]).strip().lower()
                # Check if first cell looks like a header (not a URL)
                is_header = (
                    'url' in first_cell or 
                    'link' in first_cell or 
                    'enlace' in first_cell or
                    (not first_cell.startswith('http'))
                )
            
            if is_header:
                logger.info(f"📋 [GOOGLE SHEETS] Detected header row: {first_row}")
                headers = first_row
                data_rows = values[1:]
                start_row = 2
            else:
                logger.info(f"📋 [GOOGLE SHEETS] No header detected - first row is data: {first_row[0][:50] if first_row else ''}")
                # Create default headers
                headers = ['URL', 'Tipo', 'Status', 'Fecha', 'Notas', 'Precio USD', 'Habitaciones', 'Baños', 'M² Construcción', 'Ubicación', 'Property ID']
                data_rows = values
                start_row = 1
            
            logger.info(f"📋 [GOOGLE SHEETS] Processing {len(data_rows)} data rows starting from row {start_row}")
            logger.info(f"📋 [GOOGLE SHEETS] Processing {len(data_rows)} data rows starting from row {start_row}")
            
            rows = []
            
            for idx, row in enumerate(data_rows, start=start_row):
                # Pad row if it's shorter than headers
                row_data = row + [''] * (len(headers) - len(row))
                
                row_dict = {
                    'row_index': idx,
                    'url': row_data[0] if len(row_data) > 0 else '',
                    'tipo': row_data[1] if len(row_data) > 1 else '',
                    'status': row_data[2] if len(row_data) > 2 else '',
                    'fecha_procesada': row_data[3] if len(row_data) > 3 else '',
                    'notas': row_data[4] if len(row_data) > 4 else '',
                    'precio': row_data[5] if len(row_data) > 5 else '',
                    'habitaciones': row_data[6] if len(row_data) > 6 else '',
                    'banos': row_data[7] if len(row_data) > 7 else '',
                    'm2': row_data[8] if len(row_data) > 8 else '',
                    'ubicacion': row_data[9] if len(row_data) > 9 else '',
                    'property_id': row_data[10] if len(row_data) > 10 else '',
                }
                
                logger.info(f"🔍 [ROW {idx}] URL: '{row_dict['url'][:50]}...' | Status: '{row_dict['status']}' | Status lower: '{row_dict['status'].strip().lower()}'")
                
                # Check if row has complete data (all property columns filled)
                has_complete_data = all([
                    row_dict.get('precio', '').strip(),
                    row_dict.get('habitaciones', '').strip(),
                    row_dict.get('banos', '').strip(),
                    row_dict.get('m2', '').strip(),
                    row_dict.get('ubicacion', '').strip(),
                    row_dict.get('property_id', '').strip()
                ])
                
                status_lower = row_dict['status'].strip().lower()
                has_url = bool(row_dict['url'].strip())
                
                # Include if:
                # 1. Status is 'Pendiente' (or empty) with valid URL, OR
                # 2. Status is 'Procesado' or 'Error' BUT missing data columns (needs reprocessing)
                should_process = False
                
                if (status_lower == 'pendiente' or status_lower == '') and has_url:
                    logger.info(f"✅ [ROW {idx}] MATCHED as '{row_dict['status'] or 'empty'}' - adding to processing queue")
                    should_process = True
                elif status_lower in ['procesado', 'error'] and has_url and not has_complete_data:
                    logger.info(f"🔄 [ROW {idx}] MATCHED as '{row_dict['status']}' but INCOMPLETE DATA - will reprocess")
                    logger.info(f"   Missing data: Precio={bool(row_dict.get('precio'))}, Habitaciones={bool(row_dict.get('habitaciones'))}, Baños={bool(row_dict.get('banos'))}, M²={bool(row_dict.get('m2'))}, Ubicación={bool(row_dict.get('ubicacion'))}, Property ID={bool(row_dict.get('property_id'))}")
                    should_process = True
                else:
                    logger.info(f"⏭️ [ROW {idx}] SKIPPED - status='{row_dict['status']}', has_url={has_url}, complete_data={has_complete_data}")
                
                if should_process:
                    rows.append(row_dict)
            
            logger.info(f"📊 [GOOGLE SHEETS] Found {len(rows)} pending rows out of {len(values)-1} total data rows")
            return rows
            
        except HttpError as error:
            logger.error(f"Error reading from Google Sheets: {error}")
            raise
    
    def update_row_status(
        self,
        spreadsheet_id: str,
        row_index: int,
        status: str,
        notes: str = '',
        date_processed: Optional[str] = None,
        property_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update the status of a specific row and optionally add extracted property data.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            row_index: The row number (1-indexed)
            status: New status value ('Procesado', 'Error', etc.)
            notes: Optional notes to add
            date_processed: Optional date string, uses current time if None
            property_data: Optional dictionary with extracted property data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if date_processed is None:
                date_processed = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"📝 [GOOGLE SHEETS] Preparing to update row {row_index}")
            logger.info(f"📝 [GOOGLE SHEETS] Spreadsheet ID: {spreadsheet_id}")
            logger.info(f"📝 [GOOGLE SHEETS] Status: {status}")
            logger.info(f"📝 [GOOGLE SHEETS] Date: {date_processed}")
            logger.info(f"📝 [GOOGLE SHEETS] Notes: {notes[:100]}..." if len(notes) > 100 else f"📝 [GOOGLE SHEETS] Notes: {notes}")
            
            # Prepare values: C (status), D (fecha), E (notas), F-K (property data)
            values = [status, date_processed, notes]
            
            # Add property data if available
            if property_data:
                logger.info(f"📝 [GOOGLE SHEETS] Adding property data to sheet")
                
                # Convert Decimal to float/str for JSON serialization
                def convert_value(val):
                    if val is None or val == '':
                        return ''
                    if hasattr(val, '__float__'):  # Decimal, int, float
                        return float(val)
                    return str(val)
                
                values.extend([
                    convert_value(property_data.get('price_usd', '')),
                    convert_value(property_data.get('bedrooms', '')),
                    convert_value(property_data.get('bathrooms', '')),
                    convert_value(property_data.get('square_meters', '')),
                    str(property_data.get('location', '')),
                    str(property_data.get('property_id', ''))
                ])
                range_name = f'Sheet1!C{row_index}:K{row_index}'
            else:
                range_name = f'Sheet1!C{row_index}:E{row_index}'
            
            values = [values]  # Wrap in list for API
            
            logger.info(f"📝 [GOOGLE SHEETS] Range: {range_name}")
            logger.info(f"📝 [GOOGLE SHEETS] Values to write: {values}")
            
            body = {
                'values': values
            }
            
            logger.info(f"📝 [GOOGLE SHEETS] Calling sheets API update...")
            result = self.sheets_api.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ [GOOGLE SHEETS] API Response: {result}")
            logger.info(f"✅ [GOOGLE SHEETS] Successfully updated row {row_index} with status: {status}")
            logger.info(f"✅ [GOOGLE SHEETS] Updated cells: {result.get('updatedCells', 'unknown')}")
            logger.info(f"✅ [GOOGLE SHEETS] Updated range: {result.get('updatedRange', 'unknown')}")
            return True
            
        except HttpError as error:
            logger.error(f"❌ [GOOGLE SHEETS] HttpError updating row {row_index}: {error}")
            logger.error(f"❌ [GOOGLE SHEETS] Error details: {error.content if hasattr(error, 'content') else 'No details'}")
            return False
        except Exception as e:
            logger.error(f"❌ [GOOGLE SHEETS] Unexpected error updating row {row_index}: {e}")
            logger.error(f"❌ [GOOGLE SHEETS] Exception type: {type(e).__name__}")
            return False
    
    def batch_update_rows(
        self,
        spreadsheet_id: str,
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update multiple rows at once.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            updates: List of update dictionaries with keys:
                    - row_index: int
                    - status: str
                    - notes: str
                    - date_processed: str (optional)
                    
        Returns:
            True if successful, False otherwise
        """
        try:
            data = []
            
            for update in updates:
                row_index = update['row_index']
                status = update.get('status', 'Error')
                notes = update.get('notes', '')
                date_processed = update.get(
                    'date_processed',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                
                range_name = f'Sheet1!C{row_index}:E{row_index}'
                values = [[status, date_processed, notes]]
                
                data.append({
                    'range': range_name,
                    'values': values
                })
            
            body = {
                'valueInputOption': 'RAW',
                'data': data
            }
            
            self.sheets_api.values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Batch updated {len(updates)} rows")
            return True
            
        except HttpError as error:
            logger.error(f"Error batch updating Google Sheets: {error}")
            return False
    
    def create_template_sheet(self, title: str = "Property Ingestion Template") -> str:
        """
        Create a new Google Sheet with the proper template structure.
        
        Args:
            title: Title for the new spreadsheet
            
        Returns:
            The spreadsheet ID of the created sheet
        """
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [{
                    'properties': {
                        'title': 'Sheet1',
                        'gridProperties': {
                            'frozenRowCount': 1  # Freeze header row
                        }
                    }
                }]
            }
            
            result = self.sheets_api.create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheetId']
            
            # Add headers
            headers = [[
                'URL de la propiedad',
                'Tipo',
                'Status',
                'Fecha procesada',
                'Notas'
            ]]
            
            body = {
                'values': headers
            }
            
            self.sheets_api.values().update(
                spreadsheetId=spreadsheet_id,
                range='Sheet1!A1:E1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format header row (bold)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            },
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }]
            
            body = {
                'requests': requests
            }
            
            self.sheets_api.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Created template sheet: {spreadsheet_id}")
            return spreadsheet_id
            
        except HttpError as error:
            logger.error(f"Error creating template sheet: {error}")
            raise


def process_sheet_batch(
    spreadsheet_id: str,
    process_callback,
    credentials_path: Optional[str] = None,
    task_id: Optional[str] = None,
    create_results_sheet: bool = False,
    results_sheet_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all pending rows from a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        process_callback: Function to call for each URL, should return (success, result)
        credentials_path: Optional path to credentials file
        task_id: Optional task ID for progress tracking
        create_results_sheet: If True, writes to results spreadsheet
        results_sheet_id: Optional ID of pre-created results spreadsheet
        
    Returns:
        Dictionary with processing results and optionally results_spreadsheet info
    """
    sheets_service = GoogleSheetsService(credentials_path)
    
    # Read pending rows
    pending_rows = sheets_service.read_pending_rows(spreadsheet_id)
    
    if not pending_rows:
        return {
            'total': 0,
            'processed': 0,
            'failed': 0,
            'results': []
        }
    
    # Use provided results spreadsheet if available
    results_spreadsheet = None
    if create_results_sheet and results_sheet_id:
        results_spreadsheet = {
            'spreadsheet_id': results_sheet_id,
            'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{results_sheet_id}/edit',
            'title': 'Results Sheet'
        }
        logger.info(f"Using results spreadsheet: {results_spreadsheet['spreadsheet_url']}")
    
    results = []
    processed_count = 0
    failed_count = 0
    total_rows = len(pending_rows)
    
    # Process each row
    for index, row in enumerate(pending_rows):
        try:
            url = row['url']
            logger.info(f"Processing row {row['row_index']}: {url} ({index + 1}/{total_rows})")
            
            # Call the processing callback with index information for progress
            success, result = process_callback(url, index, total_rows)
            
            if success:
                # Prepare property data for sheet
                property_data = {
                    'price_usd': result.get('price_usd', ''),
                    'bedrooms': result.get('bedrooms', ''),
                    'bathrooms': result.get('bathrooms', ''),
                    'square_meters': result.get('square_meters', ''),
                    'location': result.get('location', ''),
                    'property_id': result.get('property_id', '')
                }
                
                sheets_service.update_row_status(
                    spreadsheet_id,
                    row['row_index'],
                    status='Procesado',
                    notes=f"Property ID: {result.get('property_id', 'N/A')}",
                    property_data=property_data
                )
                
                # Add to results spreadsheet if it was created
                if results_spreadsheet:
                    result_row_data = {
                        'url': url,
                        'property_data': {
                            'title': result.get('title', ''),
                            'price': result.get('price_usd', ''),
                            'bedrooms': result.get('bedrooms', ''),
                            'bathrooms': result.get('bathrooms', ''),
                            'area': result.get('square_meters', ''),
                            'location': result.get('location', ''),
                            'property_type': result.get('property_type', ''),
                        },
                        'status': 'Procesado',
                        'notes': f"Property ID: {result.get('property_id', 'N/A')}",
                        'property_id': result.get('property_id', '')
                    }
                    sheets_service.append_result_row(
                        results_spreadsheet['spreadsheet_id'],
                        result_row_data
                    )
                
                processed_count += 1
            else:
                sheets_service.update_row_status(
                    spreadsheet_id,
                    row['row_index'],
                    status='Error',
                    notes=result.get('error', 'Unknown error')
                )
                
                # Add error to results spreadsheet if it was created
                if results_spreadsheet:
                    error_row_data = {
                        'url': url,
                        'property_data': {},
                        'status': 'Error',
                        'notes': result.get('error', 'Unknown error'),
                        'property_id': ''
                    }
                    sheets_service.append_result_row(
                        results_spreadsheet['spreadsheet_id'],
                        error_row_data
                    )
                
                failed_count += 1
            
            results.append({
                'row': row['row_index'],
                'url': url,
                'success': success,
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error processing row {row['row_index']}: {e}")
            sheets_service.update_row_status(
                spreadsheet_id,
                row['row_index'],
                status='Error',
                notes=str(e)
            )
            
            # Add error to results spreadsheet if it was created
            if results_spreadsheet:
                error_row_data = {
                    'url': row.get('url', ''),
                    'property_data': {},
                    'status': 'Error',
                    'notes': str(e),
                    'property_id': ''
                }
                sheets_service.append_result_row(
                    results_spreadsheet['spreadsheet_id'],
                    error_row_data
                )
            
            failed_count += 1
            results.append({
                'row': row['row_index'],
                'url': row['url'],
                'success': False,
                'result': {'error': str(e)}
            })
    
    result_dict = {
        'total': len(pending_rows),
        'processed': processed_count,
        'failed': failed_count,
        'results': results
    }
    
    # Add results spreadsheet info if it was created
    if results_spreadsheet:
        result_dict['results_spreadsheet'] = results_spreadsheet
    
    return result_dict
