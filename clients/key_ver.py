import gnupg

# Initialize the GnuPG interface
gpg = gnupg.GPG()

# Assuming you have the public key and the signed message in the following variables
public_key = """
-----BEGIN PGP SIGNATURE-----

iJAEARYKADgWIQTDZo8dTC/1ilLtuI7WSsTvFWOmTgUCY/v5fBoaaHR0cHM6Ly93
b3dhbmEubWUvcGdwLnhodAAKCRDWSsTvFWOmTu93AP9qmBzs/bzBecKx4u4MqLNL
RUPzNxklHJfFg1nHnqmuvgEAtDZ14bLEo2agZb3WwVxumBigTwG56W3ti19a/tsx
aAE=
=t8hv
-----END PGP SIGNATURE-----
"""

signed_message = """
The original message that was signed.
"""

signature = """
-----BEGIN PGP SIGNATURE-----

iJAEARYKADgWIQTDZo8dTC/1ilLtuI7WSsTvFWOmTgUCY/v5fBoaaHR0cHM6Ly93
b3dhbmEubWUvcGdwLnhodAAKCRDWSsTvFWOmTu93AP9qmBzs/bzBecKx4u4MqLNL
RUPzNxklHJfFg1nHnqmuvgEAtDZ14bLEo2agZb3WwVxumBigTwG56W3ti19a/tsx
aAE=
=t8hv
-----END PGP SIGNATURE-----
"""

# Import the public key
import_result = gpg.import_keys(public_key)

# Verify the signature
verified = gpg.verify_data(signature, signed_message)

print(verified.valid)  # Will be True if the signature is valid
print(verified.status)  # Will give more info about the verification
