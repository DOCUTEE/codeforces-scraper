import cloudscraper
from bs4 import BeautifulSoup
import json
from system_helper import read_file,append_to_jsonl,split_config_for_concurrent
import re
import threading
from problemset import CodeforcesAPI
import traceback
import os
import time
import random

def get_submission_ids(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    # Tìm tất cả các thẻ <script> trong HTML
    scripts = soup.find_all('script')

    # Biểu thức chính quy để trích xuất viewableSubmissionIds
    viewable_submission_ids = []

    # Duyệt qua tất cả các thẻ <script>
    for script in scripts:
        script_content = script.string  # Lấy nội dung của thẻ <script>
        
        if script_content and 'viewableSubmissionIds' in script_content:
            # Sử dụng regex để tìm và trích xuất viewableSubmissionIds
            match = re.search(r'const\s+viewableSubmissionIds\s*=\s*(\[[^\]]*\]);', script_content)
            if match:
                # Chuyển chuỗi JSON thành đối tượng Python (mảng)
                viewable_submission_ids = json.loads(match.group(1))
                break  # Dừng lại khi đã tìm thấy
    return viewable_submission_ids

def get_solution_ids(scraper, problem, headers, cookies, csrf_token, number_of_solutions=5):
    url = f'https://codeforces.com/contest/{problem["contestId"]}/status/{problem["index"]}'
    data = {
        "csrf_token": csrf_token,  # csrf_token từ form
        "action": "setupSubmissionFilter",
        "frameProblemIndex": problem["index"],
        "verdictName": "OK",
        "programTypeForInvoker": "cpp.g++17",
        "comparisonType": "NOT_USED",
        "judgedTestCount": "",
        "participantSubstring": "",
        "_tta": "284"
    }
    response = scraper.post(url, headers=headers, cookies=cookies, data=data)
    time.sleep(random.uniform(15, 30))  # Thêm độ trễ để tránh bị chặn
    c17_ids = get_submission_ids(response.text)
    c17_ids = [{"id": id , "programType": "cpp.g++17"} for id in c17_ids]
    return c17_ids[:number_of_solutions]
    

def get_solution_detail(scraper, problem_url, solution_id, headers, cookies, csrf_token):
    base_url = "https://codeforces.com/data/submitSource"
    headers_with_referer = headers.copy()
    headers_with_referer['Referer'] = problem_url
    data = {
        "submissionId": solution_id,
        "csrf_token": csrf_token
    }
    response = scraper.post(base_url, headers=headers_with_referer, cookies=cookies, data=data)
    time.sleep(random.uniform(15, 20))  # Thêm độ trễ để tránh bị chặn
    code = json.loads(response.text).get('source', 'Unknown')
    return code

def run(thread_idx, problems, headers, cookies, csrf_token):
    scraper = cloudscraper.create_scraper()
    for problem in problems:
        try:
            problem_data = {
                'raw': problem,
                'statement': '',
                'solutions': [],
                "solutions_ids": []
            }
            url = f"https://codeforces.com/contest/{problem['contestId']}/problem/{problem['index']}"
            print(f"Thread {thread_idx} processing problem {problem['contestId']}{problem['index']} at {url}")
            response = scraper.get(url, headers=headers, cookies=cookies)
            # time.sleep(random.uniform(1,2))  # Thêm độ trễ để tránh bị chặn
            soup = BeautifulSoup(response.text, 'html.parser')
            problem_statement = soup.find('div', class_='problem-statement')
            # print(problem_statement)
            # problem_data['statement'] = str(problem_statement)
            solution_ids = get_solution_ids(scraper, problem, headers, cookies, csrf_token)
            problem_data['solutions_ids'] = solution_ids.copy()
            
            for solution in solution_ids:
                solution_detail = get_solution_detail(scraper, url, solution['id'], headers, cookies, csrf_token)
                solution['code'] = solution_detail
                problem_data['solutions'].append(solution)
            if problem_data['solutions']:
                print(f"Thread {thread_idx} processed problem {problem['contestId']}{problem['index']}")
                print(f"Statement length: {len(problem_data['statement'])}")
                print(f"Number of solutions: {len(problem_data['solutions'])}")
                append_to_jsonl('problems_statements_uncode.jsonl', problem_data)
            else:
                print(f"Thread {thread_idx} found no solutions for problem {problem['contestId']}{problem['index']}")
        except Exception as e:
            print(f"Thread {thread_idx} failed to process problem {problem['contestId']}{problem['index']}: {e}")
            print(traceback.format_exc())
        finally:
            time.sleep(random.uniform(15, 30))  # Thêm độ trễ để tránh bị chặn
            pass

def get_unextracted_problems(problems, output_file):
    try:
        problems_done = read_file(output_file, file_extension='jsonl')
        problems_done_set = set(str(p['raw']['contestId']) + p['raw']['index'] for p in problems_done)
        unextracted_problems = [p for p in problems if (str(p['contestId']) + p['index']) not in problems_done_set]
        print("Unextracted problems:")
        print(unextracted_problems)

    except FileNotFoundError:
        unextracted_problems = problems
    return unextracted_problems

def scale_fit_threads(items, number_of_threads=8):
    result = []
    n = len(items)
    for i in range(number_of_threads):
        if type(items[i % n]) != str:
            result.append(items[i % n].copy())
        else:
            result.append(items[i % n])
    return result

def run_with_retries(num_threads, problems, headers_list, cookies_list, csrf_token_list, max_retries=1000):
    problems = get_unextracted_problems(problems, 'problems_statements_uncode.jsonl')
    num_threads = min(num_threads, len(problems))
    batches = split_config_for_concurrent(num_threads, problems)
    for attempt in range(max_retries):
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=run, args=(i, batches[i], headers_list[i], cookies_list[i], csrf_token_list[i]))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        problems = get_unextracted_problems(problems, 'problems_statements_uncode.jsonl')
        if not problems:
            print("All problems processed successfully.")
            break
        else:
            print(f"Retrying {len(problems)} unprocessed problems (Attempt {attempt + 2}/{max_retries})...")
    else:
        print("Some problems could not be processed after maximum retries.")

def filter_problem_by_rating(problems, min_rating=0, max_rating=10000):
    filtered_problems = []
    for problem in problems:
        rating = problem.get('rating', -1)
        if min_rating <= rating <= max_rating:
            filtered_problems.append(problem)
    return filtered_problems

if __name__ == "__main__":
    codeforces_client = CodeforcesAPI()
    # all_problems_path = os.path.abspath('data/all_problems.json')
    # print(f"All problems path: {all_problems_path}")
    problems = read_file('data/all_problems.json', file_extension='json')
    problems = filter_problem_by_rating(problems, 800, 1000)
    problems = problems[:800]
    print(f"Total problems to process: {len(problems)}")
    num_threads = min(1, len(problems))
    headers_list = codeforces_client.get_headers_list()
    cookies_list = codeforces_client.get_cookies_list()
    csrf_token_list = codeforces_client.get_csrf_token_list()
    headers_list = scale_fit_threads(headers_list, num_threads)
    cookies_list = scale_fit_threads(cookies_list, num_threads)
    csrf_token_list = scale_fit_threads(csrf_token_list, num_threads)
    run_with_retries(num_threads, problems, headers_list, cookies_list, csrf_token_list)



