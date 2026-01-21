import requests
import sys
import json
from datetime import datetime, timedelta

class FFArenaAPITester:
    def __init__(self, base_url="https://guildwars-ff.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.guild_id = None
        self.tournament_id = None
        self.challenge_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        if self.token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    'test': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'test': name,
                'error': str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"testuser{timestamp}@example.com",
            "password": "TestPass123!",
            "username": f"TestUser{timestamp}",
            "ign": f"TestIGN{timestamp}"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.token:
            print("⚠️  Skipping login test - no token from registration")
            return False
            
        # We'll use the same credentials from registration
        # In a real scenario, you'd test with known credentials
        return True

    def test_get_user_profile(self):
        """Test getting user profile"""
        if not self.token:
            print("⚠️  Skipping profile test - no token")
            return False
            
        return self.run_test("Get User Profile", "GET", "auth/me", 200)[0]

    def test_create_guild(self):
        """Test guild creation"""
        if not self.token:
            print("⚠️  Skipping guild creation - no token")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        guild_data = {
            "name": f"Test Guild {timestamp}",
            "tag": f"TG{timestamp[-3:]}",
            "description": "A test guild for API testing",
            "logo_url": "https://example.com/logo.png"
        }
        
        success, response = self.run_test(
            "Create Guild",
            "POST",
            "guilds",
            200,
            data=guild_data
        )
        
        if success and 'id' in response:
            self.guild_id = response['id']
            print(f"   Guild created with ID: {self.guild_id}")
            return True
        return False

    def test_get_guilds(self):
        """Test getting all guilds"""
        return self.run_test("Get All Guilds", "GET", "guilds", 200)[0]

    def test_get_guild_detail(self):
        """Test getting specific guild details"""
        if not self.guild_id:
            print("⚠️  Skipping guild detail test - no guild ID")
            return False
            
        return self.run_test("Get Guild Detail", "GET", f"guilds/{self.guild_id}", 200)[0]

    def test_create_tournament(self):
        """Test tournament creation"""
        if not self.token:
            print("⚠️  Skipping tournament creation - no token")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        start_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        tournament_data = {
            "name": f"Test Tournament {timestamp}",
            "description": "A test tournament for API testing",
            "format": "single_elimination",
            "max_teams": 8,
            "start_date": start_date,
            "entry_fee": 0,
            "prize_pool": 1000,
            "rules": "Standard Free Fire rules apply"
        }
        
        success, response = self.run_test(
            "Create Tournament",
            "POST",
            "tournaments",
            200,
            data=tournament_data
        )
        
        if success and 'id' in response:
            self.tournament_id = response['id']
            print(f"   Tournament created with ID: {self.tournament_id}")
            return True
        return False

    def test_get_tournaments(self):
        """Test getting all tournaments"""
        return self.run_test("Get All Tournaments", "GET", "tournaments", 200)[0]

    def test_get_tournament_detail(self):
        """Test getting specific tournament details"""
        if not self.tournament_id:
            print("⚠️  Skipping tournament detail test - no tournament ID")
            return False
            
        return self.run_test("Get Tournament Detail", "GET", f"tournaments/{self.tournament_id}", 200)[0]

    def test_register_tournament(self):
        """Test registering guild for tournament"""
        if not self.token or not self.tournament_id or not self.guild_id:
            print("⚠️  Skipping tournament registration - missing requirements")
            return False
            
        return self.run_test(
            "Register for Tournament",
            "POST",
            f"tournaments/{self.tournament_id}/register",
            200
        )[0]

    def test_create_gvg_challenge(self):
        """Test creating a GVG challenge"""
        if not self.token or not self.guild_id:
            print("⚠️  Skipping GVG challenge creation - missing requirements")
            return False
            
        # First, let's get another guild to challenge
        success, guilds_response = self.run_test("Get Guilds for Challenge", "GET", "guilds", 200)
        if not success or not guilds_response:
            print("⚠️  No guilds available to challenge")
            return False
            
        # Find a different guild to challenge
        target_guild = None
        for guild in guilds_response:
            if guild['id'] != self.guild_id:
                target_guild = guild
                break
                
        if not target_guild:
            print("⚠️  No other guilds available to challenge")
            return True  # Not a failure, just no targets
            
        challenge_data = {
            "defender_guild_id": target_guild['id'],
            "message": "Test challenge from API testing",
            "wager": 100
        }
        
        success, response = self.run_test(
            "Create GVG Challenge",
            "POST",
            "challenges",
            200,
            data=challenge_data
        )
        
        if success and 'id' in response:
            self.challenge_id = response['id']
            print(f"   Challenge created with ID: {self.challenge_id}")
            return True
        return False

    def test_get_challenges(self):
        """Test getting challenges"""
        if not self.token:
            print("⚠️  Skipping challenges test - no token")
            return False
            
        return self.run_test("Get Challenges", "GET", "challenges", 200)[0]

    def test_get_notifications(self):
        """Test getting user notifications"""
        if not self.token:
            print("⚠️  Skipping notifications test - no token")
            return False
            
        return self.run_test("Get Notifications", "GET", "notifications", 200)[0]

    def test_get_guild_leaderboard(self):
        """Test getting guild leaderboard"""
        return self.run_test("Get Guild Leaderboard", "GET", "leaderboard/guilds", 200)[0]

    def test_get_matches(self):
        """Test getting matches"""
        return self.run_test("Get Matches", "GET", "matches", 200)[0]

def main():
    print("🚀 Starting FF Arena API Tests")
    print("=" * 50)
    
    tester = FFArenaAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("User Registration", tester.test_user_registration),
        ("User Profile", tester.test_get_user_profile),
        ("Create Guild", tester.test_create_guild),
        ("Get All Guilds", tester.test_get_guilds),
        ("Get Guild Detail", tester.test_get_guild_detail),
        ("Create Tournament", tester.test_create_tournament),
        ("Get All Tournaments", tester.test_get_tournaments),
        ("Get Tournament Detail", tester.test_get_tournament_detail),
        ("Register for Tournament", tester.test_register_tournament),
        ("Create GVG Challenge", tester.test_create_gvg_challenge),
        ("Get Challenges", tester.test_get_challenges),
        ("Get Notifications", tester.test_get_notifications),
        ("Get Guild Leaderboard", tester.test_get_guild_leaderboard),
        ("Get Matches", tester.test_get_matches),
    ]
    
    print(f"Running {len(tests)} API tests...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            tester.failed_tests.append({
                'test': test_name,
                'error': str(e)
            })
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%" if tester.tests_run > 0 else "0%")
    
    if tester.failed_tests:
        print("\n❌ FAILED TESTS:")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"{i}. {failure['test']}")
            if 'error' in failure:
                print(f"   Error: {failure['error']}")
            else:
                print(f"   Expected: {failure['expected']}, Got: {failure['actual']}")
                print(f"   Response: {failure['response']}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())