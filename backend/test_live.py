import requests, time

files = {'file': open('C:/Users/srini/Downloads/multi_agent_dataset_testing.csv', 'rb')}
res = requests.post('http://localhost:8000/api/datasets/upload/', files=files)
print('Upload status:', res.status_code)

for i in range(12):
    time.sleep(3)
    s = requests.get('http://localhost:8000/api/dashboard/stats/').json()
    ds_status = s.get('active_dataset_status')
    logs = s.get('active_logs', [])
    agents = [l['agent'] + ':' + l['status'] for l in logs]
    print(f"[{i*3}s] dataset_status={ds_status} logs={agents}")
    if ds_status == 'completed' and i > 2:
        print("Done!")
        break
