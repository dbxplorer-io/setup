# Password Encryption for dbxplorer Agent Inventory

This directory contains tools and instructions for encrypting database passwords for use in dbxplorer agent inventory/configuration files.

## Why Encrypt Passwords?
- Storing plain-text passwords in configuration files is insecure.
- Encrypting passwords protects them at rest and reduces the risk of accidental exposure.
- The agent will transparently decrypt passwords at runtime using a secure key.

## How It Works
- Passwords are encrypted using **AES-128-CBC** with a random IV (Initialization Vector).
- The encryption key is **never stored in the repo**. It must be provided via the `DB_PASSWORD_KEY` environment variable (16 characters, 128 bits).
- Encrypted passwords are stored in the format:
  
  `enc[<base64-iv>:<base64-ciphertext>]`

- The agent will automatically detect and decrypt passwords in this format.

## Usage

### 1. Set the Encryption Key
Export your 16-character key (must match the agent's runtime key):

```sh
export DB_PASSWORD_KEY='your16charsecret'
```

### 2. Encrypt a Password
Run the provided script:

```sh
python encrypt_password.py 'my_db_password'
```

**Output:**
```
enc[<base64-iv>:<base64-ciphertext>]
```

Copy this value into your inventory/config YAML:

```yaml
password: enc[...]
```

### 3. Agent Decryption
- The agent will read the password field.
- If it matches the `enc[...]` format, it will decrypt using the key from `DB_PASSWORD_KEY`.
- If not, it will use the value as plain text.

## Security Notes
- **Never commit your encryption key to version control.**
- Rotate keys periodically and restrict access.
- For production, consider using a secrets manager (Vault, AWS Secrets Manager, etc.) for key management.

## Requirements
- Python 3
- `pycryptodome` package (`pip install pycryptodome`)

## File List
- `encrypt_password.py` — Script to encrypt passwords for use in inventory files.

## Example

```sh
export DB_PASSWORD_KEY='my16charsecret!!'
python encrypt_password.py 'supersecretpassword'
# Output: enc[QkFTRTY0SVY=:QkFTRTY0Q0lQSEVSVEVYVA==]
```

Paste the output into your YAML:

```yaml
password: enc[QkFTRTY0SVY=:QkFTRTY0Q0lQSEVSVEVYVA==]
```

---

For questions or help, contact your dbxplorer administrator.
