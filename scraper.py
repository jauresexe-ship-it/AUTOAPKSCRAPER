import sys
import os
import json
import time
import random
import cloudscraper
from urllib.parse import urljoin, quote

class APKDownloader:
    def __init__(self):
        # ✅ cloudscraper يتعامل مع User-Agent تلقائياً - لا تضف User-Agent يدوياً!
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        # ✅ نضيف فقط Headers الضرورية بدون User-Agent
        self.scraper.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.base_url = 'https://apkpure.com'
    
    def random_delay(self, min_sec=0.1, max_sec=0.3):
        """تأخير عشوائي لتجنب الحظر"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def search_app(self, package_name):
        """البحث عن التطبيق باستخدام package name"""
        try:
            import re
            
            # محاولة URLs المباشرة أولاً (أسرع)
            app_name_slug = package_name.split('.')[-1]
            possible_urls = [
                f"{self.base_url}/{app_name_slug}/{package_name}",
                f"{self.base_url}/{app_name_slug}-app/{package_name}",
                f"{self.base_url}/ar/{app_name_slug}/{package_name}",  # Arabic version
            ]
            
            for url in possible_urls:
                self.random_delay(0.1, 0.2)
                
                try:
                    response = self.scraper.get(url, timeout=10)
                    
                    if response.status_code == 200 and package_name in response.text:
                        return url
                except:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def get_download_link(self, app_url):
        """الحصول على رابط التحميل المباشر"""
        try:
            download_page = f"{app_url}/download"
            
            self.random_delay(0.1, 0.3)
            response = self.scraper.get(download_page, timeout=15)
            
            if response.status_code != 200:
                return None
            
            import re
            
            # ✅ البحث عن XAPK أولاً (للألعاب مع OBB)
            patterns = [
                # XAPK patterns (أولوية أعلى)
                (r'href="(https://d\.apkpure\.com/b/XAPK/[^"]+)"', 'XAPK', True),
                (r'href="(https://download\.apkpure\.com/b/XAPK/[^"]+)"', 'XAPK', True),
                (r'data-dt-file="([^"]+\.xapk[^"]*)"', 'XAPK', True),
                
                # APK patterns (أولوية أقل)
                (r'href="(https://d\.apkpure\.com/b/APK/[^"]+)"', 'APK', False),
                (r'href="(https://download\.apkpure\.com/b/APK/[^"]+)"', 'APK', False),
                (r'data-dt-file="([^"]+\.apk[^"]*)"', 'APK', False),
                
                # Fallback patterns
                (r'data-dt-file="([^"]+)"', 'APK', False),
            ]
            
            for pattern, file_type, is_xapk in patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    download_url = match.group(1)
                    
                    # إصلاح الروابط النسبية
                    if not download_url.startswith('http'):
                        if download_url.startswith('//'):
                            download_url = 'https:' + download_url
                        else:
                            download_url = urljoin(self.base_url, download_url)
                    
                    return {
                        'url': download_url,
                        'is_xapk': is_xapk,
                        'type': file_type
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def get_download_info(self, package_name):
        """الحصول على معلومات التحميل الكاملة"""
        try:
            # البحث عن التطبيق
            app_url = self.search_app(package_name)
            
            if not app_url:
                return {
                    'error': 'App not found',
                    'success': False
                }
            
            # الحصول على رابط التحميل
            download_info = self.get_download_link(app_url)
            
            if not download_info:
                return {
                    'error': 'Download link not found',
                    'success': False
                }
            
            download_url = download_info.get('url', '')
            is_xapk = download_info.get('is_xapk', False)
            file_type = download_info.get('type', 'APK')
            
            # تحديد امتداد الملف
            ext = '.xapk' if is_xapk else '.apk'
            filename = f"{package_name}{ext}"
            
            result = {
                'success': True,
                'download_url': download_url,
                'filename': filename,
                'is_xapk': is_xapk,
                'file_type': file_type,
                'app_url': app_url
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

def main():
    try:
        if len(sys.argv) < 2:
            result = {
                'error': 'No package name provided',
                'success': False
            }
            print(json.dumps(result))
            sys.exit(1)
        
        package_name = sys.argv[1].strip()
        
        if not package_name:
            result = {
                'error': 'Package name is empty',
                'success': False
            }
            print(json.dumps(result))
            sys.exit(1)
        
        downloader = APKDownloader()
        result = downloader.get_download_info(package_name)
        
        # التأكد من أن النتيجة dictionary صالح
        if not isinstance(result, dict):
            result = {
                'error': 'Invalid response format',
                'success': False
            }
        
        # طباعة JSON صالح فقط
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            'error': f'Script error: {str(e)}',
            'success': False
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    main()