"""
Pinterest Crawler
Pinterest에서 이미지 URL을 크롤링하는 모듈
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class PinterestCrawler:
    """Pinterest 크롤러 (Selenium 기반)"""
    
    BASE_URL = "https://www.pinterest.com"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search(self, category: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        카테고리로 Pinterest 검색
        """
        images = []
        
        # 방법 1: Selenium을 사용한 동적 콘텐츠 크롤링
        print(f"   [Method 1] Selenium-based Pinterest crawling...")
        try:
            images = self._crawl_with_selenium(category, limit)
            if images:
                print(f"   Success: {len(images)} images collected (Method 1)")
                return images
        except Exception as e:
            print(f"   Failed: {e}")
        
        # 방법 2: API 역분석
        print(f"   [Method 2] Pinterest API reverse engineering...")
        try:
            images = self._crawl_with_api(category, limit)
            if images:
                print(f"   Success: {len(images)} images collected (Method 2)")
                return images
        except Exception as e:
            print(f"   Failed: {e}")
        
        # 방법 3: 정규식을 사용한 향상된 파싱
        print(f"   [Method 3] Advanced regex parsing...")
        try:
            images = self._crawl_with_advanced_parsing(category, limit)
            if images:
                print(f"   Success: {len(images)} images collected (Method 3)")
                return images
        except Exception as e:
            print(f"   Failed: {e}")
        
        print(f"   Failed: Unable to fetch images")
        return []
    
    def _crawl_with_selenium(self, category: str, limit: int) -> List[Dict[str, str]]:
        """Selenium을 사용한 Pinterest 크롤링"""
        images = []
        driver = None
        
        try:
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Pinterest 검색 페이지 열기
            encoded_category = urllib.parse.quote(category)
            search_url = f"{self.BASE_URL}/search/pins/?q={encoded_category}"
            print(f"   Request URL: {search_url}")
            
            driver.get(search_url)
            
            # 페이지 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
            )
            
            # 추가 스크롤로 더 많은 이미지 로드
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 3
            
            while scroll_count < max_scrolls and len(images) < limit * 2:
                # 스크롤
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # 새로운 높이 계산
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1
            
            # img 태그에서 이미지 URL 추출
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            print(f"   Found {len(img_elements)} img elements")
            
            seen_urls = set()
            
            for img in img_elements:
                if len(images) >= limit:
                    break
                
                try:
                    src = img.get_attribute("src")
                    srcset = img.get_attribute("srcset")
                    alt = img.get_attribute("alt")
                    
                    # pinimg.com에서 이미지 추출
                    image_url = None
                    if srcset:
                        urls = [u.strip().split()[0] for u in srcset.split(',')]
                        image_url = urls[-1] if urls else None
                    elif src and 'pinimg' in src:
                        image_url = src
                    
                    if image_url and image_url not in seen_urls and image_url.startswith('http'):
                        seen_urls.add(image_url)
                        images.append({
                            "url": image_url,
                            "external_id": f"pin_{len(images)}",
                            "title": alt or "Pinterest Image",
                            "description": ""
                        })
                except Exception as e:
                    print(f"   Error processing img: {e}")
                    continue
            
            return images
        
        except Exception as e:
            print(f"   Selenium error: {e}")
            return []
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _crawl_with_api(self, category: str, limit: int) -> List[Dict[str, str]]:
        """Pinterest 비공식 API를 사용한 크롤링"""
        images = []
        
        try:
            # Pinterest의 XHR 요청 시뮬레이션
            search_url = f"{self.BASE_URL}/api/v1/search/pins/"
            
            params = {
                "query": category,
                "scope": "pins",
                "rs": "filter",
                "page_size": limit * 2,
                "redux": "true"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.BASE_URL}/search/pins/?q={urllib.parse.quote(category)}",
            }
            
            print(f"   Request URL: {search_url}")
            
            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답에서 이미지 추출
            if "resource_response" in data:
                results = data["resource_response"].get("data", {}).get("results", [])
                
                for item in results[:limit]:
                    if isinstance(item, dict):
                        images_data = item.get("images", {})
                        
                        # 가장 큰 이미지 선택
                        image_url = None
                        for size_key in ["orig", "1200x", "600x"]:
                            if size_key in images_data:
                                image_url = images_data[size_key].get("url")
                                break
                        
                        if not image_url and images_data:
                            # 첫 번째 사용 가능한 이미지
                            for key, img_data in images_data.items():
                                if isinstance(img_data, dict) and "url" in img_data:
                                    image_url = img_data["url"]
                                    break
                        
                        if image_url:
                            images.append({
                                "url": image_url,
                                "external_id": str(item.get("id", len(images))),
                                "title": item.get("title", "Pinterest Image"),
                                "description": item.get("description", "")
                            })
            
            return images
        
        except Exception as e:
            print(f"   API error: {e}")
            return []
    
    def _crawl_with_advanced_parsing(self, category: str, limit: int) -> List[Dict[str, str]]:
        """향상된 정규식 파싱"""
        images = []
        
        try:
            encoded_category = urllib.parse.quote(category)
            search_url = f"{self.BASE_URL}/search/pins/?q={encoded_category}"
            
            print(f"   Request URL: {search_url}")
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            html = response.text
            print(f"   Response size: {len(html)} bytes")
            
            # JSON 데이터 추출 시도
            # Pinterest는 초기 렌더링에 JSON 데이터를 포함
            json_pattern = r'"images"\s*:\s*\{[^}]*"orig"\s*:\s*\{[^}]*"url"\s*:\s*"([^"]+)"'
            matches = re.findall(json_pattern, html)
            
            if matches:
                for url in matches[:limit]:
                    if url.startswith('http'):
                        images.append({
                            "url": url,
                            "external_id": f"pin_{len(images)}",
                            "title": "Pinterest Image",
                            "description": ""
                        })
            
            # 추가 패턴: pinimg URL 직접 추출
            if not images:
                pinimg_pattern = r'https://i\.pinimg\.com/[^\s"<>\)]+\.jpg'
                pinimg_matches = re.findall(pinimg_pattern, html)
                
                if pinimg_matches:
                    for url in pinimg_matches[:limit]:
                        images.append({
                            "url": url,
                            "external_id": f"pin_{len(images)}",
                            "title": "Pinterest Image",
                            "description": ""
                        })
            
            return images
        
        except Exception as e:
            print(f"   Parsing error: {e}")
            return []


class SimplePinterestClient:
    """
    간단한 Pinterest 클라이언트
    실제 Pinterest 데이터 또는 샘플 데이터 사용
    """
    
    def __init__(self):
        self.crawler = PinterestCrawler()
    
    def search_references(self, category: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        카테고리로 참고 이미지 검색
        """
        # 카테고리 정규화
        normalized_category = self._normalize_category(category)
        
        # 검색
        results = self.crawler.search(normalized_category, limit)
        
        return results
    
    @staticmethod
    def _normalize_category(category: str) -> str:
        """카테고리 정규화"""
        category_map = {
            "전신": "full body pose photography",
            "셀카": "selfie pose",
            "카페": "cafe photography pose",
            "야외": "outdoor photography pose",
            "실내": "indoor photography pose",
            "하이라이트": "highlight pose",
            "손": "hand pose",
            "얼굴": "face pose",
            "옆모습": "side profile pose",
            "뒷모습": "back pose"
        }
        return category_map.get(category, category)
