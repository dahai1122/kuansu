#!/usr/bin/env python3
"""
 GitHub Trending 爬蟲
 功能：獲取 GitHub 今日 Trending 排名
"""

import requests
from datetime import datetime
import json
import sys

def fetch_github_trending(language='', since='daily'):
    """
    獲取 GitHub Trending 倉庫列表
    
    Args:
        language: 程式語言 (如 'python', 'javascript', '' 表示全部)
        since: 時間範圍 ('daily', 'weekly', 'monthly')
    
    Returns:
        list: Trending 倉庫信息
    """
    
    url = 'https://github.com/trending'
    params = {'since': since}
    
    if language:
        params['spoken_language_code'] = language
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 使用正則表達式或 BeautifulSoup 解析
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        trending_repos = []
        
        # 查找倉庫容器
        repo_elements = soup.find_all('article', class_='Box-row')
        
        for idx, repo in enumerate(repo_elements[:30], 1):  # 取前 30 個
            try:
                # 倉庫名稱和 URL
                repo_link = repo.find('h2', class_='h3').find('a')
                repo_name = repo_link.get_text(strip=True)
                repo_url = 'https://github.com' + repo_link.get('href')
                
                # 描述
                desc_elem = repo.find('p', class_='col-9')
                description = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
                
                # 語言
                lang_elem = repo.find('span', itemprop='programmingLanguage')
                language_info = lang_elem.get_text(strip=True) if lang_elem else 'N/A'
                
                # Stars
                stars_elem = repo.find('svg', class_='octicon-star')
                stars = 'N/A'
                if stars_elem:
                    stars_text = stars_elem.parent.get_text(strip=True)
                    stars = stars_text.split()[0] if stars_text else 'N/A'
                
                trending_repos.append({
                    'rank': idx,
                    'name': repo_name,
                    'url': repo_url,
                    'description': description,
                    'language': language_info,
                    'stars': stars
                })
            except Exception as e:
                print(f"解析倉庫出錯: {e}", file=sys.stderr)
                continue
        
        return trending_repos
    
    except requests.exceptions.RequestException as e:
        print(f"請求失敗: {e}", file=sys.stderr)
        return None

def main():
    print("🚀 GitHub Trending Fetcher")
    print(f"📅 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # 獲取全部語言的 Trending
    trending = fetch_github_trending(language='', since='daily')
    
    if trending:
        print(f"\n✅ 成功獲取 {len(trending)} 個倉庫:\n")
        
        for repo in trending:
            print(f"#{repo['rank']} {repo['name']}")
            print(f"   🔗 {repo['url']}")
            print(f"   📝 {repo['description'][:80]}..." if len(repo['description']) > 80 else f"   📝 {repo['description']}")
            print(f"   💻 {repo['language']} | ⭐ {repo['stars']}")
            print()
        
        # 保存為 JSON
        output_file = 'trending_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': trending
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ 數據已保存到 {output_file}")
    else:
        print("❌ 獲取失敗")
        sys.exit(1)

if __name__ == '__main__':
    main()
