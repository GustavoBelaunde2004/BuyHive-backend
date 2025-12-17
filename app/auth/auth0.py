import httpx
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from app.config.settings import settings
from app.functions.database import users_collection
from datetime import datetime


# Cache for Auth0 JWKS (JSON Web Key Set)
_jwks_cache: Optional[Dict] = None
_jwks_cache_time: Optional[datetime] = None


async def get_auth0_jwks() -> Dict:
    """
    Fetch Auth0's JSON Web Key Set (JWKS) for token verification.
    Caches the result to avoid repeated API calls.
    """
    global _jwks_cache, _jwks_cache_time
    
    # Cache for 1 hour
    if _jwks_cache and _jwks_cache_time:
        time_diff = (datetime.utcnow() - _jwks_cache_time).total_seconds()
        if time_diff < 3600:  # 1 hour
            return _jwks_cache
    
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        jwks = response.json()
    
    _jwks_cache = jwks
    _jwks_cache_time = datetime.utcnow()
    
    return jwks


def get_signing_key(token: str, jwks: Dict) -> Optional[Dict]:
    """
    Get the signing key from JWKS that matches the token's header.
    """
    try:
        import base64
        import json
        
        # Decode token header without verification
        parts = token.split('.')
        if len(parts) < 2:
            return None
        
        # Decode header
        header_data = base64.urlsafe_b64decode(parts[0] + '==')
        unverified_header = json.loads(header_data)
        
        rsa_key = {}
        
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            return None
        
        return rsa_key
    
    except Exception:
        return None


async def verify_auth0_token(token: str) -> Dict[str, Any]:
    """
    Verify an Auth0 JWT token.
    
    Args:
        token: JWT token from Auth0
    
    Returns:
        Decoded token payload
    
    Raises:
        JWTError: If token is invalid
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import base64
        
        # Get JWKS
        jwks = await get_auth0_jwks()
        
        # Get signing key
        signing_key = get_signing_key(token, jwks)
        
        if not signing_key:
            raise JWTError("Unable to find appropriate key")
        
        # Construct RSA public key from JWK using cryptography
        # Decode base64url encoded modulus (n) and exponent (e)
        def base64url_decode(data: str) -> bytes:
            # Add padding if needed for base64url
            padding = 4 - len(data) % 4
            if padding != 4:
                data += '=' * padding
            return base64.urlsafe_b64decode(data)
        
        n_bytes = base64url_decode(signing_key['n'])
        e_bytes = base64url_decode(signing_key['e'])
        
        # Convert bytes to integers
        n_int = int.from_bytes(n_bytes, 'big')
        e_int = int.from_bytes(e_bytes, 'big')
        
        # Construct RSA public key
        public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()
        
        # Serialize to PEM format for python-jose
        pem_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            pem_key,
            algorithms=[settings.AUTH0_ALGORITHMS],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
        )
        
        return payload
    
    except JWTError as e:
        raise JWTError(f"Invalid Auth0 token: {str(e)}")


async def get_or_create_user_from_token(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get user from database or create if doesn't exist, based on Auth0 token payload.
    
    Args:
        payload: Decoded Auth0 token payload
    
    Returns:
        User information dictionary
    
    Raises:
        ValueError: If no valid email found in token
    """
    import re
    
    # Extract user info from Auth0 token
    # Auth0 token typically has: sub (user ID), email, name, etc.
    user_id = payload.get("sub")  # Auth0 user ID (stable)
    email_raw = payload.get("email") or payload.get("https://your-namespace/email")
    name = payload.get("name") or payload.get("nickname", "Unknown")
    auth0_id = user_id

    if not user_id:
        raise ValueError("No user_id (sub) found in Auth0 token.")
    
    # Validate email format
    email = None
    if email_raw:
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email_raw):
            email = email_raw
    
    if not email:
        # No valid email found in token
        available_keys = list(payload.keys())
        raise ValueError(
            f"No valid email found in Auth0 token. "
            f"Token sub: {auth0_id}. "
            f"Available claims in token: {available_keys}. "
            f"Please ensure your Auth0 application requests the 'email' scope."
        )
    
    now = datetime.utcnow().isoformat()

    # Upsert user in users collection keyed by user_id (Auth0 sub)
    await users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "email": email,
                "name": name,
                "auth0_id": auth0_id,  # kept for compatibility
                "updated_at": now,
            },
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": now,
                "cart_count": 0,
                "cart_ids": [],
            },
        },
        upsert=True,
    )

    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "auth0_id": auth0_id,
    }

