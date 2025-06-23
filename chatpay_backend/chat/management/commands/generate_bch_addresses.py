import os
import sys
import json
import subprocess
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat.models import CustomUser


class Command(BaseCommand):
    help = 'Generate BCH keys and addresses for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate address for specific user ID only'
        )

    def handle(self, *args, **options):
        # Create a temporary Node.js script to generate addresses
        script_content = '''
import BCHJS from '@psf/bitcoincashjs-lib';

const { ECPair } = BCHJS;

async function generateAddresses(usersData) {
    const results = [];

    for (const user of usersData) {
        try {
            const keypair = ECPair.makeRandom();
            
            // Use the correct method to get the public key
            const publicKeyBuffer = keypair.getPublicKeyBuffer();
            const publicKey = publicKeyBuffer.toString('hex');
            
            // Generate a regular BCH address (not contract-based)
            const address = keypair.getAddress();

            results.push({
                user_id: user.id,
                username: user.username,
                public_key: publicKey,
                address: address
            });

            console.log(`Generated address for ${user.username}: ${address}`);
        } catch (error) {
            console.error(`Error generating address for ${user.username}:`, error.message);
            results.push({
                user_id: user.id,
                username: user.username,
                public_key: null,
                address: null,
                error: error.message
            });
        }
    }

    console.log('RESULTS_START');
    console.log(JSON.stringify(results));
    console.log('RESULTS_END');
}

// Read users data from stdin
let data = '';
process.stdin.on('data', chunk => {
    data += chunk;
});

process.stdin.on('end', () => {
    const usersData = JSON.parse(data);
    generateAddresses(usersData);
});
'''
        
        # Write the script to a temporary file
        script_path = os.path.join(os.getcwd(), 'temp_generate_addresses.mjs')
        with open(script_path, 'w') as f:
            f.write(script_content)

        try:
            # Get users to process
            if options['user_id']:
                users = User.objects.filter(id=options['user_id'])
            else:
                users = User.objects.all()

            # Prepare user data for the Node.js script
            users_data = []
            for user in users:
                # Check if user already has a profile, create if not
                profile, created = CustomUser.objects.get_or_create(user=user)
                users_data.append({
                    'id': user.id,
                    'username': user.username
                })

            if not users_data:
                self.stdout.write(self.style.WARNING('No users found'))
                return

            # Run the Node.js script
            self.stdout.write('Generating BCH addresses...')
            
            # Pass users data to the script via stdin
            process = subprocess.Popen(
                ['node', script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=json.dumps(users_data))
            
            if stderr:
                self.stdout.write(self.style.WARNING(f'Script warnings: {stderr}'))
            
            # Extract results from stdout
            if 'RESULTS_START' in stdout and 'RESULTS_END' in stdout:
                start_idx = stdout.find('RESULTS_START') + len('RESULTS_START\n')
                end_idx = stdout.find('RESULTS_END')
                results_json = stdout[start_idx:end_idx].strip()
                
                try:
                    results = json.loads(results_json)
                    
                    # Update Django database
                    updated_count = 0
                    error_count = 0
                    
                    for result in results:
                        if result.get('error'):
                            self.stdout.write(
                                self.style.ERROR(f"Error for {result['username']}: {result['error']}")
                            )
                            error_count += 1
                            continue
                        
                        try:
                            profile = CustomUser.objects.get(user_id=result['user_id'])
                            profile.bch_pubkey = result['public_key']
                            profile.bch_address = result['address']
                            profile.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Updated {result['username']}: {result['address']}"
                                )
                            )
                            updated_count += 1
                        except CustomUser.DoesNotExist:
                            self.stdout.write(
                                self.style.ERROR(f"Profile not found for user {result['username']}")
                            )
                            error_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully updated {updated_count} users. '
                            f'Errors: {error_count}'
                        )
                    )
                    
                except json.JSONDecodeError as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to parse results: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('Script did not return expected results format')
                )
                self.stdout.write(f'Script output: {stdout}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running address generation: {e}')
            )
        finally:
            # Clean up temporary script
            if os.path.exists(script_path):
                os.unlink(script_path) 