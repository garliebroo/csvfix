# csvfix

A JavaScript utility to detect and repair common encoding and formatting issues in CSV files.

## Installation

```bash
npm install csvfix
```

## Usage

```javascript
const csvfix = require('csvfix');

// Fix encoding and formatting issues in a CSV file
csvfix.fix('input.csv', 'output.csv')
  .then(() => console.log('CSV repaired successfully'))
  .catch(err => console.error(err));
```

You can also use it from the command line:

```bash
npx csvfix input.csv output.csv
```

### Options

```javascript
csvfix.fix('input.csv', 'output.csv', {
  encoding: 'utf-8',     // Target encoding (default: utf-8)
  delimiter: ',',        // Column delimiter (default: ,)
  fixQuotes: true,       // Repair mismatched quotes
  trimWhitespace: true   // Strip leading/trailing whitespace
});
```

## Features

- Detects and converts common encoding issues (Latin-1, Windows-1252, UTF-8 BOM)
- Repairs mismatched or unescaped quotes
- Normalizes line endings (CRLF, LF, CR)
- Fixes inconsistent delimiters
- Removes null bytes and non-printable characters

## License

MIT © csvfix contributors