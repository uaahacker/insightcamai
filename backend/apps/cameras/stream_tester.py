import logging
import subprocess
from django.conf import settings

logger = logging.getLogger(__name__)


class StreamConnectionTester:
    """Test camera stream connectivity"""
    
    TIMEOUT = 10  # seconds
    
    @staticmethod
    def test_rtsp_stream(host, port, username, password, stream_path, stream_protocol='rtsp'):
        """Test RTSP stream connection"""
        try:
            if username and password:
                url = f"{stream_protocol}://{username}:{password}@{host}:{port}{stream_path}"
            else:
                url = f"{stream_protocol}://{host}:{port}{stream_path}"
            
            # Use ffprobe to test stream
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                '-rtsp_transport', 'tcp',
                '-timeout', str(StreamConnectionTester.TIMEOUT * 1000000),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=StreamConnectionTester.TIMEOUT)
            
            if result.returncode == 0:
                return True, "Stream connection successful"
            else:
                error = result.stderr.decode()
                return False, f"Stream connection failed: {error}"
        
        except subprocess.TimeoutExpired:
            return False, "Connection timed out"
        except FileNotFoundError:
            return False, "ffprobe not found. Make sure FFmpeg is installed."
        except Exception as e:
            return False, f"Error testing stream: {str(e)}"
    
    @staticmethod
    def test_http_stream(host, port, stream_path, username=None, password=None):
        """Test HTTP/MJPEG stream connection"""
        import requests
        
        try:
            protocol = 'https' if port == 443 else 'http'
            if stream_path.startswith('http'):
                url = stream_path
            else:
                url = f"{protocol}://{host}:{port}{stream_path}"
            
            auth = (username, password) if username and password else None
            response = requests.head(url, auth=auth, timeout=StreamConnectionTester.TIMEOUT)
            
            if response.status_code < 400:
                return True, "HTTP stream connection successful"
            else:
                return False, f"HTTP error: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return False, "Connection timed out"
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to the host"
        except Exception as e:
            return False, f"Error testing stream: {str(e)}"
