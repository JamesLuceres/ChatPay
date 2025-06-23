import os
import json
import subprocess
import tempfile
from .models import CustomUser


def generate_bch_address_for_user(user):
    """
    Generate a BCH address for a specific user.
    Returns a tuple of (public_key, address) or (None, None) if failed.
    """
    # Create a temporary Node.js script to generate address for one user
    script_content = '''
import BCHJS from '@psf/bitcoincashjs-lib';

const { ECPair } = BCHJS;

async function generateAddress(userData) {
    try {
        const keypair = ECPair.makeRandom();
        const publicKeyBuffer = keypair.getPublicKeyBuffer();
        const publicKey = publicKeyBuffer.toString('hex');
        
        // Generate a regular BCH address (not contract-based)
        const address = keypair.getAddress();

        console.log('SUCCESS');
        console.log(JSON.stringify({
            user_id: userData.id,
            username: userData.username,
            public_key: publicKey,
            address: address
        }));
    } catch (error) {
        console.log('ERROR');
        console.log(error.message);
    }
}

// Read user data from stdin
let data = '';
process.stdin.on('data', chunk => {
    data += chunk;
});

process.stdin.on('end', () => {
    const userData = JSON.parse(data);
    generateAddress(userData);
});
'''
    
    # Write the script to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(script_content)
        script_path = f.name

    try:
        # Prepare user data for the Node.js script
        user_data = {
            'id': user.id,
            'username': user.username
        }

        # Run the Node.js script
        process = subprocess.Popen(
            ['node', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(user_data))
        
        if stderr:
            print(f"Script warnings: {stderr}")
        
        # Parse the result
        lines = stdout.strip().split('\n')
        if len(lines) >= 2 and lines[0] == 'SUCCESS':
            result = json.loads(lines[1])
            return result['public_key'], result['address']
        else:
            print(f"Script failed: {stdout}")
            return None, None
            
    except Exception as e:
        print(f"Error running address generation: {e}")
        return None, None
    finally:
        # Clean up temporary script
        if os.path.exists(script_path):
            os.unlink(script_path)


def ensure_user_has_bch_address(user):
    """
    Ensure a user has a BCH address. If they don't have one, generate it.
    Returns True if successful, False otherwise.
    """
    try:
        profile, created = CustomUser.objects.get_or_create(user=user)
        
        # If user already has a BCH address, return True
        if profile.bch_address:
            return True
        
        # Generate new BCH address
        public_key, address = generate_bch_address_for_user(user)
        
        if public_key and address:
            profile.bch_pubkey = public_key
            profile.bch_address = address
            profile.save()
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error ensuring BCH address for user {user.username}: {e}")
        return False 