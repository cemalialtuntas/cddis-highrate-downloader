import os
import gzip
import shutil
import subprocess
from ftplib import FTP_TLS
from typing import List, Optional
from pathlib import Path
from .utils import check_crx2rnx, get_crx2rnx_path
import time

class CDDISFTPClient:
    """CDDIS FTP client for downloading GNSS data."""
    
    def __init__(self):
        self.ftp = None

    def connect(self) -> bool:
        """Establishes FTP connection to CDDIS server."""
        try:
            if self.ftp:
                try:
                    self.ftp.quit()
                except:
                    pass
                self.ftp = None
                
            self.ftp = FTP_TLS('gdc.cddis.eosdis.nasa.gov')
            self.ftp.connect(timeout=30)  # 30 saniyelik timeout ekleyelim
            self.ftp.login()  # anonymous login
            self.ftp.prot_p()  # Set up secure data connection
            self.ftp.set_pasv(True)  # Pasif mod kullan
            return True
        except Exception as e:
            print(f"FTPS connection/login failed: {e}")
            self.ftp = None
            return False

    def list_hour_subfolders(self, base_path: str) -> List[str]:
        """Lists hour-based subdirectories."""
        if not self.ftp:
            return []
        
        try:
            self.ftp.cwd(base_path)
            folders = []
            self.ftp.retrlines('LIST', lambda x: folders.append(x.split()[-1]))
            hour_folders = [f for f in folders if f.isdigit() and len(f) == 2]
            return sorted(hour_folders)
        except Exception as e:
            print(f"Error listing hour subfolders: {e}")
            return []

    def list_crx_files(self, base_path: str, hour_subdir: str, 
                      station_filter: Optional[str] = None) -> List[str]:
        """Lists .crx.gz files in the specified hour directory."""
        max_retries = 3  # Maksimum yeniden deneme sayısı
        retry_count = 0
        
        while retry_count < max_retries:
            if not self.ftp:
                if not self.reconnect():
                    return []
                
            try:
                full_path = f"{base_path}/{hour_subdir}"
                self.ftp.cwd(full_path)
                files = []
                self.ftp.retrlines('LIST', lambda x: files.append(x.split()[-1]))
                
                crx_files = [f for f in files if f.endswith('.crx.gz')]
                if station_filter:
                    crx_files = [f for f in crx_files if f.startswith(station_filter)]
                
                return sorted(crx_files)
            except Exception as e:
                print(f"Error listing .crx.gz files: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Attempting to reconnect (attempt {retry_count + 1}/{max_retries})...")
                    if not self.reconnect():
                        print("Reconnection failed")
                        return []
                else:
                    print("Max retries reached")
                    return []
        return []

    def download_file(self, base_path: str, hour_subdir: str, 
                     filename: str, local_path: str) -> bool:
        """Downloads a single file from FTP to local path."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            if not self.ftp:
                if not self.reconnect():
                    return False
                
            try:
                full_path = f"{base_path}/{hour_subdir}"
                self.ftp.cwd(full_path)
                
                with open(local_path, 'wb') as fp:
                    self.ftp.retrbinary(f'RETR {filename}', fp.write)
                print(f"Downloaded: {filename}")
                return True
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
                if os.path.exists(local_path):
                    os.remove(local_path)
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Attempting to reconnect (attempt {retry_count + 1}/{max_retries})...")
                    if not self.reconnect():
                        print("Reconnection failed")
                        return False
                else:
                    print("Max retries reached")
                    return False
        return False

    def close(self):
        """Closes the FTP connection safely."""
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as e:
                print(f"Warning: Error while closing FTP connection: {e}")
            finally:
                self.ftp = None

    def extract_and_convert(self, file_path: str, convert_to_rnx: bool = False) -> None:
        """
        Extracts .gz file and optionally converts .crx to .rnx using CRX2RNX
        """
        file_path = Path(file_path)
        
        # First extract .gz
        crx_path = file_path.with_suffix('')  # Removes .gz extension
        try:
            with gzip.open(file_path, 'rb') as f_in:
                with open(crx_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Extracted: {crx_path.name}")
            
            # Remove original .gz file
            file_path.unlink()
            
            # Convert to RNX if requested
            if convert_to_rnx:
                # Construct output .rnx filename
                rnx_path = crx_path.with_suffix('.rnx')
                
                # Run CRX2RNX using local executable
                try:
                    crx2rnx_path = get_crx2rnx_path()
                    if not crx2rnx_path.exists():
                        print(f"Error: CRX2RNX not found at {crx2rnx_path}")
                        return
                        
                    result = subprocess.run(
                        [str(crx2rnx_path), str(crx_path)],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Converted to RNX: {rnx_path.name}")
                    
                    # Remove .crx file after successful conversion
                    crx_path.unlink()
                    
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {crx_path.name} to RNX: {e.stderr}")
                    
        except Exception as e:
            print(f"Error extracting/converting {file_path.name}: {e}")

    def reconnect(self) -> bool:
        """Attempts to reconnect to the FTP server."""
        max_reconnect_attempts = 3
        reconnect_delay = 5  # saniye
        
        for attempt in range(max_reconnect_attempts):
            try:
                print(f"Reconnection attempt {attempt + 1}/{max_reconnect_attempts}")
                self.close()  # Mevcut bağlantıyı kapat
                
                if self.connect():  # Yeniden bağlan
                    print("Successfully reconnected to FTP server")
                    return True
                    
                print(f"Reconnection failed, waiting {reconnect_delay} seconds before next attempt...")
                time.sleep(reconnect_delay)  # Yeniden denemeden önce bekle
                reconnect_delay *= 2  # Her başarısız denemede bekleme süresini iki katına çıkar
                
            except Exception as e:
                print(f"Reconnection error: {e}")
                
        print("All reconnection attempts failed")
        return False

def check_crx2rnx_availability() -> bool:
    """Checks if CRX2RNX is available for use."""
    if not check_crx2rnx():
        print("Error: CRX2RNX executable not found in package directory.")
        return False
    return True

def validate_range(value: str, min_val: int, max_val: int, name: str) -> List[str]:
    """Validates and formats range input (e.g., '1-5' or '1')."""
    if not value:
        return []
        
    try:
        # Check if it's a range (e.g., "1-5")
        if '-' in value:
            start, end = map(int, value.split('-'))
            if start > end:
                print(f"Invalid {name} range: start cannot be greater than end.")
                return []
        else:
            # Single value
            start = end = int(value)
            
        # Validate range
        if start < min_val or end > max_val:
            print(f"{name} must be between {min_val:02d}-{max_val:02d}.")
            return []
            
        # Generate list of values with leading zeros
        # Use 3 digits for DOY, 2 digits for others
        if name == "DOY":
            return [f"{i:03d}" for i in range(start, end + 1)]
        else:
            return [f"{i:02d}" for i in range(start, end + 1)]
        
    except ValueError:
        print(f"Invalid {name} format. Use single value or range (e.g., 1-5)")
        return []

def validate_hour(hour: str) -> List[str]:
    """Validates and formats hour input (e.g., '0-5' or '1')."""
    return validate_range(hour, 0, 23, "hour")

def validate_doy(doy: str) -> List[str]:
    """Validates and formats DOY input (e.g., '300-305' or '300')."""
    return validate_range(doy, 1, 366, "DOY")

def main():
    """Main CLI entry point."""
    # 1. User input
    station = input("Enter station name (e.g., BRST00FRA) or press Enter for ALL: ").strip()
    year = input("Enter year (e.g., 2024): ").strip()
    doy_input = input("Enter DOY (e.g., 001 or 001-030): ").strip()
    subfolder = input("Enter subfolder (e.g., 24d, 24o): ").strip()
    hour_input = input("Enter hour (e.g., 00 or 00-05) or press Enter for ALL: ").strip()
    
    # Ask for extraction preferences
    extract_files = input("Extract downloaded files? (y/N): ").strip().lower() == 'y'
    convert_to_rnx = False
    if extract_files:
        convert_to_rnx = input("Convert to RINEX (.rnx)? (y/N): ").strip().lower() == 'y'
        if convert_to_rnx and not check_crx2rnx_availability():
            print("RINEX conversion will be skipped.")
            convert_to_rnx = False
    
    # Validate DOY range
    doy_list = validate_doy(doy_input)
    if not doy_list:
        return
        
    # Validate hour range
    hour_list = validate_hour(hour_input) if hour_input else []
    if hour_input and not hour_list:  # Only fail if hour was provided but invalid
        return

    # Process each DOY
    doy_index = 0
    while doy_index < len(doy_list):
        doy = doy_list[doy_index]
        print(f"\nProcessing DOY: {doy}")
        
        # 3. Connect to FTP if needed
        client = CDDISFTPClient()
        if not client.connect():
            print("FTP connection failed. Waiting 30 seconds before retry...")
            time.sleep(30)
            continue

        try:
            # 4. Construct base path on FTP
            base_path = f"/gnss/data/highrate/{year}/{doy}/{subfolder}"

            # 5. List and validate available hours
            available_hours = client.list_hour_subfolders(base_path)
            if not available_hours:
                print(f"No hour subfolders found in {base_path}")
                doy_index += 1  # Move to next DOY
                continue

            # 6. Filter hours based on user input
            hour_folders = hour_list if hour_list else available_hours
            valid_hours = [h for h in hour_folders if h in available_hours]
            
            if not valid_hours:
                print(f"No valid hours found in available hours: {available_hours}")
                doy_index += 1  # Move to next DOY
                continue

            # 7. Prepare download directory
            station_folder = station if station else "ALLSTATIONS"
            download_dir = os.path.join("downloads", station_folder, year, doy)
            os.makedirs(download_dir, exist_ok=True)
            
            print(f"Processing hours: {valid_hours}")
            print(f"Files will be saved to: {download_dir}\n")

            # 8. Download files
            success = True
            for hour_subdir in valid_hours:
                try:
                    crx_files = client.list_crx_files(base_path, hour_subdir, 
                                                    station_filter=station if station else None)
                    if not crx_files:
                        print(f"No .crx.gz files found in {base_path}/{hour_subdir} "
                              f"(filter={station or 'None'})")
                        continue

                    local_hour_dir = os.path.join(download_dir, hour_subdir)
                    os.makedirs(local_hour_dir, exist_ok=True)

                    for file_name in crx_files:
                        local_path = os.path.join(local_hour_dir, file_name)
                        # Eğer .rnx dosyası zaten varsa, bu dosyayı atla
                        rnx_path = local_path.replace('.crx.gz', '.rnx')
                        if os.path.exists(rnx_path):
                            print(f"Skipping {file_name} - RINEX file already exists: {os.path.basename(rnx_path)}")
                            continue
                            
                        # Eğer .crx dosyası varsa, onu da kontrol et
                        crx_path = local_path.replace('.gz', '')
                        if os.path.exists(crx_path):
                            print(f"Skipping {file_name} - CRX file already exists: {os.path.basename(crx_path)}")
                            continue

                        if client.download_file(base_path, hour_subdir, file_name, local_path):
                            if extract_files:
                                client.extract_and_convert(local_path, convert_to_rnx)
                        else:
                            success = False
                            break

                except Exception as e:
                    print(f"Error processing hour {hour_subdir}: {e}")
                    success = False
                    break

            if success:
                doy_index += 1  # Move to next DOY only if current one was successful
            else:
                print(f"Errors occurred while processing DOY {doy}. Will retry after 30 seconds...")
                client.close()
                time.sleep(30)
                continue

        except Exception as e:
            print(f"Error processing DOY {doy}: {e}")
            client.close()
            time.sleep(30)
            continue
        
        finally:
            client.close()

    print("\nAll operations completed.")


if __name__ == "__main__":
    main() 