# XML to CSV Data Extractor

Python script that parses the XML files created by the TEPC (Transcription of Estate Papers at the Cape of Good Hope) project to extract structured person and document data, then exports it as a CSV.

## Features
- Parses XML documents to extract structured data.
- Handles missing or malformed date fields.
- Associates individuals with their roles and relationships.
- Outputs a CSV file (`output.csv`) for further analysis.

## Requirements
- Python 3.x
- Required libraries:
  - `pandas`
  - `dateutil`
  - `xml.etree.ElementTree`

## Usage
1. Place your XML files inside the `source/` directory.
2. Run the script:
   ```sh
   python TEPC-XML-parser.py
   ```
3. The extracted data will be saved as `output.csv` in the script directory.

## File Structure
```
project-folder/
│-- script.py        # The main script
│-- source/          # Folder containing XML files
│   │-- file1.xml
│   │-- file2.xml
│-- output.csv       # Generated output file
```

## Output Format
The script generates a CSV with the following columns:

| Column | Description |
|--------|-------------|
| `Person_Observation_ID` | Unique ID assigned to each person |
| `Source` | Document reference |
| `Document date` | Standardized date of the document |
| `Person Name` | Name of the person |
| `Standardized Name` | Normalized version of the name |
| `Role` | Role of the person in the document |
| `Patronym` | Derived patronym (if applicable) |
| `Is this person unnamed?` | Boolean flag for unnamed individuals |
| `Enslaved By` | IDs of associated enslavers |

## Error Handling
- The script handles missing dates and replaces them with `None`.

## License
This script is released under the MIT License.

