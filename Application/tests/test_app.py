import unittest
import json
import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add root directory to path to import src (via app)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app

class TestStringMatchingAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_datasets(self):
        response = self.app.get('/api/datasets')
        data = json.loads(response.data)
        self.assertIn('datasets', data)
        self.assertIn('sample_dna', data['datasets'])

    def test_search_operation(self):
        # Load sample DNA
        self.app.post('/api/dataset', json={'name': 'sample_dna'})
        
        # Search for 'GATC'
        response = self.app.post('/api/operation', json={
            'type': 'search',
            'algorithm': 'Finite Automata',
            'pattern': 'GATC'
        })
        data = json.loads(response.data)
        
        self.assertIn('matches', data)
        self.assertGreater(data['match_count'], 0)
        self.assertIn('time_taken', data)

    def test_delete_operation(self):
        # Set a small known text
        self.app.post('/api/upload', data={
            'file': (b'Hello World Hello', 'test.txt')
        }, content_type='multipart/form-data')
        
        # Delete 'Hello'
        response = self.app.post('/api/operation', json={
            'type': 'delete',
            'algorithm': 'Z-Algorithm',
            'pattern': 'Hello'
        })
        data = json.loads(response.data)
        
        self.assertEqual(data['updated_text'].strip(), 'World')

    def test_insert_operation(self):
        # Set a small known text
        self.app.post('/api/upload', data={
            'file': (b'Hello World', 'test.txt')
        }, content_type='multipart/form-data')
        
        # Insert ' Beautiful' after 'Hello'
        response = self.app.post('/api/operation', json={
            'type': 'insert',
            'algorithm': 'Finite Automata',
            'pattern': 'Hello',
            'insert_text': ' Beautiful'
        })
        data = json.loads(response.data)
        
        self.assertEqual(data['updated_text'], 'Hello Beautiful World')

if __name__ == '__main__':
    unittest.main()
