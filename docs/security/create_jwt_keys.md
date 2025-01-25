# Generating JWT Keys for the Application

This guide provides step-by-step instructions for generating RSA keys for JWT signing and verification. These keys are essential for ensuring secure authentication and communication in your application.

## Prerequisites

- OpenSSH installed on your system.
- Access to the application’s `.env` file to set the paths and passphrase.

## Steps to Generate the Keys

### 1. Create a Directory for the Keys

Create a `.keys` directory in the root of your project to store the keys securely.

```bash
mkdir -p .keys
```

Ensure the directory has restricted permissions to prevent unauthorized access:

```bash
chmod 700 .keys
```

### 2. Generate the Private Key

Run the following command to generate a private RSA key with a passphrase:

```bash
ssh-keygen -t rsa -b 2048 -f .keys/private.pem -m PEM -N "your-strong-passphrase"
```

Replace `your-strong-passphrase` with a secure passphrase. This key will be used for signing JWTs.

### 3. Generate the Public Key

The public key will be automatically generated as `.keys/private.pem.pub` when creating the private key. Ensure both files exist:

```bash
ls -l .keys/
```

You should see `private.pem` and `private.pem.pub`.

### 4. Verify the Generated Keys

To check the details of the private key:

```bash
openssl rsa -in .keys/private.pem -passin pass:your-strong-passphrase -text -noout
```

To verify the public key:

```bash
openssl rsa -pubin -in .keys/private.pem.pub -text -noout
```

### 5. Update the .env File

Add the following configurations to your `.env` file:

```env
JWT_PRIVATE_KEY_PATH=".keys/private.pem"
JWT_PUBLIC_KEY_PATH=".keys/private.pem.pub"
JWT_KEYS_PASSPHRASE="your-strong-passphrase"
```

Ensure the passphrase matches the one used during key generation.

### 6. Secure the Keys

- Ensure the `.keys` directory and its contents are not included in version control. Add the following line to your `.gitignore` file:

```gitignore
.keys/
```

- Restrict access to the `**/.keys/**` directory:

```bash
chmod 600 .keys/private.pem .keys/private.pem.pub
```

### 7. Test the Application

Start your application and verify that the keys are loaded correctly. Check for any errors related to key loading or JWT signing/verification.

---

For more details on JWT security best practices, refer to the [JWT Handbook](https://jwt.io/introduction/).
