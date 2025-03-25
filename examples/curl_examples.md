# API Usage Examples

## Upload Email File

Using curl to upload an .eml file to the API endpoint:

```bash
curl -X POST \
  http://localhost:8000/process-email \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/email.eml"
```

Note: Replace `/path/to/your/email.eml` with the actual path to your .eml file.

Examples:
- Windows: `"file=@C:/Users/username/email.eml"`
- Linux/Mac: `"file=@/home/username/email.eml"`
```
