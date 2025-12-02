#!/usr/bin/env python3
"""
LifeTap RSA Key Generator

Generates RSA key pair for WhatsApp Flow encryption/decryption.

Usage:
    python generate_keys.py
    python generate_keys.py --output-dir ./keys
    python generate_keys.py --no-passphrase
    python generate_keys.py --key-size 4096
"""

import os
import sys
import argparse
import secrets
import string
import base64
from pathlib import Path

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography package not installed.")
    print("Install with: pip install cryptography")
    sys.exit(1)


def generate_passphrase(length: int = 32) -> str:
    """Generate a secure random passphrase."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_rsa_keys(
    key_size: int = 2048,
    passphrase: str = None
) -> tuple[bytes, bytes]:
    """
    Generate RSA key pair.

    Args:
        key_size: RSA key size (2048 or 4096 recommended)
        passphrase: Optional passphrase to encrypt private key

    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    # Serialize private key
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase.encode())
    else:
        encryption = serialization.NoEncryption()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )

    # Extract and serialize public key
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem


def save_keys(
    output_dir: Path,
    private_key_pem: bytes,
    public_key_pem: bytes,
    passphrase: str = None
) -> dict:
    """
    Save keys to files and generate env var format.

    Returns:
        Dict with file paths and base64 encoded key
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    private_key_path = output_dir / "private.pem"
    public_key_path = output_dir / "public.pem"
    passphrase_path = output_dir / "passphrase.txt"
    env_path = output_dir / "env_vars.txt"

    # Save private key
    with open(private_key_path, 'wb') as f:
        f.write(private_key_pem)
    os.chmod(private_key_path, 0o600)  # Restrict permissions

    # Save public key
    with open(public_key_path, 'wb') as f:
        f.write(public_key_pem)

    # Save passphrase if provided
    if passphrase:
        with open(passphrase_path, 'w') as f:
            f.write(passphrase)
        os.chmod(passphrase_path, 0o600)

    # Generate base64 encoded private key for env var
    private_key_base64 = base64.b64encode(private_key_pem).decode('utf-8')

    # Save env vars format
    with open(env_path, 'w') as f:
        f.write("# WhatsApp Flow Encryption Environment Variables\n")
        f.write("# Add these to your Coolify or .env file\n\n")
        f.write(f"WHATSAPP_PRIVATE_KEY={private_key_base64}\n")
        if passphrase:
            f.write(f"WHATSAPP_PRIVATE_KEY_PASSWORD={passphrase}\n")
        f.write("\n# Or use file path (for local development):\n")
        f.write(f"# WHATSAPP_PRIVATE_KEY_PATH={private_key_path.absolute()}\n")
    os.chmod(env_path, 0o600)

    return {
        'private_key_path': private_key_path,
        'public_key_path': public_key_path,
        'passphrase_path': passphrase_path if passphrase else None,
        'env_path': env_path,
        'private_key_base64': private_key_base64
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate RSA keys for WhatsApp Flow encryption"
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path('./keys'),
        help='Output directory for keys (default: ./keys)'
    )
    parser.add_argument(
        '--key-size', '-s',
        type=int,
        default=2048,
        choices=[2048, 4096],
        help='RSA key size (default: 2048)'
    )
    parser.add_argument(
        '--no-passphrase',
        action='store_true',
        help='Generate keys without passphrase encryption'
    )
    parser.add_argument(
        '--passphrase', '-p',
        type=str,
        help='Use specific passphrase (default: auto-generate)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("LifeTap WhatsApp Flow Key Generator")
    print("=" * 60)
    print()

    # Generate or use provided passphrase
    if args.no_passphrase:
        passphrase = None
        print("⚠️  Generating keys WITHOUT passphrase protection")
    elif args.passphrase:
        passphrase = args.passphrase
        print("🔐 Using provided passphrase")
    else:
        passphrase = generate_passphrase()
        print("🔐 Generated secure passphrase")

    print(f"📏 Key size: {args.key_size} bits")
    print()

    # Generate keys
    print("🔑 Generating RSA key pair...")
    private_key_pem, public_key_pem = generate_rsa_keys(
        key_size=args.key_size,
        passphrase=passphrase
    )
    print("✅ Keys generated successfully")
    print()

    # Save keys
    print(f"💾 Saving to {args.output_dir.absolute()}...")
    result = save_keys(
        output_dir=args.output_dir,
        private_key_pem=private_key_pem,
        public_key_pem=public_key_pem,
        passphrase=passphrase
    )
    print("✅ Keys saved successfully")
    print()

    # Print summary
    print("=" * 60)
    print("📁 Generated Files:")
    print("=" * 60)
    print(f"  Private Key: {result['private_key_path']}")
    print(f"  Public Key:  {result['public_key_path']}")
    if result['passphrase_path']:
        print(f"  Passphrase:  {result['passphrase_path']}")
    print(f"  Env Vars:    {result['env_path']}")
    print()

    if passphrase:
        print("=" * 60)
        print("🔐 Passphrase (SAVE THIS SECURELY):")
        print("=" * 60)
        print(f"  {passphrase}")
        print()

    print("=" * 60)
    print("📋 Public Key (Upload to WhatsApp):")
    print("=" * 60)
    print(public_key_pem.decode('utf-8'))

    print("=" * 60)
    print("🌐 For Coolify (Environment Variables):")
    print("=" * 60)
    print()
    print("WHATSAPP_PRIVATE_KEY=")
    # Print first 50 chars + ... for preview
    preview = result['private_key_base64'][:80] + "..."
    print(f"  {preview}")
    print()
    print(f"  (Full value saved to {result['env_path']})")
    if passphrase:
        print()
        print(f"WHATSAPP_PRIVATE_KEY_PASSWORD={passphrase}")
    print()

    print("=" * 60)
    print("📝 Next Steps:")
    print("=" * 60)
    print("1. Upload public key to WhatsApp Business API:")
    print("   curl -X POST \\")
    print('     "https://graph.facebook.com/v18.0/{BUSINESS_ID}/whatsapp_business_encryption" \\')
    print('     -H "Authorization: Bearer {ACCESS_TOKEN}" \\')
    print('     -H "Content-Type: application/json" \\')
    print("     -d '{\"business_public_key\": \"<contents of public.pem>\"}'")
    print()
    print("2. Add environment variables to Coolify or .env file")
    print()
    print("3. Keep private key and passphrase SECURE - never commit to git!")
    print()
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
