import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from flask import Flask, template_rendered
from contextlib import contextmanager

# Import the web interface module
try:
    from web_interface import app, db_manager
except ImportError:
    # Fallback for testing structure
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from web_interface import app, db_manager

@contextmanager
def captured_templates(app):
    """Capture templates rendered during request."""
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class TestWebInterface(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and disable CSRF for testing."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create a temporary database for testing
        self.db_fd, self.app.config['DATABASE'] = tempfile.mkstemp()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.app.config['DATABASE']
        
        # Mock the db_manager to use test database
        self.original_get_stats = db_manager.get_stats
        self.original_get_recent_moves = db_manager.get_recent_moves
        
    def tearDown(self):
        """Clean up after tests."""
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])
        db_manager.get_stats = self.original_get_stats
        db_manager.get_recent_moves = self.original_get_recent_moves
    
    def test_index_route(self):
        """Test that index route returns 200 and renders template."""
        with captured_templates(self.app) as templates:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'index.html')
            self.assertIn('stats', context)
            self.assertIn('recent_moves', context)
    
    def test_stats_route(self):
        """Test that stats route returns 200 and renders template."""
        # Mock the database response
        mock_stats = {
            'total_files': 100,
            'by_category': {'Images': 30, 'Documents': 20},
            'by_extension': {'.jpg': 25, '.pdf': 15}
        }
        db_manager.get_stats = MagicMock(return_value=mock_stats)
        
        with captured_templates(self.app) as templates:
            response = self.client.get('/stats')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'stats.html')
            self.assertEqual(context['stats'], mock_stats)
    
    def test_history_route(self):
        """Test that history route returns 200 and renders template."""
        # Mock the database response
        mock_history = [
            {'id': 1, 'filename': 'test.jpg', 'category': 'Images', 'timestamp': '2023-01-01 12:00:00'},
            {'id': 2, 'filename': 'doc.pdf', 'category': 'Documents', 'timestamp': '2023-01-01 11:00:00'}
        ]
        db_manager.get_recent_moves = MagicMock(return_value=mock_history)
        
        with captured_templates(self.app) as templates:
            response = self.client.get('/history')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'history.html')
            self.assertEqual(context['history'], mock_history)
    
    def test_api_stats_route(self):
        """Test that API stats route returns JSON data."""
        # Mock the database response
        mock_stats = {
            'total_files': 100,
            'by_category': {'Images': 30, 'Documents': 20},
            'by_extension': {'.jpg': 25, '.pdf': 15}
        }
        db_manager.get_stats = MagicMock(return_value=mock_stats)
        
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_stats)
    
    def test_api_history_route(self):
        """Test that API history route returns JSON data."""
        # Mock the database response
        mock_history = [
            {'id': 1, 'filename': 'test.jpg', 'category': 'Images', 'timestamp': '2023-01-01 12:00:00'},
            {'id': 2, 'filename': 'doc.pdf', 'category': 'Documents', 'timestamp': '2023-01-01 11:00:00'}
        ]
        db_manager.get_recent_moves = MagicMock(return_value=mock_history)
        
        response = self.client.get('/api/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_history)
    
    def test_api_history_with_limit(self):
        """Test that API history route respects limit parameter."""
        # Mock the database response
        mock_history = [
            {'id': 1, 'filename': 'test.jpg', 'category': 'Images', 'timestamp': '2023-01-01 12:00:00'}
        ]
        db_manager.get_recent_moves = MagicMock(return_value=mock_history)
        
        response = self.client.get('/api/history?limit=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        db_manager.get_recent_moves.assert_called_with(limit=1)
    
    def test_404_error(self):
        """Test that non-existent routes return 404."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_static_files(self):
        """Test that static files are served."""
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'css', response.data)
    
    @patch('web_interface.db_manager.get_stats')
    def test_index_with_mocked_db(self, mock_get_stats):
        """Test index route with mocked database calls."""
        mock_stats = {
            'total_files': 50,
            'by_category': {'Videos': 10, 'Music': 5},
            'by_extension': {'.mp4': 8, '.mp3': 5}
        }
        mock_history = [
            {'id': 1, 'filename': 'video.mp4', 'category': 'Videos', 'timestamp': '2023-01-01 10:00:00'}
        ]
        
        mock_get_stats.return_value = mock_stats
        db_manager.get_recent_moves = MagicMock(return_value=mock_history)
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Verify mocks were called
        mock_get_stats.assert_called_once()
        db_manager.get_recent_moves.assert_called_once()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'OK')

if __name__ == '__main__':
    unittest.main()